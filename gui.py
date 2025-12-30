import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import time
from datetime import datetime

from templates import TemplatesManager
import registry

APP_TITLE = "py-new-file"

# small tooltip helper
class ToolTip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self._win: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hide()

    def _schedule(self):
        self._unschedule()
        self._id = self.widget.after(self.delay, self._show)

    def _unschedule(self):
        if self._id:
            try:
                self.widget.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _show(self):
        if self._win or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self._win = tk.Toplevel(self.widget)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry(f"+{x}+{y}")
        lbl = ttk.Label(self._win, text=self.text, relief="solid", padding=(6,4), background="#ffffe0")
        lbl.pack()
        # hide if focus changes
        self.widget.after(30000, self._hide)

    def _hide(self):
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win = None

class PythonNewGUI(tk.Tk):
    def __init__(self, target_dir: str):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x600")
        self.minsize(700, 420)
        self.target_dir = Path(target_dir).expanduser().resolve()

        # theme & vim state
        self._dark_theme = False
        self._vim_mode = False        # whether vim emulation is enabled
        self._vim_insert = True       # if vim enabled, whether we're in insert mode (True) or normal mode (False)
        self._vim_seq = ""            # simple sequence buffer for multi-key commands (dd, yy)
        self._vim_yank = ""           # store yanked text

        self._setup_style()
        self._create_widgets()
        self._bind_shortcuts()
        self.templates_dir = Path(__file__).with_name("templates")
        self.tm = TemplatesManager(self.templates_dir)
        self._load_templates_async()
        # restore last template selection from registry if present
        last = registry.get("last_template")
        if last:
            self._select_template_by_name(last)

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        default_font = ("Segoe UI", 10)
        self.option_add("*Font", default_font)
        style.configure("TButton", padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", foreground="#666666")
        # provide quick dark defaults (colors applied in _apply_theme)
        self._apply_theme()

    def _apply_theme(self):
        if self._dark_theme:
            bg = "#1e1f26"
            pane_bg = "#25262b"
            text_bg = "#111218"
            text_fg = "#d7d7d7"
            line_bg = "#2b2d33"
            select_bg = "#264f7a"
            insert_color = "#ffffff"
        else:
            bg = None
            pane_bg = None
            text_bg = "#f8f8f8"
            text_fg = "#111111"
            line_bg = "#eeeef0"
            select_bg = "#a8c6ff"
            insert_color = "#000000"

        # window/pane background
        if bg:
            self.configure(background=bg)
        # update preview widget colors if created
        try:
            self.preview.config(background=text_bg, foreground=text_fg, insertbackground=insert_color,
                                selectbackground=select_bg)
            # tag for current line highlight (reconfigure on theme switch)
            self.preview.tag_configure("current_line", background=line_bg)
        except Exception:
            pass

    def _create_widgets(self):
        # Main layout: left list, right preview+vars, bottom status/actions
        main = ttk.Frame(self, padding=(10,10,10,8))
        main.pack(fill="both", expand=True)

        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Left: templates list + CRUD buttons + Save
        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsw", padx=(0,8))
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Templates", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.tpl_list = tk.Listbox(left, width=28, activestyle="none", exportselection=False)
        self.tpl_list.grid(row=1, column=0, sticky="nsew", pady=(6,6))
        self.tpl_list.bind("<<ListboxSelect>>", lambda e: self._on_template_select())

        btns = ttk.Frame(left)
        btns.grid(row=2, column=0, sticky="ew", pady=(6,0))
        ttk.Button(btns, text="New", command=self._new_template).pack(side="left", padx=(0,6))
        ttk.Button(btns, text="Rename", command=self._rename_template).pack(side="left", padx=(0,6))
        ttk.Button(btns, text="Delete", command=self._delete_template).pack(side="left", padx=(6,6))
        # Save grouped with template actions
        self.save_btn = ttk.Button(btns, text="Save", command=self._save_template)
        self.save_btn.pack(side="left")
        self.save_btn.config(state="disabled")
        ToolTip(self.save_btn, "Save edits made to the template (Ctrl+S). Template metadata (variable keys) will be updated.")

        # Right: preview and variables
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        header = ttk.Frame(right)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.tpl_label = ttk.Label(header, text="No template selected", style="Header.TLabel")
        self.tpl_label.grid(row=0, column=0, sticky="w")

        # help button to explain template variables and show an example
        self.help_btn = ttk.Button(header, text="?", width=3, command=self._show_helper_dialog)
        self.help_btn.grid(row=0, column=1, sticky="e", padx=(6,0))
        self.help_btn.config(state="disabled")
        ToolTip(self.help_btn, "Explain template variables and show an example (Ctrl+H).")

        # Vim toggle button
        self.vim_btn = ttk.Button(header, text="Vim: Off", width=8, command=self._toggle_vim_mode)
        self.vim_btn.grid(row=0, column=2, sticky="e", padx=(6,0))
        ToolTip(self.vim_btn, "Toggle minimal Vim emulation (Normal/Insert modes).")

        # Theme toggle
        self.theme_btn = ttk.Button(header, text="Dark", width=6, command=self._toggle_theme)
        self.theme_btn.grid(row=0, column=3, sticky="e", padx=(6,0))
        ToolTip(self.theme_btn, "Toggle dark theme (Ctrl+T).")

        # Render and Create file (create is primary action)
        self.render_btn = ttk.Button(header, text="Render ▶", command=self._render_preview)
        self.render_btn.grid(row=0, column=4, sticky="e", padx=(6,0))
        self.render_btn.config(state="disabled")
        ToolTip(self.render_btn, "Render substitutes variables into the template preview. Placeholders use ${key} syntax (string.Template.safe_substitute).")
        self.create_btn = ttk.Button(header, text="Create file", command=self._create_file)
        self.create_btn.grid(row=0, column=5, sticky="e", padx=(6,0))
        self.create_btn.config(state="disabled")
        ToolTip(self.create_btn, "Writes the rendered preview to the target folder. You will be prompted for filename and overwrite confirmation.")

        self.preview = ScrolledText(right, wrap="none", height=18, font=("Consolas", 11))
        self.preview.grid(row=1, column=0, sticky="nsew", pady=(6,6))
        ToolTip(self.preview, "Preview area. Edit here and Save to update the template content.")
        # apply initial theme colors to preview
        self._apply_theme()
        # text tag for highlighting current line
        self.preview.tag_configure("current_line", background="#eeeef0")

        # bind tab/dedent and vim handling
        self.preview.bind("<Tab>", self._on_tab)
        self.preview.bind("<Shift-Tab>", self._on_shift_tab)
        self.preview.bind("<Key>", self._on_keypress, add="+")
        self.preview.bind("<KeyRelease>", lambda e: self._highlight_current_line(), add="+")
        self.preview.bind("<ButtonRelease-1>", lambda e: self._highlight_current_line(), add="+")
        self.preview.bind("<FocusIn>", lambda e: self._highlight_current_line(), add="+")
        # make sure mouse wheel and arrow keys still work

        vars_frame = ttk.LabelFrame(right, text="Template variables")
        vars_frame.grid(row=2, column=0, sticky="ew")
        vars_frame.columnconfigure(1, weight=1)
        ToolTip(vars_frame, "Define key/value pairs used to replace ${key} placeholders in templates. Missing keys are left unchanged when rendering.")

        ttk.Label(vars_frame, text="key").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Label(vars_frame, text="value").grid(row=0, column=1, padx=6, pady=6, sticky="w")

        self.vars_entries: Dict[str, ttk.Entry] = {}
        self.vars_container = ttk.Frame(vars_frame)
        self.vars_container.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(0,8))
        self._vars_row = 0

        vars_actions = ttk.Frame(right)
        vars_actions.grid(row=3, column=0, sticky="ew", pady=(6,0))
        self.add_var_btn = ttk.Button(vars_actions, text="Add var", command=self._add_var_row)
        self.add_var_btn.pack(side="left")
        ToolTip(self.add_var_btn, "Add an empty variable row. Enter a variable name (key) and its value to be used for substitution.")
        self.clear_vars_btn = ttk.Button(vars_actions, text="Clear vars", command=self._clear_vars)
        self.clear_vars_btn.pack(side="left", padx=(6,0))
        ToolTip(self.clear_vars_btn, "Remove all variable rows.")
        # Auto-fill populates vars with sane sample values (from metadata if available)
        self.autofill_btn = ttk.Button(vars_actions, text="Auto-fill", command=self._auto_fill_vars)
        self.autofill_btn.pack(side="left", padx=(6,0))
        self.autofill_btn.config(state="disabled")
        ToolTip(self.autofill_btn, "Auto-fill variable values with sensible defaults (useful for demo and templates with known keys).")

        # Bottom action bar
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0,10))
        self.status = ttk.Label(bar, text=f"Target: {self.target_dir}", style="Status.TLabel")
        self.status.pack(side="left")
        ttk.Button(bar, text="Choose target...", command=self._choose_target).pack(side="right", padx=(6,0))
        # mode indicator (insert/normal for vim)
        self.mode_label = ttk.Label(bar, text="Mode: Insert", width=16, anchor="e", style="Status.TLabel")
        self.mode_label.pack(side="right")

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self._new_template())
        self.bind("<Control-s>", lambda e: self._save_template())
        self.bind("<Control-r>", lambda e: self._render_preview())
        self.bind("<Control-o>", lambda e: self._create_file())
        self.bind("<Control-h>", lambda e: self._show_helper_dialog())
        self.bind("<Control-t>", lambda e: self._toggle_theme())
        self.bind("<Delete>", lambda e: self._delete_template())

    def _load_templates_async(self):
        threading.Thread(target=self._load_templates, daemon=True).start()

    def _load_templates(self):
        names = self.tm.list_templates()
        self.after(0, lambda: self._populate_list(names))

    def _populate_list(self, names):
        self.tpl_list.delete(0, "end")
        for n in names:
            self.tpl_list.insert("end", n)
        # ensure buttons reflect selection state
        self._update_button_states()

    def _on_template_select(self):
        sel = self.tpl_list.curselection()
        if not sel:
            self._update_button_states()
            return
        name = self.tpl_list.get(sel[0])
        registry.set("last_template", name)
        self._show_template(name)
        self._update_button_states()

    def _update_button_states(self):
        has_selection = bool(self.tpl_list.curselection())
        state = "normal" if has_selection else "disabled"
        self.save_btn.config(state=state)
        self.render_btn.config(state=state)
        self.create_btn.config(state=state)
        self.autofill_btn.config(state=state)
        self.help_btn.config(state=state)

    def _select_template_by_name(self, name: str):
        try:
            idx = list(self.tpl_list.get(0, "end")).index(name)
            self.tpl_list.selection_clear(0, "end")
            self.tpl_list.selection_set(idx)
            self.tpl_list.see(idx)
            self._show_template(name)
            self._update_button_states()
        except ValueError:
            pass

    def _show_template(self, name: str):
        content, meta = self.tm.load_template(name, with_meta=True)
        self.tpl_label.config(text=name)
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", content)
        # show vars according to metadata
        self._clear_vars()
        vars_list = meta.get("vars") or []
        for k in vars_list:
            self._add_var_row(k, "")
        # always show a blank var row
        self._add_var_row()
        # ensure highlighting is updated
        self._highlight_current_line()

    def _render_preview(self):
        name = self._current_template_name()
        if not name:
            messagebox.showinfo(APP_TITLE, "Select a template first.")
            return
        # collect vars
        vars_dict = self._collect_vars()
        out = self.tm.render_template(name, vars_dict)
        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", out)
        self._highlight_current_line()

    def _collect_vars(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for key_entry, val_entry in self.vars_entries.values():
            key = key_entry.get().strip()
            if not key:
                continue
            out[key] = val_entry.get()
        return out

    def _add_var_row(self, key: str = "", value: str = ""):
        row = self._vars_row
        key_e = ttk.Entry(self.vars_container, width=20)
        val_e = ttk.Entry(self.vars_container)
        key_e.grid(row=row, column=0, sticky="ew", padx=(0,6), pady=2)
        val_e.grid(row=row, column=1, sticky="ew", pady=2)
        key_e.insert(0, key)
        val_e.insert(0, value)
        self.vars_entries[row] = (key_e, val_e)
        # tooltip on inputs: name explains syntax and that it's referenced as ${key}
        ToolTip(key_e, "Variable name. Use this name in templates as ${name}.")
        ToolTip(val_e, "Value used to replace the corresponding ${name} when rendering.")
        self._vars_row += 1

    def _clear_vars(self):
        for widgets in self.vars_entries.values():
            for w in widgets:
                w.destroy()
        self.vars_entries.clear()
        self._vars_row = 0

    # Tab handling -> insert 4 spaces, Shift-Tab dedent
    def _on_tab(self, event):
        # If vim enabled and in normal mode, swallow tab
        if self._vim_mode and not self._vim_insert:
            return "break"
        self.preview.insert("insert", " " * 4)
        return "break"

    def _on_shift_tab(self, event):
        # remove up to 4 leading spaces from current line at cursor
        idx = self.preview.index("insert")
        line_start = self.preview.index(f"{idx.split('.')[0]}.0")
        line = self.preview.get(line_start, f"{line_start} lineend")
        # compute how many spaces to remove before cursor
        remove = 0
        for c in line[: int(idx.split('.')[1])]:
            if c == " " and remove < 4:
                remove += 1
            else:
                break
        if remove:
            self.preview.delete(f"{line_start}+0c", f"{line_start}+{remove}c")
        return "break"

    # Highlight current line
    def _highlight_current_line(self):
        try:
            self.preview.tag_remove("current_line", "1.0", "end")
            line = self.preview.index("insert").split(".")[0]
            self.preview.tag_add("current_line", f"{line}.0", f"{line}.end")
        except Exception:
            pass

    # Vim imitation: minimal commands in normal mode (h/j/k/l, i to insert, x to delete char,
    # dd to delete line, yy to yank line, p to paste)
    def _on_keypress(self, event):
        # always update highlight on key events
        self.after_idle(self._highlight_current_line)

        if not self._vim_mode:
            # normal editing behavior
            return

        # When vim mode is enabled, intercept keys depending on insert/normal mode
        # If in insert mode, only Escape switches to Normal
        if self._vim_insert:
            if event.keysym == "Escape":
                self._vim_insert = False
                self._vim_seq = ""
                self._update_mode_label()
                return "break"
            # allow normal insertion in insert mode
            return

        # Normal mode: swallow most keys and interpret commands
        ks = event.keysym
        ch = event.char or ""
        handled = True

        if ks in ("Left",) or ch == "h":
            self._move_cursor("left")
        elif ks in ("Right",) or ch == "l":
            self._move_cursor("right")
        elif ks in ("Up",) or ch == "k":
            self._move_cursor("up")
        elif ks in ("Down",) or ch == "j":
            self._move_cursor("down")
        elif ch == "i":
            self._vim_insert = True
            self._update_mode_label()
        elif ch == "x":
            # delete character under cursor
            pos = self.preview.index("insert")
            self.preview.delete(pos)
        elif ch == "d":
            if self._vim_seq == "d":
                # dd => delete current line
                line = self.preview.index("insert").split(".")[0]
                self.preview.delete(f"{line}.0", f"{line}.end+1c")
                self._vim_seq = ""
            else:
                self._vim_seq = "d"
                # clear after short timeout
                self.after(700, lambda: setattr(self, "_vim_seq", "") )
        elif ch == "y":
            if self._vim_seq == "y":
                # yy => yank (copy) line
                line = self.preview.index("insert").split(".")[0]
                self._vim_yank = self.preview.get(f"{line}.0", f"{line}.end+1c")
                self._vim_seq = ""
            else:
                self._vim_seq = "y"
                self.after(700, lambda: setattr(self, "_vim_seq", "") )
        elif ch == "p":
            if self._vim_yank:
                # paste after current line (simple behavior)
                line = self.preview.index("insert").split(".")[0]
                self.preview.insert(f"{line}.end+1c", self._vim_yank)
        elif ks == "Escape":
            # already normal
            pass
        else:
            handled = False  # let other keys pass through (e.g., shortcuts)
        # ensure mode label reflects state
        self._update_mode_label()
        return "break" if handled else None

    def _move_cursor(self, direction: str):
        try:
            if direction == "left":
                self.preview.mark_set("insert", "insert -1c")
            elif direction == "right":
                self.preview.mark_set("insert", "insert +1c")
            elif direction == "up":
                self.preview.mark_set("insert", "insert -1l")
            elif direction == "down":
                self.preview.mark_set("insert", "insert +1l")
            self.preview.see("insert")
        except Exception:
            pass

    def _toggle_vim_mode(self):
        self._vim_mode = not self._vim_mode
        if self._vim_mode:
            # enter Vim; start in Normal mode
            self._vim_insert = False
            self.vim_btn.config(text="Vim: On")
        else:
            self._vim_insert = True
            self.vim_btn.config(text="Vim: Off")
            self._vim_seq = ""
        self._update_mode_label()
        self.preview.focus_set()

    def _update_mode_label(self):
        if not self._vim_mode:
            self.mode_label.config(text="Mode: Insert")
        else:
            self.mode_label.config(text="Mode: Insert" if self._vim_insert else "Mode: Normal")

    def _toggle_theme(self):
        self._dark_theme = not self._dark_theme
        self.theme_btn.config(text="Dark" if not self._dark_theme else "Light")
        self._apply_theme()
        self._highlight_current_line()

    def _auto_fill_vars(self):
        """Populate variable rows with sensible sample values (from metadata vars or simple heuristics)."""
        name = self._current_template_name()
        if not name:
            return
        meta = self.tm.get_metadata(name) or {}
        vars_list = meta.get("vars") or []
        # simple heuristics for sample values
        samples = {}
        for k in vars_list:
            kl = k.lower()
            if "name" in kl:
                samples[k] = self.target_dir.name or "MyProject"
            elif "author" in kl:
                samples[k] = registry.get("author", "Your Name")
            elif "license" in kl:
                samples[k] = "MIT"
            elif "date" in kl or "created" in kl:
                samples[k] = datetime.utcnow().date().isoformat()
            elif "description" in kl:
                samples[k] = meta.get("description") or "A demo project"
            else:
                samples[k] = f"<{k}>"
        # reset and fill rows
        self._clear_vars()
        for k, v in samples.items():
            self._add_var_row(k, v)
        # add an empty row for convenience
        self._add_var_row()
        messagebox.showinfo(APP_TITLE, f"Auto-filled {len(samples)} variable(s) for {name}.")

    def _show_helper_dialog(self):
        """Show help about template variables and an example render for the selected template."""
        name = self._current_template_name()
        text = (
            "Template variables help\n\n"
            "Use ${key} placeholders in templates (string.Template syntax). "
            "Enter variable key/value pairs below and click 'Render' to substitute them. "
            "Missing keys are left unchanged by safe_substitute.\n\n"
            "Keyboard: Ctrl+R to render, Ctrl+S to save, Ctrl+O to create file, Ctrl+H for this help.\n"
            "Vim: Toggle with 'Vim' button. In Normal mode use h/j/k/l, i to insert, x to delete char, dd to delete line, yy to yank, p to paste.\n"
        )
        if name:
            meta = self.tm.get_metadata(name) or {}
            vars_list = meta.get("vars") or []
            if vars_list:
                text += "\nDetected variable keys: " + ", ".join(vars_list) + "\n"
            # show a sample render using auto-filled values (don't modify user entries)
            samples = {}
            for k in vars_list:
                if "name" in k.lower():
                    samples[k] = self.target_dir.name or "MyProject"
                elif "author" in k.lower():
                    samples[k] = registry.get("author", "Your Name")
                elif "license" in k.lower():
                    samples[k] = "MIT"
                elif "date" in k.lower() or "created" in k.lower():
                    samples[k] = datetime.utcnow().date().isoformat()
                else:
                    samples[k] = f"<{k}>"
            rendered = self.tm.render_template(name, samples)
            text += "\n--- Example render ---\n\n" + rendered
        messagebox.showinfo(f"{APP_TITLE} — Template variables", text)

    def _current_template_name(self) -> Optional[str]:
        sel = self.tpl_list.curselection()
        if not sel:
            return None
        return self.tpl_list.get(sel[0])

    def _new_template(self):
        name = simpledialog.askstring(APP_TITLE, "New template name (with or without .py):")
        if not name:
            return
        name = self.tm._sanitize_name(name)
        if name in self.tm.list_templates():
            messagebox.showwarning(APP_TITLE, "A template with that name already exists.")
            return
        starter = "# new template\n"
        try:
            self.tm.create_template(name, starter, {"description": "", "vars": []})
            self._load_templates()
            self._select_template_by_name(name)
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Cannot create template:\n{e}")

    def _rename_template(self):
        name = self._current_template_name()
        if not name:
            return
        new = simpledialog.askstring(APP_TITLE, "New name for template:", initialvalue=name)
        if not new or new == name:
            return
        try:
            self.tm.rename_template(name, new)
            self._load_templates()
            self._select_template_by_name(new)
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Rename failed:\n{e}")

    def _delete_template(self):
        name = self._current_template_name()
        if not name:
            return
        if not messagebox.askyesno(APP_TITLE, f"Delete template '{name}'?"):
            return
        try:
            self.tm.delete_template(name)
            self._load_templates()
            self.preview.delete("1.0", "end")
            self.tpl_label.config(text="No template selected")
            self._update_button_states()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Delete failed:\n{e}")

    def _save_template(self):
        name = self._current_template_name()
        if not name:
            messagebox.showinfo(APP_TITLE, "Select a template to save.")
            return
        content = self.preview.get("1.0", "end").rstrip("\n")
        # collect var keys for metadata
        vars_keys = [k.get().strip() for k, v in self.vars_entries.values() if k.get().strip()]
        meta = {"vars": vars_keys}
        try:
            self.tm.save_template(name, content, metadata=meta, overwrite=True)
            messagebox.showinfo(APP_TITLE, "Template saved.")
            self._load_templates()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Save failed:\n{e}")

    def _choose_target(self):
        chosen = filedialog.askdirectory(initialdir=str(self.target_dir))
        if chosen:
            self.target_dir = Path(chosen)
            self.status.config(text=f"Target: {self.target_dir}")
            registry.update_registry({"last_target": str(self.target_dir)})

    def _create_file(self):
        name = self._current_template_name()
        if not name:
            messagebox.showinfo(APP_TITLE, "Select a template first.")
            return
        content = self.preview.get("1.0", "end")
        default_name = name.replace(".py", "") + ".py"
        fname = simpledialog.askstring(APP_TITLE, "Filename to create (in target):", initialvalue=default_name)
        if not fname:
            return
        dest = self.target_dir / fname
        if dest.exists() and not messagebox.askyesno(APP_TITLE, "File exists. Overwrite?"):
            return
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            messagebox.showinfo(APP_TITLE, f"Created {dest}")
            registry.update_registry({"last_created": str(dest)})
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Cannot create file:\n{e}")

    def render_template(self, name: str, vars: Optional[Dict[str, Any]] = None) -> str:
        # Delegate rendering (including nested substitutions) to TemplatesManager
        return self.tm.render_template(name, vars)

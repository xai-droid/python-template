$readme = Join-Path $PSScriptRoot "README.md"

if (-Not (Test-Path $readme)) {
    Write-Host "README.md nicht gefunden!"
    Read-Host "Enter zum Beenden"
    exit
}

# Variablen für Abschnitt
$buffer = @()
$firstTitle = $true

Get-Content $readme -Encoding UTF8 | ForEach-Object {
    $line = $_

    # Prüfen, ob es ein Markdown-Titel ist
    if ($line -match '^#') {
        if (-not $firstTitle) {
            # Ausgabe der gesammelten Seite
            $buffer | ForEach-Object { Write-Host $_ }
            Read-Host "Druecken Sie Enter fuer naechste Seite"
            Clear-Host
            $buffer = @()
        }
        $firstTitle = $false
    }

    # Linie zum aktuellen Abschnitt hinzufügen
    $buffer += $line
}

# Letzte Seite ausgeben
if ($buffer.Count -gt 0) {
    $buffer | ForEach-Object { Write-Host $_ }
}

Write-Host "--- Ende der README ---"
Read-Host "Druecken Sie Enter zum Beenden"



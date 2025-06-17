Set-Location -Path $PSScriptRoot
if (-not (Test-Path -Path ".venv" -PathType Container)) {
    python -m venv .venv
    & ".\.venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
} else {
    & ".\.venv\Scripts\Activate.ps1"
}
python main.py
Write-Host "Done! Check the directory 'output'" -ForegroundColor Cyan

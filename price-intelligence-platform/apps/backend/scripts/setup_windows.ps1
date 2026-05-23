$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

Write-Host "Checking Python version..."
$version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($version -eq "3.14") {
  Write-Host "Python 3.14 is not supported by the pinned NumPy/scikit-learn stack yet."
  Write-Host "Install Python 3.12 or create a conda env with Python 3.11/3.12, then rerun this script."
  exit 1
}

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

Write-Host "Backend dependencies installed."
Write-Host "Next:"
Write-Host "  python -m alembic upgrade head"
Write-Host "  python -m uvicorn app.main:app --reload"

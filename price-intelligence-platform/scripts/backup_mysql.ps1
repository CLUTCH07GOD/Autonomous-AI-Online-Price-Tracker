$ErrorActionPreference = "Stop"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$root = Resolve-Path "$PSScriptRoot\.."
$backupDir = Join-Path $root "db\backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

mysqldump -uroot -ppass123 price_intelligence | Out-File -Encoding utf8 (Join-Path $backupDir "price_intelligence_$timestamp.sql")
Write-Host "Backup written to $backupDir"

# Automatski backup baze
$date = Get-Date -Format 'yyyy-MM-dd_HH-mm'
$backupDir = "D:\Projekti\ServisMasterOS\backups"

# Napravi folder ako ne postoji
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force
}

# SQL dump
docker exec -t servismaster-postgres pg_dump -U postgres -d servismaster_db > "$backupDir\servismaster_$date.sql"

# Obriši backup-e starije od 30 dana
Get-ChildItem "$backupDir\servismaster_*.sql" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item

Write-Host "Backup završen: $backupDir\servismaster_$date.sql"
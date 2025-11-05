# Run this script as Administrator
# Right-click this file and select "Run with PowerShell"

Write-Host "Restarting PostgreSQL service..." -ForegroundColor Cyan
Restart-Service postgresql-x64-15
Write-Host "PostgreSQL restarted successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

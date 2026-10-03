# Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running." -ForegroundColor Red
    Write-Host "Please open 'Docker Desktop' from your Start Menu and wait for it to start."
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

Write-Host "Stopping any existing containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "Building and starting application... (This may take a few minutes)" -ForegroundColor Cyan
docker-compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n---------------------------------------------------" -ForegroundColor Green
    Write-Host "SUCCESS! Your application is now running." -ForegroundColor Green
    Write-Host "---------------------------------------------------"
    Write-Host "1. Frontend (The App):   http://localhost"
    Write-Host "2. Backend (The API):    http://localhost:8000"
    Write-Host "3. API Docs:             http://localhost:8000/docs"
    Write-Host "---------------------------------------------------"
    Write-Host "To stop the app, run: docker-compose down"
} else {
    Write-Host "`nError: Something went wrong." -ForegroundColor Red
}

Read-Host -Prompt "Press Enter to exit"

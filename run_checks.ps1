Write-Host ">>> Running Automated Pytest Suite..." -ForegroundColor Cyan
uv run pytest -v
if ($LASTEXITCODE -ne 0) { Write-Host "Tests failed!" -ForegroundColor Red; exit 1 }

Write-Host "
>>> Running Ruff Lint Checks..." -ForegroundColor Cyan
uv run ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "Lint checks failed!" -ForegroundColor Red; exit 1 }

Write-Host "
>>> Checking Code Formatting..." -ForegroundColor Cyan
uv run ruff format --check .
if ($LASTEXITCODE -ne 0) { Write-Host "Formatting check failed!" -ForegroundColor Red; exit 1 }

Write-Host "
All enterprise quality checks passed successfully!" -ForegroundColor Green
$ErrorActionPreference = "Stop"

Write-Host ">>> Running Automated Pytest Suite (Unit + API)..." -ForegroundColor Cyan
uv run pytest -v

Write-Host ">>> Running Ruff Lint Checks..." -ForegroundColor Cyan
uv run ruff check .

Write-Host ">>> Checking Code Formatting..." -ForegroundColor Cyan
uv run ruff format --check .

Write-Host "All enterprise quality checks passed successfully!" -ForegroundColor Green
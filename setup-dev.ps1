# setup-dev.ps1 — Helper to setup and run the project for local development (Windows PowerShell)
# Usage: Open PowerShell in repo root and run: .\setup-dev.ps1

# 1) Create virtualenv if missing
if (-not (Test-Path -Path .\.venv)) {
    Write-Host "Creating virtual environment .venv..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists"
}

# 2) Activate virtualenv
Write-Host "Activating virtualenv..."
. .\.venv\Scripts\Activate.ps1

# 3) Upgrade pip and install dev requirements
python -m pip install --upgrade pip
if (Test-Path requirements-dev.txt) {
    pip install -r requirements-dev.txt
} else {
    Write-Host "requirements-dev.txt not found — please create it or install dependencies manually."
}

# 4) Ensure .env has SQLite configured for dev
if (Test-Path .env) {
    $envContent = Get-Content .env
    if ($envContent -notmatch '^DATABASE_ENGINE=') {
        Add-Content .env "DATABASE_ENGINE=sqlite"
        Write-Host "Added DATABASE_ENGINE=sqlite to .env"
    } else {
        $envContent -replace '^DATABASE_ENGINE=.*','DATABASE_ENGINE=sqlite' | Set-Content .env
        Write-Host "Set DATABASE_ENGINE=sqlite in .env"
    }
} else {
    Write-Host "Creating .env with DATABASE_ENGINE=sqlite"
    "DATABASE_ENGINE=sqlite" | Out-File .env -Encoding utf8
}

# 5) Run migrations
Write-Host "Running migrations..."
python manage.py migrate

# 6) Create static folder and a .gitkeep if missing
if (-not (Test-Path .\static)) {
    New-Item -ItemType Directory -Path .\static | Out-Null
    "" | Out-File .\static\.gitkeep -Encoding utf8
    Write-Host "Created ./static and .gitkeep"
} else {
    Write-Host "./static already exists"
}

# 7) Collect static files
Write-Host "Collecting static files..."
python manage.py collectstatic --noinput

# 8) Run migrations first
Write-Host "Running migrations..."
python manage.py migrate

Write-Host "Setup complete!"
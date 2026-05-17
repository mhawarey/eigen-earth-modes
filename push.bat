@echo off
cd /d "%~dp0"

IF NOT EXIST ".git" (
    git init
    git branch -M main
)

git add .
git commit -m "Initial release: Interactive visualizer of Earth's free oscillations (normal modes) — both **spheroidal** (`nSl`) and **toroidal** (`nTl`)."

git remote get-url origin >nul 2>&1
IF ERRORLEVEL 1 (
    gh repo create mhawarey/eigen-earth-modes --public --source=. --remote=origin --push
) ELSE (
    git push -u origin main
)

echo [DONE] https://github.com/mhawarey/eigen-earth-modes
pause

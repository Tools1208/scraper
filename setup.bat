@echo off
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Creating output directory...
if not exist output mkdir output

echo Setup complete! Usage:
echo python scraper.py [URL] --format [json/csv] --delay [MIN MAX]

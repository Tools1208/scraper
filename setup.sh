#!/bin/bash
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Creating output directory..."
mkdir -p output

echo "Setup complete! Usage:"
echo "python3 scraper.py [URL] --format [json/csv] --delay [MIN MAX]"

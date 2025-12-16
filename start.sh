#!/bin/bash

# Finanz-Copilot WebAPI Startskript

set -e

cd "$(dirname "$0")"

# Virtuelle Umgebung erstellen falls nicht vorhanden
if [ ! -d ".venv" ]; then
    echo "🔧 Erstelle virtuelle Umgebung..."
    python3 -m venv .venv
fi

# Aktivieren
source .venv/bin/activate

# Dependencies installieren
echo "📦 Installiere Dependencies..."
pip install -q -r requirements.txt

# Server starten
echo "🚀 Starte FastAPI Server..."
python main.py

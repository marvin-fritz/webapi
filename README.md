# Finanz-Copilot API

Eine REST-API für Finanzanalysen, gebaut mit FastAPI und MongoDB.

## Features

- 📈 **Insider Trading Sentiment-Analyse** - Berechnung von Sentiment-Indikatoren basierend auf Insider-Trades
- 📰 **News Aggregation** - Verwaltung von News-Quellen und Artikeln
- 💼 **SEC Financials** - Zugriff auf SEC-Finanzdaten
- 📊 **Stock Index** - Aktien-Stammdaten und Suche

## Projektstruktur

```
webapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI App Factory
│   ├── config.py            # Settings (pydantic-settings)
│   ├── dependencies.py      # Shared Dependencies
│   ├── exceptions.py        # Custom Exceptions & Handler
│   ├── api/
│   │   └── v1/
│   │       ├── router.py    # API Version Router
│   │       └── endpoints/   # Feature-basierte Endpunkte
│   │           ├── health.py
│   │           ├── insider_trades.py
│   │           ├── news.py
│   │           ├── news_sources.py
│   │           ├── sec_financials.py
│   │           ├── sentiment.py
│   │           └── stocks.py
│   ├── schemas/             # Pydantic Request/Response Models
│   ├── models/              # Beanie/MongoDB Document Models
│   ├── services/            # Business Logic Layer
│   └── core/                # Database, Security, Utils
├── tests/                   # Pytest Tests
├── .env                     # Environment Variables
├── requirements.txt         # Dependencies
├── main.py                  # Entry Point
├── start.sh                 # Startskript
└── README.md
```

## Schnellstart

```bash
# Mit Startskript (empfohlen)
./start.sh

# Oder manuell:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## API Endpoints

### Health

| Methode | Endpoint         | Beschreibung |
| ------- | ---------------- | ------------ |
| GET     | `/api/v1/health` | Health Check |

### Sentiment Analysis

| Methode | Endpoint                           | Beschreibung                                |
| ------- | ---------------------------------- | ------------------------------------------- |
| GET     | `/api/v1/sentiment`                | Vollständige Sentiment-Analyse mit Historie |
| GET     | `/api/v1/sentiment/current`        | Aktuelle Sentiment-Werte                    |
| GET     | `/api/v1/sentiment/market-breadth` | Marktbreite-Analyse                         |
| GET     | `/api/v1/sentiment/top-movers`     | Top-Mover ISINs                             |
| GET     | `/api/v1/sentiment/trends`         | Trend-Analyse mit Momentum                  |

### Insider Trades

| Methode | Endpoint                      | Beschreibung                    |
| ------- | ----------------------------- | ------------------------------- |
| GET     | `/api/v1/insider-trades`      | Alle Insider-Trades (paginiert) |
| GET     | `/api/v1/insider-trades/{id}` | Einzelner Trade                 |
| POST    | `/api/v1/insider-trades`      | Neuen Trade erstellen           |

### Stocks

| Methode | Endpoint                            | Beschreibung                       |
| ------- | ----------------------------------- | ---------------------------------- |
| GET     | `/api/v1/stocks`                    | Alle Aktien (paginiert, filterbar) |
| GET     | `/api/v1/stocks/search?q=`          | Aktien-Suche                       |
| GET     | `/api/v1/stocks/by-isin/{isin}`     | Aktie nach ISIN                    |
| GET     | `/api/v1/stocks/by-ticker/{ticker}` | Aktien nach Ticker                 |

### News

| Methode | Endpoint               | Beschreibung      |
| ------- | ---------------------- | ----------------- |
| GET     | `/api/v1/news`         | Alle News         |
| GET     | `/api/v1/news-sources` | Alle News-Quellen |

### SEC Financials

| Methode | Endpoint                 | Beschreibung    |
| ------- | ------------------------ | --------------- |
| GET     | `/api/v1/sec-financials` | SEC Finanzdaten |

## API Dokumentation

Nach dem Start verfügbar unter:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Umgebungsvariablen

Erstelle eine `.env` Datei im Root-Verzeichnis:

```env
# App
APP_NAME=Finanz-Copilot API
DEBUG=true
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=financecentre
```

## Tests

```bash
pytest
```

## Entwicklung

### Neue Endpoints hinzufügen

1. Schema in `app/schemas/` erstellen
2. Model in `app/models/` erstellen (Beanie Document)
3. Service in `app/services/` erstellen
4. Endpoint in `app/api/v1/endpoints/` erstellen
5. Router in `app/api/v1/router.py` registrieren
6. Exports in `__init__.py` Dateien aktualisieren

## Tech Stack

- **Framework**: FastAPI
- **Datenbank**: MongoDB mit Beanie ODM
- **Validation**: Pydantic v2
- **Server**: Uvicorn
- **Testing**: Pytest + httpx

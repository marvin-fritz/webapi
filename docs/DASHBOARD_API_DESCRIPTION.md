# Dashboard Statistics API Dokumentation

Diese Dokumentation beschreibt die benötigte REST API für das Dashboard-Statistik-Modul der Startseite.

## Base URL

```
https://api.finanz-copilot.de/api/v1/dashboard
```

---

## Konzept

Die Dashboard-API liefert aggregierte Statistiken über Insider-Trading-Aktivitäten in einem konfigurierbaren Zeitraum. Sie dient als zentrale Datenquelle für das Startseiten-Dashboard und ermöglicht:

- **Echtzeit-Statistiken**: Neue Trades, Käufe/Verkäufe-Verhältnis
- **Aktivitäts-Monitoring**: Verarbeitete Aktien, stündliche Aktivität
- **Top-Performer**: Meistgehandelte Aktien nach Insider-Aktivität
- **Volumen-Analyse**: Handelsvolumen nach Währung

### Parameter

- **Zeitraum**: 1-336 Stunden (1 Stunde bis 2 Wochen)
- **Granularität**: Stündliche Auflösung für Zeitreihen
- **Auto-Refresh**: Empfohlen alle 60 Sekunden für Zeiträume ≤ 24h

---

## TypeScript Types

```typescript
// types/dashboard.types.ts

// === Time Range ===
export interface TimeRange {
  /** ISO-Datum Start */
  from: string;
  /** ISO-Datum Ende */
  to: string;
  /** Zeitzone (z.B. "Europe/Berlin") */
  timezone: string;
  /** Angefragter Zeitraum in Stunden */
  hours: number;
}

// === Processing Statistics ===
export interface ProcessedPerHour {
  /** ISO-Datum der Stunde */
  hour: string;
  /** Anzahl verarbeiteter Aktien in dieser Stunde */
  count: number;
  /** Anzahl neuer Trades in dieser Stunde */
  tradesCount: number;
}

export interface ProcessingStats {
  /** Anzahl eindeutiger Aktien mit Insider-Aktivität im Zeitraum */
  processedStocks: number;
  /** Gesamtanzahl aller Trades im Zeitraum */
  totalTrades: number;
  /** Stündliche Aufschlüsselung */
  processedPerHour: ProcessedPerHour[];
}

// === Insider Trades Statistics ===
export interface TradesByType {
  /** Anzahl Insider-Käufe */
  BUY: number;
  /** Anzahl Insider-Verkäufe */
  SELL: number;
}

export interface TopTicker {
  /** Ticker-Symbol oder ISIN */
  ticker: string;
  /** Firmenname (optional) */
  companyName?: string;
  /** Anzahl Trades */
  count: number;
  /** ISIN (optional) */
  isin?: string;
}

export interface VolumeByCurrency {
  /** Währungscode (EUR, USD, CHF, etc.) */
  currency: string;
  /** Gesamtvolumen in dieser Währung */
  totalVolume: number;
  /** Durchschnittliches Volumen pro Trade */
  avgVolume: number;
  /** Anzahl Trades in dieser Währung */
  count: number;
}

export interface InsiderTradesStats {
  /** Anzahl neuer Trades im Zeitraum */
  newTrades: number;
  /** Aufschlüsselung nach Transaktionstyp */
  byType: TradesByType;
  /** Top Aktien nach Trade-Anzahl (max 20) */
  topTickersByCount: TopTicker[];
  /** Volumen aggregiert nach Währung */
  volumeByCurrency: VolumeByCurrency[];
}

// === Main Response ===
export interface DashboardStatsResponse {
  /** Metadata über den Zeitraum */
  timeRange: TimeRange;
  /** Verarbeitungs-Statistiken */
  processing: ProcessingStats;
  /** Insider-Trading-Statistiken */
  insiderTrades: InsiderTradesStats;
}
```

---

## API Endpoint

### Dashboard-Statistiken abrufen

```
GET /api/v1/dashboard/stats
```

| Parameter  | Typ    | Required | Default         | Beschreibung                        |
| ---------- | ------ | -------- | --------------- | ----------------------------------- |
| `hours`    | int    | ❌       | 24              | Zeitraum in Stunden (1-336)         |
| `timezone` | string | ❌       | "Europe/Berlin" | Zeitzone für Zeitreihen-Aggregation |

**Anwendungsfall:** Dashboard-Startseite mit Echtzeit-Statistiken

#### Beispiel Request

```bash
# Letzte 24 Stunden
GET /api/v1/dashboard/stats?hours=24

# Letzte Woche
GET /api/v1/dashboard/stats?hours=168

# Letzte 6 Stunden mit UTC
GET /api/v1/dashboard/stats?hours=6&timezone=UTC
```

---

## Beispiel Response

### GET /api/v1/dashboard/stats?hours=24

```json
{
  "timeRange": {
    "from": "2025-12-15T14:30:00.000Z",
    "to": "2025-12-16T14:30:00.000Z",
    "timezone": "Europe/Berlin",
    "hours": 24
  },
  "processing": {
    "processedStocks": 127,
    "totalTrades": 342,
    "processedPerHour": [
      {
        "hour": "2025-12-15T15:00:00.000Z",
        "count": 8,
        "tradesCount": 15
      },
      {
        "hour": "2025-12-15T16:00:00.000Z",
        "count": 12,
        "tradesCount": 28
      },
      {
        "hour": "2025-12-15T17:00:00.000Z",
        "count": 5,
        "tradesCount": 11
      }
      // ... weitere Stunden
    ]
  },
  "insiderTrades": {
    "newTrades": 342,
    "byType": {
      "BUY": 198,
      "SELL": 144
    },
    "topTickersByCount": [
      {
        "ticker": "AAPL",
        "companyName": "Apple Inc.",
        "count": 18,
        "isin": "US0378331005"
      },
      {
        "ticker": "MSFT",
        "companyName": "Microsoft Corporation",
        "count": 15,
        "isin": "US5949181045"
      },
      {
        "ticker": "SAP",
        "companyName": "SAP SE",
        "count": 12,
        "isin": "DE0007164600"
      },
      {
        "ticker": "NVDA",
        "companyName": "NVIDIA Corporation",
        "count": 10,
        "isin": "US67066G1040"
      },
      {
        "ticker": "TSLA",
        "companyName": "Tesla, Inc.",
        "count": 9,
        "isin": "US88160R1014"
      }
      // ... bis zu 20 Einträge
    ],
    "volumeByCurrency": [
      {
        "currency": "USD",
        "totalVolume": 45672890.5,
        "avgVolume": 228364.45,
        "count": 200
      },
      {
        "currency": "EUR",
        "totalVolume": 12450000.0,
        "avgVolume": 155625.0,
        "count": 80
      },
      {
        "currency": "CHF",
        "totalVolume": 3250000.0,
        "avgVolume": 108333.33,
        "count": 30
      },
      {
        "currency": "GBP",
        "totalVolume": 1890000.0,
        "avgVolume": 94500.0,
        "count": 20
      }
    ]
  }
}
```

---

## Datenberechnungen

### Abgeleitete Metriken (Frontend)

Das Frontend berechnet folgende Werte aus den API-Daten:

| Metrik                 | Berechnung                                            |
| ---------------------- | ----------------------------------------------------- |
| **Buy-Percentage**     | `(byType.BUY / (byType.BUY + byType.SELL)) * 100`     |
| **Sell-Percentage**    | `(byType.SELL / (byType.BUY + byType.SELL)) * 100`    |
| **Ø Trades pro Aktie** | `processing.totalTrades / processing.processedStocks` |
| **Anteil pro Ticker**  | `ticker.count / insiderTrades.newTrades * 100`        |

### Aggregations-Regeln (Backend)

1. **processedPerHour**: Eine Stunde pro Eintrag, chronologisch sortiert
2. **topTickersByCount**: Absteigend nach `count` sortiert, max 20 Einträge
3. **volumeByCurrency**: Absteigend nach `totalVolume` sortiert
4. **Deduplizierung**: Nur echte Käufe/Verkäufe zählen (keine Awards, Gifts, Tax Withholding)

---

## Gefilterte Transaktionstypen

Folgende Transaktionsmethoden werden **nicht** als echte Käufe/Verkäufe gezählt:

- `award_or_grant` / `AWARD`
- `gift` / `GIFT`
- `tax_withholding_or_exercise_cost` / `TAX_WITHHOLDING`
- `OPTION_EXERCISE`
- `TRANSFER`

Nur `BUY` und `SELL` werden in `byType` aggregiert.

---

## Fetch Funktion

```typescript
// lib/api/dashboard.ts

const API_BASE = "https://api.finanz-copilot.de/api/v1";

export interface DashboardStatsParams {
  hours?: number;
  timezone?: string;
}

export async function getDashboardStats(
  params: DashboardStatsParams = {}
): Promise<DashboardStatsResponse> {
  const { hours = 24, timezone } = params;

  const searchParams = new URLSearchParams();
  searchParams.set("hours", hours.toString());
  if (timezone) searchParams.set("timezone", timezone);

  const res = await fetch(`${API_BASE}/dashboard/stats?${searchParams}`, {
    headers: { accept: "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  return res.json();
}
```

---

## React Hook

```typescript
// hooks/useDashboardStats.ts

import { useState, useEffect, useCallback, useRef } from "react";
import { getDashboardStats } from "@/lib/api/dashboard";
import type { DashboardStatsResponse } from "@/types/dashboard.types";

interface UseDashboardStatsOptions {
  hours?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function useDashboardStats(options: UseDashboardStatsOptions = {}) {
  const { hours = 24, autoRefresh = true, refreshInterval = 60000 } = options;

  const [data, setData] = useState<DashboardStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(
    async (manual = false) => {
      if (abortRef.current) {
        abortRef.current.abort();
      }
      const controller = new AbortController();
      abortRef.current = controller;

      if (manual) setLoading(true);

      try {
        const result = await getDashboardStats({ hours });
        setData(result);
        setLastUpdated(new Date());
        setError(null);
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setError(err as Error);
        }
      } finally {
        if (manual) setLoading(false);
      }
    },
    [hours]
  );

  useEffect(() => {
    fetchData(true);
    return () => abortRef.current?.abort();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh || hours > 24) return;

    const id = setInterval(() => fetchData(false), refreshInterval);
    return () => clearInterval(id);
  }, [autoRefresh, hours, refreshInterval, fetchData]);

  return {
    data,
    loading,
    error,
    lastUpdated,
    refresh: () => fetchData(true),
  };
}
```

---

## Verfügbare Zeiträume

| Stunden | Label             | Auto-Refresh empfohlen |
| ------- | ----------------- | ---------------------- |
| 1       | Letzte Stunde     | ✅ Ja (30s)            |
| 6       | Letzte 6 Stunden  | ✅ Ja (60s)            |
| 12      | Letzte 12 Stunden | ✅ Ja (60s)            |
| 24      | Letzte 24 Stunden | ✅ Ja (60s)            |
| 48      | Letzte 2 Tage     | ⚠️ Optional (5min)     |
| 72      | Letzte 3 Tage     | ⚠️ Optional (5min)     |
| 168     | Letzte Woche      | ❌ Manuell             |
| 336     | Letzte 2 Wochen   | ❌ Manuell             |

---

## Error Responses

| Status | Beschreibung                                     |
| ------ | ------------------------------------------------ |
| 400    | Ungültiger Parameter (z.B. hours < 1 oder > 336) |
| 500    | Interner Serverfehler                            |
| 503    | Service temporär nicht verfügbar                 |

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Parameter 'hours' must be between 1 and 336",
    "details": {
      "parameter": "hours",
      "provided": 500,
      "min": 1,
      "max": 336
    }
  }
}
```

---

## Performance-Hinweise

1. **Caching**: Response kann für 30-60 Sekunden gecacht werden
2. **Stündliche Daten**: `processedPerHour` enthält nur Stunden mit Aktivität
3. **Top Tickers**: Limitiert auf 20 Einträge für schnelle Antwortzeiten
4. **Compression**: gzip-Komprimierung empfohlen

---

## Migration von alter API

Die alte API unter `/get/insiderTrades/stats` wird deprecated. Migration:

| Alt                                 | Neu                                |
| ----------------------------------- | ---------------------------------- |
| `/get/insiderTrades/stats?hours=24` | `/api/v1/dashboard/stats?hours=24` |
| `processedStocks24h`                | `processing.processedStocks`       |
| `newTrades24h`                      | `insiderTrades.newTrades`          |

Die Response-Struktur bleibt weitgehend kompatibel.

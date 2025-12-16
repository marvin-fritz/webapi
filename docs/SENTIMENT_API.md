# Sentiment-API Dokumentation

Diese Dokumentation beschreibt die Sentiment-API zur Analyse von Insider-Trading-Aktivitäten.

## Base URL

```
https://api.finanz-copilot.de/api/v1/sentiment
```

---

## Konzept

Die Sentiment-API analysiert Insider-Trading-Aktivitäten und berechnet daraus verschiedene Indikatoren:

| Indikator                | Beschreibung                          | Formel                               |
| ------------------------ | ------------------------------------- | ------------------------------------ |
| **Insider-Indikator**    | Anteil Käufe an Gesamt-Transaktionen  | `(Käufe / (Käufe + Verkäufe)) × 100` |
| **Insider-Barometer**    | Abweichung vom 12-Monats-Durchschnitt | `Aktueller Indikator - Ø 365 Tage`   |
| **Aktivitäts-Indikator** | Durchschnittliche Transaktionen/Tag   | `Transaktionen / Tage im Fenster`    |

### Parameter

- **Gleitendes Fenster**: 28 Tage
- **Referenzzeitraum**: 365 Tage (12 Monate)
- **Deduplizierung**: Mehrere Transaktionen desselben Insiders am gleichen Tag werden nur einmal gezählt

### Gefilterte Transaktionstypen

Folgende Transaktionsmethoden werden **nicht** als echte Käufe/Verkäufe gezählt:

- `award_or_grant` / `AWARD`
- `gift` / `GIFT`
- `tax_withholding_or_exercise_cost` / `TAX_WITHHOLDING`
- `OPTION_EXERCISE`

---

## TypeScript Types

```typescript
// types/sentiment.ts

// === Interpretation Enums ===
export type IndicatorInterpretation =
  | "bullish"
  | "slightly_bullish"
  | "neutral"
  | "slightly_bearish"
  | "bearish";

export type BarometerInterpretation =
  | "strong_bullish"
  | "bullish"
  | "neutral"
  | "bearish"
  | "strong_bearish";

export type ActivityInterpretation = "very_high" | "high" | "normal" | "low";

export type MomentumInterpretation =
  | "accelerating_bullish"
  | "bullish"
  | "mixed"
  | "bearish"
  | "accelerating_bearish";

export type CompanySentiment =
  | "strong_bullish"
  | "bullish"
  | "neutral"
  | "bearish"
  | "strong_bearish";

// === Time Series Data Points ===
export interface IndicatorDataPoint {
  date: string;
  value: number;
  buys: number;
  sells: number;
  transactions: number;
}

export interface BarometerDataPoint {
  date: string;
  value: number;
  currentIndicator: number;
  average12m: number;
  normalized: number;
}

export interface ActivityDataPoint {
  date: string;
  value: number;
  totalTransactions: number;
  windowDays: number;
  average12m?: number;
  deviationPercent?: number;
  normalized?: number;
}

// === Current Values ===
export interface InsiderIndicatorCurrent {
  value: number;
  buys: number;
  sells: number;
  transactions: number;
  interpretation: IndicatorInterpretation;
}

export interface InsiderBarometerCurrent {
  value: number;
  normalized: number;
  average12m: number;
  interpretation: BarometerInterpretation;
}

export interface ActivityIndicatorCurrent {
  value: number;
  deviationPercent: number;
  interpretation: ActivityInterpretation;
}

export interface CurrentSentiment {
  insiderIndicator: InsiderIndicatorCurrent;
  insiderBarometer: InsiderBarometerCurrent;
  activityIndicator: ActivityIndicatorCurrent;
}

// === Market Statistics ===
export interface MarketStatistics {
  totalTransactions: number;
  totalBuys: number;
  totalSells: number;
  avgDailyTransactions: number;
  buySellRatio: number;
  activeDays: number;
  daysWithoutActivity: number;
  dataQuality: "excellent" | "good" | "moderate" | "limited";
  dataQualityScore: number;
}

// === Full Sentiment Response ===
export interface SentimentResponse {
  metadata: {
    generatedAt: string;
    timeRange: {
      days: number;
      from: string;
      to: string;
    };
    jurisdiction: string;
    parameters: {
      indicatorWindow: number;
      referencePeriod: number;
    };
    dataPoints: number;
  };
  current: CurrentSentiment;
  timeSeries: {
    insiderIndicator: IndicatorDataPoint[];
    insiderBarometer: BarometerDataPoint[];
    activityIndicator: ActivityDataPoint[];
  };
  marketStatistics: MarketStatistics;
}

// === Current Sentiment Response ===
export interface CurrentSentimentResponse {
  metadata: {
    generatedAt: string;
    jurisdiction: string;
  };
  current: CurrentSentiment;
}

// === Market Breadth ===
export interface JurisdictionBreakdown {
  jurisdiction: string;
  transactions: number;
  buys: number;
  sells: number;
  buyRatio: number;
}

export interface TopActiveCompany {
  isin: string;
  companyName: string;
  jurisdiction: string;
  transactions: number;
  buys: number;
  sells: number;
  buyRatio: number;
  sentiment: CompanySentiment;
  lastActivity: string | null;
}

export interface MarketBreadthResponse {
  metadata: {
    generatedAt: string;
    days: number;
    jurisdiction: string;
  };
  breadthMetrics: {
    totalActiveCompanies: number;
    bullishCompanies: number;
    bearishCompanies: number;
    neutralCompanies: number;
    breadthRatio: number;
  };
  jurisdictionBreakdown: JurisdictionBreakdown[];
  topActiveCompanies: TopActiveCompany[];
}

// === Top Movers ===
export interface TopMover {
  isin: string;
  companyName: string;
  jurisdiction: string;
  transactions: number;
  buys: number;
  sells: number;
  buyRatio: number;
  uniqueInsiders: number;
  activityScore: number;
  sentiment: CompanySentiment;
  lastActivity: string | null;
}

export interface TopMoversResponse {
  metadata: {
    generatedAt: string;
    days: number;
    limit: number;
    minTransactions: number;
    jurisdiction: string;
    resultCount: number;
  };
  topMovers: TopMover[];
}

// === Trends ===
export interface TrendWindow {
  avgIndicator: number;
  recentBuys: number;
  recentSells: number;
  sentiment: IndicatorInterpretation;
}

export interface TrendsResponse {
  metadata: {
    generatedAt: string;
    jurisdiction: string;
  };
  trends: {
    "7d": TrendWindow;
    "28d": TrendWindow;
    "90d": TrendWindow;
    "365d": TrendWindow;
  };
  momentum: {
    shortTerm?: number;
    mediumTerm?: number;
    longTerm?: number;
  };
  interpretation: MomentumInterpretation;
}
```

---

## API Endpoints

### 1. Vollständige Sentiment-Analyse

```
GET /api/v1/sentiment
```

| Parameter      | Typ    | Required | Default | Beschreibung                   |
| -------------- | ------ | -------- | ------- | ------------------------------ |
| `days`         | int    | ❌       | 90      | Anzahl Tage Historie (1-730)   |
| `jurisdiction` | string | ❌       | ALL     | Filter: `US`, `DE`, `GB`, etc. |

**Anwendungsfall:** Chart-Darstellung mit Zeitreihen

---

### 2. Aktuelle Werte (Schnell)

```
GET /api/v1/sentiment/current
```

| Parameter      | Typ    | Required | Default | Beschreibung             |
| -------------- | ------ | -------- | ------- | ------------------------ |
| `jurisdiction` | string | ❌       | ALL     | Filter nach Jurisdiktion |

**Anwendungsfall:** Dashboard-Anzeige, KPI-Widgets

---

### 3. Marktbreite-Analyse

```
GET /api/v1/sentiment/market-breadth
```

| Parameter      | Typ    | Required | Default | Beschreibung             |
| -------------- | ------ | -------- | ------- | ------------------------ |
| `days`         | int    | ❌       | 30      | Analysezeitraum (1-365)  |
| `jurisdiction` | string | ❌       | ALL     | Filter nach Jurisdiktion |

**Anwendungsfall:** Sektor-/Ländervergleiche, Top-Unternehmen-Listen

---

### 4. Top Movers

```
GET /api/v1/sentiment/top-movers
```

| Parameter         | Typ    | Required | Default | Beschreibung                |
| ----------------- | ------ | -------- | ------- | --------------------------- |
| `days`            | int    | ❌       | 7       | Zeitraum (1-90)             |
| `limit`           | int    | ❌       | 20      | Max Ergebnisse (1-100)      |
| `jurisdiction`    | string | ❌       | ALL     | Filter nach Jurisdiktion    |
| `minTransactions` | int    | ❌       | 3       | Mindestanzahl Transaktionen |

**Anwendungsfall:** "Hot Stocks" Watchlist, Screening

---

### 5. Trend-Analyse

```
GET /api/v1/sentiment/trends
```

| Parameter      | Typ    | Required | Default | Beschreibung             |
| -------------- | ------ | -------- | ------- | ------------------------ |
| `jurisdiction` | string | ❌       | ALL     | Filter nach Jurisdiktion |

**Anwendungsfall:** Momentum-Analyse, Trendwende-Erkennung

---

## Fetch Funktionen

```typescript
// lib/api/sentiment.ts

const API_BASE = "https://api.finanz-copilot.de/api/v1";

export async function getSentiment(
  days = 90,
  jurisdiction?: string
): Promise<SentimentResponse> {
  const params = new URLSearchParams({ days: days.toString() });
  if (jurisdiction) params.set("jurisdiction", jurisdiction);

  const res = await fetch(`${API_BASE}/sentiment?${params}`);
  if (!res.ok) throw new Error("Sentiment fetch failed");
  return res.json();
}

export async function getCurrentSentiment(
  jurisdiction?: string
): Promise<CurrentSentimentResponse> {
  const params = jurisdiction ? new URLSearchParams({ jurisdiction }) : "";

  const res = await fetch(`${API_BASE}/sentiment/current?${params}`);
  if (!res.ok) throw new Error("Current sentiment fetch failed");
  return res.json();
}

export async function getMarketBreadth(
  days = 30,
  jurisdiction?: string
): Promise<MarketBreadthResponse> {
  const params = new URLSearchParams({ days: days.toString() });
  if (jurisdiction) params.set("jurisdiction", jurisdiction);

  const res = await fetch(`${API_BASE}/sentiment/market-breadth?${params}`);
  if (!res.ok) throw new Error("Market breadth fetch failed");
  return res.json();
}

export async function getTopMovers(options?: {
  days?: number;
  limit?: number;
  jurisdiction?: string;
  minTransactions?: number;
}): Promise<TopMoversResponse> {
  const params = new URLSearchParams();
  if (options?.days) params.set("days", options.days.toString());
  if (options?.limit) params.set("limit", options.limit.toString());
  if (options?.jurisdiction) params.set("jurisdiction", options.jurisdiction);
  if (options?.minTransactions) {
    params.set("minTransactions", options.minTransactions.toString());
  }

  const res = await fetch(`${API_BASE}/sentiment/top-movers?${params}`);
  if (!res.ok) throw new Error("Top movers fetch failed");
  return res.json();
}

export async function getTrends(
  jurisdiction?: string
): Promise<TrendsResponse> {
  const params = jurisdiction ? new URLSearchParams({ jurisdiction }) : "";

  const res = await fetch(`${API_BASE}/sentiment/trends?${params}`);
  if (!res.ok) throw new Error("Trends fetch failed");
  return res.json();
}
```

---

## React Hooks

### useSentiment Hook

```typescript
// hooks/useSentiment.ts

import { useState, useEffect } from "react";
import { getSentiment, getCurrentSentiment } from "@/lib/api/sentiment";
import { SentimentResponse, CurrentSentimentResponse } from "@/types/sentiment";

interface UseSentimentOptions {
  days?: number;
  jurisdiction?: string;
  fullHistory?: boolean;
  refreshInterval?: number;
}

export function useSentiment(options: UseSentimentOptions = {}) {
  const {
    days = 90,
    jurisdiction,
    fullHistory = true,
    refreshInterval,
  } = options;

  const [data, setData] = useState<
    SentimentResponse | CurrentSentimentResponse | null
  >(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setIsLoading(true);
        const result = fullHistory
          ? await getSentiment(days, jurisdiction)
          : await getCurrentSentiment(jurisdiction);

        if (isMounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchData();

    // Optional: Auto-Refresh
    let interval: NodeJS.Timeout;
    if (refreshInterval) {
      interval = setInterval(fetchData, refreshInterval);
    }

    return () => {
      isMounted = false;
      if (interval) clearInterval(interval);
    };
  }, [days, jurisdiction, fullHistory, refreshInterval]);

  return { data, isLoading, error };
}
```

### useTopMovers Hook

```typescript
// hooks/useTopMovers.ts

import { useState, useEffect } from "react";
import { getTopMovers } from "@/lib/api/sentiment";
import { TopMoversResponse } from "@/types/sentiment";

interface UseTopMoversOptions {
  days?: number;
  limit?: number;
  jurisdiction?: string;
  minTransactions?: number;
}

export function useTopMovers(options: UseTopMoversOptions = {}) {
  const [data, setData] = useState<TopMoversResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setIsLoading(true);
        const result = await getTopMovers(options);
        if (isMounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [
    options.days,
    options.limit,
    options.jurisdiction,
    options.minTransactions,
  ]);

  return { data, isLoading, error };
}
```

---

## Beispiel-Komponenten

### Sentiment Dashboard Widget

```tsx
// components/SentimentWidget.tsx

"use client";

import { useSentiment } from "@/hooks/useSentiment";
import { CurrentSentimentResponse } from "@/types/sentiment";

function getColorClass(interpretation: string): string {
  switch (interpretation) {
    case "bullish":
    case "strong_bullish":
    case "slightly_bullish":
      return "text-green-600 bg-green-100";
    case "bearish":
    case "strong_bearish":
    case "slightly_bearish":
      return "text-red-600 bg-red-100";
    default:
      return "text-gray-600 bg-gray-100";
  }
}

export function SentimentWidget({ jurisdiction }: { jurisdiction?: string }) {
  const { data, isLoading, error } = useSentiment({
    fullHistory: false,
    jurisdiction,
  });

  if (isLoading) {
    return <div className="animate-pulse h-32 bg-gray-200 rounded-lg" />;
  }

  if (error || !data) {
    return <div className="text-red-500">Fehler beim Laden</div>;
  }

  const { current } = data as CurrentSentimentResponse;

  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Insider Indikator */}
      <div className="p-4 bg-white rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Insider-Indikator</h3>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold">
            {current.insiderIndicator.value.toFixed(1)}%
          </span>
          <span
            className={`px-2 py-1 rounded text-xs ${getColorClass(
              current.insiderIndicator.interpretation
            )}`}
          >
            {current.insiderIndicator.interpretation}
          </span>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          {current.insiderIndicator.buys} Käufe /{" "}
          {current.insiderIndicator.sells} Verkäufe
        </p>
      </div>

      {/* Barometer */}
      <div className="p-4 bg-white rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Barometer</h3>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold">
            {current.insiderBarometer.normalized > 0 ? "+" : ""}
            {current.insiderBarometer.normalized.toFixed(0)}
          </span>
          <span
            className={`px-2 py-1 rounded text-xs ${getColorClass(
              current.insiderBarometer.interpretation
            )}`}
          >
            {current.insiderBarometer.interpretation}
          </span>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          vs. Ø {current.insiderBarometer.average12m.toFixed(1)}%
        </p>
      </div>

      {/* Aktivität */}
      <div className="p-4 bg-white rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Aktivität</h3>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-bold">
            {current.activityIndicator.value.toFixed(1)}
          </span>
          <span className="text-sm text-gray-500">/Tag</span>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          {current.activityIndicator.deviationPercent > 0 ? "+" : ""}
          {current.activityIndicator.deviationPercent.toFixed(0)}% vs. Ø
        </p>
      </div>
    </div>
  );
}
```

### Top Movers Liste

```tsx
// components/TopMoversList.tsx

"use client";

import { useTopMovers } from "@/hooks/useTopMovers";
import Link from "next/link";

const sentimentEmoji: Record<string, string> = {
  strong_bullish: "🟢🟢",
  bullish: "🟢",
  neutral: "⚪",
  bearish: "🔴",
  strong_bearish: "🔴🔴",
};

export function TopMoversList({
  days = 7,
  limit = 10,
  jurisdiction,
}: {
  days?: number;
  limit?: number;
  jurisdiction?: string;
}) {
  const { data, isLoading, error } = useTopMovers({
    days,
    limit,
    jurisdiction,
  });

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="animate-pulse h-12 bg-gray-200 rounded" />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return <div className="text-red-500">Fehler beim Laden</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-4 py-3 border-b bg-gray-50">
        <h2 className="font-semibold">Top Insider-Aktivität ({days}T)</h2>
      </div>
      <ul className="divide-y">
        {data.topMovers.map((mover) => (
          <li key={mover.isin}>
            <Link
              href={`/stock/${mover.isin}`}
              className="flex items-center justify-between px-4 py-3 hover:bg-gray-50"
            >
              <div>
                <div className="font-medium">{mover.companyName}</div>
                <div className="text-sm text-gray-500">
                  {mover.isin} • {mover.jurisdiction}
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-2">
                  <span>{sentimentEmoji[mover.sentiment]}</span>
                  <span className="font-medium">
                    {mover.buyRatio.toFixed(0)}%
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  {mover.transactions} Tx • {mover.uniqueInsiders} Insider
                </div>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Beispiel Responses

### GET /api/v1/sentiment/current

```json
{
  "metadata": {
    "generatedAt": "2025-12-16T14:30:00.000Z",
    "jurisdiction": "ALL"
  },
  "current": {
    "insiderIndicator": {
      "value": 52.35,
      "buys": 127,
      "sells": 115,
      "transactions": 242,
      "interpretation": "slightly_bullish"
    },
    "insiderBarometer": {
      "value": 3.45,
      "normalized": 28.5,
      "average12m": 48.9,
      "interpretation": "bullish"
    },
    "activityIndicator": {
      "value": 8.64,
      "deviationPercent": 12.3,
      "interpretation": "normal"
    }
  }
}
```

### GET /api/v1/sentiment/top-movers?days=7&limit=3

```json
{
  "metadata": {
    "generatedAt": "2025-12-16T14:30:00.000Z",
    "days": 7,
    "limit": 3,
    "minTransactions": 3,
    "jurisdiction": "ALL",
    "resultCount": 3
  },
  "topMovers": [
    {
      "isin": "US0378331005",
      "companyName": "Apple Inc.",
      "jurisdiction": "US",
      "transactions": 12,
      "buys": 9,
      "sells": 3,
      "buyRatio": 75.0,
      "uniqueInsiders": 5,
      "activityScore": 60,
      "sentiment": "strong_bullish",
      "lastActivity": "2025-12-15T09:30:00.000Z"
    },
    {
      "isin": "US5949181045",
      "companyName": "Microsoft Corporation",
      "jurisdiction": "US",
      "transactions": 8,
      "buys": 4,
      "sells": 4,
      "buyRatio": 50.0,
      "uniqueInsiders": 4,
      "activityScore": 32,
      "sentiment": "neutral",
      "lastActivity": "2025-12-14T16:00:00.000Z"
    },
    {
      "isin": "DE0007164600",
      "companyName": "SAP SE",
      "jurisdiction": "DE",
      "transactions": 6,
      "buys": 1,
      "sells": 5,
      "buyRatio": 16.67,
      "uniqueInsiders": 3,
      "activityScore": 18,
      "sentiment": "strong_bearish",
      "lastActivity": "2025-12-13T11:00:00.000Z"
    }
  ]
}
```

---

## Interpretation der Werte

### Insider-Indikator

| Wert   | Interpretation     | Bedeutung                        |
| ------ | ------------------ | -------------------------------- |
| ≥ 60%  | `bullish`          | Deutlich mehr Käufe als Verkäufe |
| 45-60% | `slightly_bullish` | Leicht überwiegend Käufe         |
| 40-45% | `neutral`          | Ausgeglichenes Verhältnis        |
| 30-40% | `slightly_bearish` | Leicht überwiegend Verkäufe      |
| < 30%  | `bearish`          | Deutlich mehr Verkäufe als Käufe |

### Barometer (Normalisiert)

| Wert        | Interpretation   | Bedeutung                        |
| ----------- | ---------------- | -------------------------------- |
| ≥ +50       | `strong_bullish` | Weit über 12-Monats-Durchschnitt |
| +20 bis +50 | `bullish`        | Über Durchschnitt                |
| -20 bis +20 | `neutral`        | Im Durchschnittsbereich          |
| -50 bis -20 | `bearish`        | Unter Durchschnitt               |
| < -50       | `strong_bearish` | Weit unter Durchschnitt          |

### Aktivitäts-Abweichung

| Wert          | Interpretation | Bedeutung                        |
| ------------- | -------------- | -------------------------------- |
| ≥ +50%        | `very_high`    | Außergewöhnlich hohe Aktivität   |
| +20% bis +50% | `high`         | Erhöhte Aktivität                |
| -20% bis +20% | `normal`       | Normale Aktivität                |
| < -20%        | `low`          | Unterdurchschnittliche Aktivität |

---

## Verfügbare Jurisdiktionen

| Code | Land           |
| ---- | -------------- |
| `US` | United States  |
| `DE` | Deutschland    |
| `GB` | Großbritannien |
| `FR` | Frankreich     |
| `CH` | Schweiz        |
| `AT` | Österreich     |
| `NL` | Niederlande    |
| ...  | weitere        |

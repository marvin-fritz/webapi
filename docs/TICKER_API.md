# Ticker API Dokumentation

Diese Dokumentation beschreibt die Ticker API für die Integration in React/Next.js Apps.

## Base URL

```
https://api.finanz-copilot.de/api/v1/ticker
```

---

## Übersicht

Die Ticker API identifiziert interessante Aktien basierend auf Insider-Trading-Mustern:

- **Cluster-Käufe**: Mehrere Insider kaufen gleichzeitig
- **Hohes Volumen**: Signifikante Transaktionsbeträge
- **Dominante Käufe**: Kaufvolumen überwiegt Verkäufe

Nur Open-Market-Transaktionen werden berücksichtigt (keine Awards, Gifts, etc.).

---

## TypeScript Types

```typescript
// types/ticker.ts

export type TickerSignal =
  | "CLUSTER_BUYING" // ≥2 verschiedene Insider kaufen
  | "HIGH_VOLUME" // Kaufvolumen >100.000
  | "PURE_BUYING" // Nur Käufe, keine Verkäufe
  | "DOMINANT_BUYING"; // Kaufvolumen >2x Verkaufsvolumen

export interface TickerItem {
  uid: string;
  isin: string;
  companyName: string;
  currency: string | null;
  lastTransactionDate: string | null;

  // Trade counts
  tradeCount: number;
  buyCount: number;
  sellCount: number;

  // Volume metrics
  buyVolume: number;
  sellVolume: number;
  netVolume: number;

  // Unique insiders
  uniqueBuyersCount: number;
  uniqueSellersCount: number;
  buyers: string[];
  sellers: string[];

  // Analysis
  signals: TickerSignal[];
  headline: string;
}

export interface TickerMeta {
  generatedAt: string;
  windowDays: number;
  minTrades: number;
  minTotalAmount: number;
  limit: number;
  count: number;
  singleIsin?: string;
}

export interface TickerResponse {
  meta: TickerMeta;
  items: TickerItem[];
}
```

---

## API Endpoints

| Endpoint             | Beschreibung                     |
| -------------------- | -------------------------------- |
| `GET /ticker`        | Alle Aktien mit Insider-Signalen |
| `GET /ticker/{isin}` | Signale für spezifische ISIN     |

### Query Parameter

| Parameter        | Typ    | Default | Beschreibung                         |
| ---------------- | ------ | ------- | ------------------------------------ |
| `days`           | int    | 30      | Analysefenster in Tagen (1-365)      |
| `minTrades`      | int    | 1       | Mindestanzahl Trades                 |
| `minTotalAmount` | float  | 10000   | Mindest-Kaufvolumen                  |
| `isin`           | string | -       | Filter nach ISIN(s), kommasepariert  |
| `source`         | string | -       | Filter nach Quelle (sec, bafin, ser) |
| `limit`          | int    | 100     | Max. Ergebnisse (1-500)              |

### Beispiel-Aufrufe

```bash
# Top Insider-Signale der letzten 30 Tage
GET /api/v1/ticker

# Letzte 7 Tage mit höherem Mindestvolumen
GET /api/v1/ticker?days=7&minTotalAmount=50000

# Nur SEC-Daten (US-Aktien)
GET /api/v1/ticker?source=sec&limit=20

# Spezifische ISIN
GET /api/v1/ticker/US0378331005

# Mehrere ISINs filtern
GET /api/v1/ticker?isin=US0378331005,US5949181045
```

---

## Signal-Typen

| Signal            | Bedingung                | Bedeutung                                                       |
| ----------------- | ------------------------ | --------------------------------------------------------------- |
| `CLUSTER_BUYING`  | ≥2 unique Käufer         | Mehrere Insider kaufen gleichzeitig - starkes bullisches Signal |
| `HIGH_VOLUME`     | Kaufvolumen >100.000     | Signifikante Position aufgebaut                                 |
| `PURE_BUYING`     | Nur Käufe, 0 Verkäufe    | Keine Insider verkaufen - sehr positiv                          |
| `DOMINANT_BUYING` | Kaufvolumen >2x Verkäufe | Käufer überwiegen deutlich                                      |

---

## Fetch Funktionen

```typescript
// lib/api/ticker.ts

import { TickerResponse } from "@/types/ticker";

const API_BASE = "https://api.finanz-copilot.de/api/v1/ticker";

export interface TickerParams {
  days?: number;
  minTrades?: number;
  minTotalAmount?: number;
  isin?: string[];
  source?: "sec" | "bafin" | "ser";
  limit?: number;
}

export async function fetchTickerSignals(
  params: TickerParams = {}
): Promise<TickerResponse> {
  const searchParams = new URLSearchParams();

  if (params.days) searchParams.set("days", params.days.toString());
  if (params.minTrades)
    searchParams.set("minTrades", params.minTrades.toString());
  if (params.minTotalAmount)
    searchParams.set("minTotalAmount", params.minTotalAmount.toString());
  if (params.isin?.length) searchParams.set("isin", params.isin.join(","));
  if (params.source) searchParams.set("source", params.source);
  if (params.limit) searchParams.set("limit", params.limit.toString());

  const url = searchParams.toString()
    ? `${API_BASE}?${searchParams}`
    : API_BASE;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Ticker API error: ${response.status}`);
  }

  return response.json();
}

export async function fetchTickerByIsin(
  isin: string,
  params: Omit<TickerParams, "isin"> = {}
): Promise<TickerResponse> {
  const searchParams = new URLSearchParams();

  if (params.days) searchParams.set("days", params.days.toString());
  if (params.minTrades)
    searchParams.set("minTrades", params.minTrades.toString());
  if (params.minTotalAmount)
    searchParams.set("minTotalAmount", params.minTotalAmount.toString());
  if (params.source) searchParams.set("source", params.source);
  if (params.limit) searchParams.set("limit", params.limit.toString());

  const url = searchParams.toString()
    ? `${API_BASE}/${isin}?${searchParams}`
    : `${API_BASE}/${isin}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Ticker API error: ${response.status}`);
  }

  return response.json();
}
```

---

## React Hooks

### Mit SWR

```typescript
// hooks/useTicker.ts

import useSWR from "swr";
import { TickerResponse, TickerParams } from "@/types/ticker";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useTickerSignals(params: TickerParams = {}) {
  const searchParams = new URLSearchParams();
  if (params.days) searchParams.set("days", params.days.toString());
  if (params.minTrades)
    searchParams.set("minTrades", params.minTrades.toString());
  if (params.minTotalAmount)
    searchParams.set("minTotalAmount", params.minTotalAmount.toString());
  if (params.source) searchParams.set("source", params.source);
  if (params.limit) searchParams.set("limit", params.limit.toString());

  const url = searchParams.toString()
    ? `https://api.finanz-copilot.de/api/v1/ticker?${searchParams}`
    : "https://api.finanz-copilot.de/api/v1/ticker";

  return useSWR<TickerResponse>(url, fetcher, {
    refreshInterval: 5 * 60 * 1000, // 5 Minuten
    revalidateOnFocus: false,
  });
}

export function useTickerByIsin(
  isin: string | null,
  params: TickerParams = {}
) {
  const searchParams = new URLSearchParams();
  if (params.days) searchParams.set("days", params.days.toString());
  if (params.source) searchParams.set("source", params.source);

  const url = isin
    ? `https://api.finanz-copilot.de/api/v1/ticker/${isin}?${searchParams}`
    : null;

  return useSWR<TickerResponse>(url, fetcher);
}
```

### Mit TanStack Query

```typescript
// hooks/useTicker.ts

import { useQuery } from "@tanstack/react-query";
import {
  fetchTickerSignals,
  fetchTickerByIsin,
  TickerParams,
} from "@/lib/api/ticker";

export function useTickerSignals(params: TickerParams = {}) {
  return useQuery({
    queryKey: ["ticker", params],
    queryFn: () => fetchTickerSignals(params),
    staleTime: 5 * 60 * 1000, // 5 Minuten
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useTickerByIsin(
  isin: string,
  params: Omit<TickerParams, "isin"> = {}
) {
  return useQuery({
    queryKey: ["ticker", isin, params],
    queryFn: () => fetchTickerByIsin(isin, params),
    enabled: !!isin,
  });
}
```

---

## Beispiel-Komponenten

### Signal Badge

```tsx
// components/SignalBadge.tsx

import { TickerSignal } from "@/types/ticker";

const signalConfig: Record<TickerSignal, { label: string; color: string }> = {
  CLUSTER_BUYING: { label: "Cluster-Kauf", color: "bg-green-500" },
  HIGH_VOLUME: { label: "Hohes Volumen", color: "bg-blue-500" },
  PURE_BUYING: { label: "Nur Käufe", color: "bg-emerald-500" },
  DOMINANT_BUYING: { label: "Kauf-Dominanz", color: "bg-teal-500" },
};

export function SignalBadge({ signal }: { signal: TickerSignal }) {
  const config = signalConfig[signal];

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white ${config.color}`}
    >
      {config.label}
    </span>
  );
}
```

### Ticker Card

```tsx
// components/TickerCard.tsx

"use client";

import { TickerItem } from "@/types/ticker";
import { SignalBadge } from "./SignalBadge";

interface TickerCardProps {
  item: TickerItem;
}

export function TickerCard({ item }: TickerCardProps) {
  const buyRatio =
    item.tradeCount > 0
      ? ((item.buyCount / item.tradeCount) * 100).toFixed(0)
      : 0;

  return (
    <div className="bg-card border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-lg">{item.companyName}</h3>
          <p className="text-sm text-muted-foreground font-mono">{item.isin}</p>
        </div>
        <span className="text-sm text-muted-foreground">
          {item.lastTransactionDate
            ? new Date(item.lastTransactionDate).toLocaleDateString("de-DE")
            : "-"}
        </span>
      </div>

      {/* Signals */}
      <div className="flex flex-wrap gap-1 mb-3">
        {item.signals.map((signal) => (
          <SignalBadge key={signal} signal={signal} />
        ))}
      </div>

      {/* Headline */}
      <p className="text-sm mb-3">{item.headline}</p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 text-center text-sm">
        <div>
          <p className="font-semibold text-green-600">
            {item.buyVolume.toLocaleString("de-DE")} {item.currency}
          </p>
          <p className="text-muted-foreground">Kaufvolumen</p>
        </div>
        <div>
          <p className="font-semibold">{item.uniqueBuyersCount}</p>
          <p className="text-muted-foreground">Käufer</p>
        </div>
        <div>
          <p className="font-semibold">{buyRatio}%</p>
          <p className="text-muted-foreground">Kauf-Anteil</p>
        </div>
      </div>
    </div>
  );
}
```

### Ticker List

```tsx
// components/TickerList.tsx

"use client";

import { useTickerSignals } from "@/hooks/useTicker";
import { TickerCard } from "./TickerCard";
import { Skeleton } from "@/components/ui/skeleton";

interface TickerListProps {
  days?: number;
  source?: "sec" | "bafin" | "ser";
  limit?: number;
}

export function TickerList({ days = 30, source, limit = 20 }: TickerListProps) {
  const { data, isLoading, error } = useTickerSignals({ days, source, limit });

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-500">
        Fehler beim Laden der Daten
      </div>
    );
  }

  if (!data?.items.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Keine Insider-Signale im gewählten Zeitraum
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        {data.meta.count} Aktien mit Insider-Aktivität in den letzten{" "}
        {data.meta.windowDays} Tagen
      </p>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data.items.map((item) => (
          <TickerCard key={item.uid} item={item} />
        ))}
      </div>
    </div>
  );
}
```

---

## Beispiel-Response

```json
{
  "meta": {
    "generatedAt": "2025-12-25T10:00:00+00:00",
    "windowDays": 30,
    "minTrades": 1,
    "minTotalAmount": 10000,
    "limit": 100,
    "count": 3
  },
  "items": [
    {
      "uid": "TICKER-US0378331005-2025-12-20T00:00:00+00:00",
      "isin": "US0378331005",
      "companyName": "Apple Inc.",
      "currency": "USD",
      "lastTransactionDate": "2025-12-20T00:00:00+00:00",
      "tradeCount": 5,
      "buyCount": 5,
      "sellCount": 0,
      "buyVolume": 250000,
      "sellVolume": 0,
      "netVolume": 250000,
      "uniqueBuyersCount": 3,
      "uniqueSellersCount": 0,
      "buyers": ["Tim Cook", "Jeff Williams", "Luca Maestri"],
      "sellers": [],
      "signals": ["CLUSTER_BUYING", "HIGH_VOLUME", "PURE_BUYING"],
      "headline": "3 Insider (Tim Cook, Jeff Williams und 1 weitere) kauften für 250,000 USD Anteile von Apple Inc."
    },
    {
      "uid": "TICKER-DE0007164600-2025-12-18T00:00:00+00:00",
      "isin": "DE0007164600",
      "companyName": "SAP SE",
      "currency": "EUR",
      "lastTransactionDate": "2025-12-18T00:00:00+00:00",
      "tradeCount": 3,
      "buyCount": 2,
      "sellCount": 1,
      "buyVolume": 150000,
      "sellVolume": 30000,
      "netVolume": 120000,
      "uniqueBuyersCount": 2,
      "uniqueSellersCount": 1,
      "buyers": ["Christian Klein", "Sabine Bendiek"],
      "sellers": ["Thomas Saueressig"],
      "signals": ["CLUSTER_BUYING", "HIGH_VOLUME", "DOMINANT_BUYING"],
      "headline": "2 Insider (Christian Klein, Sabine Bendiek) kauften für 150,000 EUR Anteile von SAP SE."
    }
  ]
}
```

---

## Changelog

| Version | Datum   | Änderungen      |
| ------- | ------- | --------------- |
| 1.0.0   | 2025-12 | Initial Release |

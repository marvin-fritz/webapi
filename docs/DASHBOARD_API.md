# Dashboard API Documentation

Diese Dokumentation beschreibt die Dashboard API-Endpunkte für die Integration in React/Next.js Frontends.

## Base URL

```
https://api.finanz-copilot.de/api/v1/dashboard
```

## TypeScript Types

```typescript
// Time range information
interface TimeRange {
  start: string; // ISO 8601 datetime
  end: string; // ISO 8601 datetime
  hours: number;
  timezone: string;
}

// Processing statistics
interface ProcessingStats {
  total: number;
  processed: number;
  pending: number;
  processingRate: number; // 0-100 percentage
}

// Trades grouped by hour
interface ProcessedPerHour {
  hour: string; // ISO 8601 datetime
  count: number;
}

// Trades grouped by type
interface TradesByType {
  type: string;
  count: number;
  percentage: number;
}

// Top ticker by trade count
interface TopTicker {
  ticker: string;
  count: number;
  totalValue: number;
}

// Volume grouped by currency
interface VolumeByCurrency {
  currency: string;
  totalVolume: number;
  tradeCount: number;
}

// Insider trades statistics
interface InsiderTradesStats {
  processedPerHour: ProcessedPerHour[];
  tradesByType: TradesByType[];
  topTickers: TopTicker[];
  volumeByCurrency: VolumeByCurrency[];
}

// Jurisdiction breakdown (extended)
interface JurisdictionStats {
  jurisdiction: string;
  count: number;
  percentage: number;
}

// Top insider by trade count (extended)
interface TopInsider {
  name: string;
  ticker: string;
  tradeCount: number;
  totalValue: number;
}

// Extended statistics (optional)
interface ExtendedStats {
  jurisdictionBreakdown: JurisdictionStats[];
  topInsiders: TopInsider[];
}

// Full dashboard stats response
interface DashboardStatsResponse {
  timeRange: TimeRange;
  processing: ProcessingStats;
  insiderTrades: InsiderTradesStats;
  extended?: ExtendedStats;
}

// Quick stats response for widgets
interface QuickStatsResponse {
  totalTrades: number;
  processingRate: number;
  topTicker: string | null;
  trendDirection: "up" | "down" | "stable";
  periodHours: number;
}
```

## API Endpoints

### GET /stats

Gibt vollständige Dashboard-Statistiken zurück.

**Query Parameters:**

| Parameter          | Type    | Default | Description                         |
| ------------------ | ------- | ------- | ----------------------------------- |
| `hours`            | integer | 24      | Zeitraum in Stunden (1-168)         |
| `tz`               | string  | "UTC"   | Zeitzone für Berechnungen           |
| `include_extended` | boolean | false   | Erweiterte Statistiken einschließen |

**Response:** `DashboardStatsResponse`

**Example Request:**

```bash
GET /api/v1/dashboard/stats?hours=24&tz=Europe/Berlin&include_extended=true
```

**Example Response:**

```json
{
  "timeRange": {
    "start": "2024-01-14T10:00:00+01:00",
    "end": "2024-01-15T10:00:00+01:00",
    "hours": 24,
    "timezone": "Europe/Berlin"
  },
  "processing": {
    "total": 1250,
    "processed": 1180,
    "pending": 70,
    "processingRate": 94.4
  },
  "insiderTrades": {
    "processedPerHour": [
      { "hour": "2024-01-14T10:00:00+01:00", "count": 45 },
      { "hour": "2024-01-14T11:00:00+01:00", "count": 52 },
      { "hour": "2024-01-14T12:00:00+01:00", "count": 38 }
    ],
    "tradesByType": [
      { "type": "Purchase", "count": 580, "percentage": 49.2 },
      { "type": "Sale", "count": 420, "percentage": 35.6 },
      { "type": "Option Exercise", "count": 180, "percentage": 15.3 }
    ],
    "topTickers": [
      { "ticker": "AAPL", "count": 45, "totalValue": 12500000.0 },
      { "ticker": "MSFT", "count": 38, "totalValue": 9800000.0 },
      { "ticker": "GOOGL", "count": 32, "totalValue": 8200000.0 }
    ],
    "volumeByCurrency": [
      { "currency": "USD", "totalVolume": 45000000.0, "tradeCount": 980 },
      { "currency": "EUR", "totalVolume": 12000000.0, "tradeCount": 200 }
    ]
  },
  "extended": {
    "jurisdictionBreakdown": [
      { "jurisdiction": "USA", "count": 850, "percentage": 72.0 },
      { "jurisdiction": "CAN", "count": 180, "percentage": 15.3 },
      { "jurisdiction": "GBR", "count": 150, "percentage": 12.7 }
    ],
    "topInsiders": [
      {
        "name": "John Smith",
        "ticker": "AAPL",
        "tradeCount": 12,
        "totalValue": 5200000.0
      },
      {
        "name": "Jane Doe",
        "ticker": "MSFT",
        "tradeCount": 8,
        "totalValue": 3100000.0
      }
    ]
  }
}
```

---

### GET /quick

Gibt schnelle Statistiken für Dashboard-Widgets zurück.

**Query Parameters:**

| Parameter | Type    | Default | Description                 |
| --------- | ------- | ------- | --------------------------- |
| `hours`   | integer | 24      | Zeitraum in Stunden (1-168) |

**Response:** `QuickStatsResponse`

**Example Request:**

```bash
GET /api/v1/dashboard/quick?hours=24
```

**Example Response:**

```json
{
  "totalTrades": 1250,
  "processingRate": 94.4,
  "topTicker": "AAPL",
  "trendDirection": "up",
  "periodHours": 24
}
```

---

### GET /health

Health-Check für den Dashboard-Service.

**Response:**

```json
{
  "status": "healthy",
  "service": "dashboard"
}
```

---

## React/Next.js Integration

### Fetch Functions

```typescript
const API_BASE = "https://api.finanz-copilot.de/api/v1/dashboard";

interface DashboardStatsParams {
  hours?: number;
  tz?: string;
  includeExtended?: boolean;
}

export async function fetchDashboardStats(
  params: DashboardStatsParams = {}
): Promise<DashboardStatsResponse> {
  const { hours = 24, tz = "UTC", includeExtended = false } = params;

  const searchParams = new URLSearchParams({
    hours: hours.toString(),
    tz,
    include_extended: includeExtended.toString(),
  });

  const response = await fetch(`${API_BASE}/stats?${searchParams}`);

  if (!response.ok) {
    throw new Error(`Dashboard stats failed: ${response.status}`);
  }

  return response.json();
}

export async function fetchQuickStats(
  hours: number = 24
): Promise<QuickStatsResponse> {
  const response = await fetch(`${API_BASE}/quick?hours=${hours}`);

  if (!response.ok) {
    throw new Error(`Quick stats failed: ${response.status}`);
  }

  return response.json();
}
```

### React Hooks

```typescript
import useSWR from "swr";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function useDashboardStats(
  hours: number = 24,
  tz: string = "UTC",
  includeExtended: boolean = false
) {
  const params = new URLSearchParams({
    hours: hours.toString(),
    tz,
    include_extended: includeExtended.toString(),
  });

  return useSWR<DashboardStatsResponse>(
    `${API_BASE}/stats?${params}`,
    fetcher,
    {
      refreshInterval: 60000, // Refresh every minute
      revalidateOnFocus: true,
    }
  );
}

export function useQuickStats(hours: number = 24) {
  return useSWR<QuickStatsResponse>(
    `${API_BASE}/quick?hours=${hours}`,
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
    }
  );
}
```

### TanStack Query Hooks

```typescript
import { useQuery } from "@tanstack/react-query";

export function useDashboardStats(
  hours: number = 24,
  tz: string = "UTC",
  includeExtended: boolean = false
) {
  return useQuery({
    queryKey: ["dashboard-stats", hours, tz, includeExtended],
    queryFn: () => fetchDashboardStats({ hours, tz, includeExtended }),
    staleTime: 1000 * 60, // 1 minute
    refetchInterval: 1000 * 60, // Refetch every minute
  });
}

export function useQuickStats(hours: number = 24) {
  return useQuery({
    queryKey: ["quick-stats", hours],
    queryFn: () => fetchQuickStats(hours),
    staleTime: 1000 * 30, // 30 seconds
    refetchInterval: 1000 * 30,
  });
}
```

---

## Example Components

### Dashboard Stats Card

```tsx
"use client";

import { useDashboardStats } from "@/hooks/useDashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface DashboardStatsCardProps {
  hours?: number;
  timezone?: string;
}

export function DashboardStatsCard({
  hours = 24,
  timezone = "Europe/Berlin",
}: DashboardStatsCardProps) {
  const { data, isLoading, error } = useDashboardStats(hours, timezone, true);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-red-500">Failed to load dashboard stats</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dashboard Statistics</CardTitle>
        <p className="text-sm text-muted-foreground">
          {data.timeRange.start} - {data.timeRange.end}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Processing Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatItem
            label="Total Trades"
            value={data.processing.total.toLocaleString()}
          />
          <StatItem
            label="Processed"
            value={data.processing.processed.toLocaleString()}
          />
          <StatItem
            label="Pending"
            value={data.processing.pending.toLocaleString()}
          />
          <StatItem
            label="Processing Rate"
            value={`${data.processing.processingRate.toFixed(1)}%`}
          />
        </div>

        {/* Top Tickers */}
        <div>
          <h3 className="font-semibold mb-2">Top Tickers</h3>
          <div className="space-y-2">
            {data.insiderTrades.topTickers.slice(0, 5).map((ticker) => (
              <div
                key={ticker.ticker}
                className="flex justify-between items-center"
              >
                <span className="font-mono">{ticker.ticker}</span>
                <span className="text-muted-foreground">
                  {ticker.count} trades · ${ticker.totalValue.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Trade Types Distribution */}
        <div>
          <h3 className="font-semibold mb-2">Trade Types</h3>
          <div className="space-y-2">
            {data.insiderTrades.tradesByType.map((type) => (
              <div key={type.type} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>{type.type}</span>
                  <span>{type.percentage.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${type.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
```

### Quick Stats Widget

```tsx
"use client";

import { useQuickStats } from "@/hooks/useDashboard";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export function QuickStatsWidget() {
  const { data, isLoading } = useQuickStats(24);

  if (isLoading || !data) {
    return <div className="animate-pulse h-20 bg-muted rounded-lg" />;
  }

  const TrendIcon = {
    up: TrendingUp,
    down: TrendingDown,
    stable: Minus,
  }[data.trendDirection];

  const trendColor = {
    up: "text-green-500",
    down: "text-red-500",
    stable: "text-gray-500",
  }[data.trendDirection];

  return (
    <div className="flex items-center justify-between p-4 bg-card rounded-lg border">
      <div>
        <p className="text-sm text-muted-foreground">
          Last {data.periodHours}h
        </p>
        <p className="text-2xl font-bold">
          {data.totalTrades.toLocaleString()} trades
        </p>
        {data.topTicker && (
          <p className="text-sm">
            Top: <span className="font-mono">{data.topTicker}</span>
          </p>
        )}
      </div>
      <div className={`flex flex-col items-center ${trendColor}`}>
        <TrendIcon className="h-8 w-8" />
        <span className="text-sm">{data.processingRate.toFixed(1)}%</span>
      </div>
    </div>
  );
}
```

### Hourly Chart Component

```tsx
"use client";

import { useDashboardStats } from "@/hooks/useDashboard";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface HourlyChartProps {
  hours?: number;
}

export function HourlyChart({ hours = 24 }: HourlyChartProps) {
  const { data, isLoading } = useDashboardStats(hours, "Europe/Berlin");

  if (isLoading || !data) {
    return <div className="h-64 animate-pulse bg-muted rounded-lg" />;
  }

  const chartData = data.insiderTrades.processedPerHour.map((item) => ({
    hour: new Date(item.hour).toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
    }),
    count: item.count,
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <XAxis dataKey="hour" tick={{ fontSize: 12 }} tickLine={false} />
          <YAxis tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary) / 0.2)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## Error Handling

```typescript
interface APIError {
  detail: string;
  status_code?: number;
}

export async function fetchWithErrorHandling<T>(url: string): Promise<T> {
  const response = await fetch(url);

  if (!response.ok) {
    const error: APIError = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.detail);
  }

  return response.json();
}
```

---

## Rate Limiting

Die API hat folgende Limits:

- **Requests pro Minute:** 60
- **Empfohlenes Refresh-Interval:** 30-60 Sekunden

Bei Rate-Limiting wird HTTP 429 zurückgegeben:

```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Changelog

| Version | Date    | Changes                                          |
| ------- | ------- | ------------------------------------------------ |
| 1.0.0   | 2024-01 | Initial release with /stats and /quick endpoints |

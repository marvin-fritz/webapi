# Such-API Dokumentation

Diese Dokumentation beschreibt die Such-API für die Integration in React/Next.js Apps.

## Base URL

```
https://api.finanz-copilot.de/api/v1/search
```

---

## TypeScript Types

```typescript
// types/search.ts

export type SearchResultType = "stock" | "news";

export interface SearchResultAction {
  type: "redirect";
  url: string;
}

export interface SearchResult {
  id: string;
  type: SearchResultType;
  title: string;
  subtitle: string | null;
  description: string | null;
  image: string | null;
  action: SearchResultAction;
  relevanceScore: number;
  metadata: Record<string, any> | null;
  // Stock-spezifisch
  ticker?: string;
  isin?: string;
  exchangeCode?: string;
  // News-spezifisch
  source?: string;
  category?: string;
  pubDate?: string;
}

export interface SearchResponse {
  query: string;
  totalResults: number;
  results: SearchResult[];
  resultsByType: Record<string, number>;
}
```

---

## API Endpoints

| Endpoint             | Parameter                        | Beschreibung   |
| -------------------- | -------------------------------- | -------------- |
| `GET /search`        | `q` (required), `types`, `limit` | Unified Search |
| `GET /search/stocks` | `q` (required), `limit`          | Nur Aktien     |
| `GET /search/news`   | `q` (required), `limit`          | Nur News       |

### Query Parameter

| Parameter | Typ    | Required | Default | Beschreibung                  |
| --------- | ------ | -------- | ------- | ----------------------------- |
| `q`       | string | ✅       | -       | Suchbegriff (1-200 Zeichen)   |
| `types`   | array  | ❌       | alle    | Filter: `stock`, `news`       |
| `limit`   | int    | ❌       | 10      | Max Ergebnisse pro Typ (1-50) |

### Beispiel-Aufrufe

```bash
# Alle Typen durchsuchen
GET /api/v1/search?q=Apple

# Nur Aktien
GET /api/v1/search?q=Tesla&types=stock

# Mehrere Typen
GET /api/v1/search?q=Microsoft&types=stock&types=news&limit=5

# Shortcuts
GET /api/v1/search/stocks?q=AAPL&limit=20
GET /api/v1/search/news?q=Inflation&limit=10
```

---

## Fetch Funktion

```typescript
// lib/api/search.ts

import { SearchResponse, SearchResultType } from "@/types/search";

const API_BASE = "https://api.finanz-copilot.de/api/v1";

export async function searchAll(
  query: string,
  options?: {
    types?: SearchResultType[];
    limit?: number;
  }
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });

  if (options?.types) {
    options.types.forEach((t) => params.append("types", t));
  }
  if (options?.limit) {
    params.set("limit", options.limit.toString());
  }

  const res = await fetch(`${API_BASE}/search?${params}`);
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export async function searchStocks(
  query: string,
  limit = 20
): Promise<SearchResponse> {
  return searchAll(query, { types: ["stock"], limit });
}

export async function searchNews(
  query: string,
  limit = 20
): Promise<SearchResponse> {
  return searchAll(query, { types: ["news"], limit });
}
```

---

## React Hook mit Debounce

```typescript
// hooks/useSearch.ts

import { useState, useEffect } from "react";
import { searchAll } from "@/lib/api/search";
import { SearchResponse, SearchResultType } from "@/types/search";

interface UseSearchOptions {
  types?: SearchResultType[];
  limit?: number;
  debounceMs?: number;
  minLength?: number;
}

export function useSearch(query: string, options: UseSearchOptions = {}) {
  const { types, limit, debounceMs = 300, minLength = 2 } = options;

  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Zu kurze Queries ignorieren
    if (!query || query.length < minLength) {
      setResults(null);
      return;
    }

    const debounceTimer = setTimeout(async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await searchAll(query, { types, limit });
        setResults(data);
      } catch (err) {
        setError(err as Error);
        setResults(null);
      } finally {
        setIsLoading(false);
      }
    }, debounceMs);

    return () => clearTimeout(debounceTimer);
  }, [query, types?.join(","), limit, debounceMs, minLength]);

  return { results, isLoading, error };
}
```

---

## Beispiel: SearchBar Component

```tsx
// components/SearchBar.tsx

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSearch } from "@/hooks/useSearch";
import { SearchResult } from "@/types/search";

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const { results, isLoading } = useSearch(query, { limit: 5 });
  const router = useRouter();

  const handleResultClick = (result: SearchResult) => {
    setIsOpen(false);
    setQuery("");

    if (result.type === "stock") {
      // Interne Navigation für Stocks
      router.push(`/stock/${result.isin}`);
    } else {
      // Externe Navigation für News (neuer Tab)
      window.open(result.action.url, "_blank");
    }
  };

  return (
    <div className="relative">
      {/* Search Input */}
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setIsOpen(true);
        }}
        onFocus={() => setIsOpen(true)}
        placeholder="Aktien, News suchen..."
        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
      />

      {/* Loading Indicator */}
      {isLoading && (
        <div className="absolute right-3 top-2.5">
          <svg
            className="animate-spin h-5 w-5 text-gray-400"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        </div>
      )}

      {/* Results Dropdown */}
      {isOpen && results && results.totalResults > 0 && (
        <div className="absolute w-full mt-1 bg-white border rounded-lg shadow-lg z-50 max-h-96 overflow-auto">
          {results.results.map((result) => (
            <button
              key={result.id}
              onClick={() => handleResultClick(result)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 border-b last:border-b-0"
            >
              {/* Icon */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  result.type === "stock" ? "bg-blue-100" : "bg-green-100"
                }`}
              >
                {result.type === "stock" ? "📈" : "📰"}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{result.title}</div>
                <div className="text-sm text-gray-500 truncate">
                  {result.subtitle}
                </div>
              </div>

              {/* Type Badge */}
              <span
                className={`text-xs px-2 py-1 rounded ${
                  result.type === "stock"
                    ? "bg-blue-100 text-blue-700"
                    : "bg-green-100 text-green-700"
                }`}
              >
                {result.type === "stock" ? "Aktie" : "News"}
              </span>
            </button>
          ))}
        </div>
      )}

      {/* No Results */}
      {isOpen && results && results.totalResults === 0 && query.length >= 2 && (
        <div className="absolute w-full mt-1 bg-white border rounded-lg shadow-lg z-50 p-4 text-center text-gray-500">
          Keine Ergebnisse für "{query}"
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}
```

---

## Beispiel Response

**Request:**

```
GET /api/v1/search?q=Apple&limit=3
```

**Response:**

```json
{
  "query": "Apple",
  "totalResults": 4,
  "resultsByType": {
    "stock": 2,
    "news": 2
  },
  "results": [
    {
      "id": "6579a1b2c3d4e5f6a7b8c9d0",
      "type": "stock",
      "title": "Apple Inc.",
      "subtitle": "AAPL • US",
      "description": "Common Stock • Equity",
      "image": null,
      "ticker": "AAPL",
      "isin": "US0378331005",
      "exchangeCode": "US",
      "action": {
        "type": "redirect",
        "url": "https://finanz-copilot.de/stock/US0378331005"
      },
      "relevanceScore": 100.0,
      "metadata": {
        "securityType": "Common Stock",
        "marketSector": "Equity"
      }
    },
    {
      "id": "6580b2c3d4e5f6a7b8c9d0e1",
      "type": "news",
      "title": "Apple übertrifft Erwartungen im Q4",
      "subtitle": "Handelsblatt • COMPANIES",
      "description": "Der iPhone-Hersteller konnte im vierten Quartal...",
      "image": "https://example.com/apple-news.jpg",
      "source": "Handelsblatt",
      "category": "COMPANIES",
      "pubDate": "2025-12-15T10:30:00Z",
      "action": {
        "type": "redirect",
        "url": "https://handelsblatt.com/apple-q4-ergebnisse"
      },
      "relevanceScore": 52.0,
      "metadata": {
        "category": "COMPANIES",
        "sourceName": "Handelsblatt"
      }
    }
  ]
}
```

---

## Relevance Scoring

Die Ergebnisse werden nach `relevanceScore` sortiert (höher = relevanter):

### Aktien-Scoring

| Match-Typ                | Score |
| ------------------------ | ----- |
| Exakter Ticker-Match     | +100  |
| ISIN beginnt mit Query   | +90   |
| Ticker beginnt mit Query | +80   |
| Exakter Name-Match       | +70   |
| Name beginnt mit Query   | +50   |
| Name enthält Query       | +30   |

### News-Scoring

| Match-Typ                       | Score |
| ------------------------------- | ----- |
| Exakter Titel-Match             | +80   |
| Titel beginnt mit Query         | +60   |
| Titel enthält Query             | +40   |
| Beschreibung enthält Query      | +20   |
| Aktualitäts-Bonus (max 10 Tage) | +0-10 |

---

## Erweiterung

Die Such-API ist erweiterbar. Aktuell unterstützte Typen:

- `stock` - Aktien aus der stockIndex Collection
- `news` - Nachrichten aus der news Collection

Geplante Erweiterungen:

- `insider_trade` - Insider-Transaktionen
- `company` - Unternehmensdaten

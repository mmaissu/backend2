import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import "./Articles.css";

type HarvestArticle = {
  openalex_id: string;
  title: string;
  authors: string[];
  year?: number | null;
  journal?: string | null;
  doi?: string | null;
  url?: string | null;
  abstract?: string | null;
  cited_by_count?: number | null;
};

type HarvestResponse = {
  query: string;
  count: number;
  results: HarvestArticle[];
};

export default function Articles() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [query, setQuery] = useState(searchParams.get("query") || "");
  const [years, setYears] = useState(Number(searchParams.get("years")) || 2);
  const [articles, setArticles] = useState<HarvestArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [importingId, setImportingId] = useState<string | null>(null);

  useEffect(() => {
    const queryFromUrl = searchParams.get("query");
    const yearsFromUrl = Number(searchParams.get("years")) || 2;

    if (queryFromUrl) {
      setQuery(queryFromUrl);
      setYears(yearsFromUrl);
      handleSearch(queryFromUrl, yearsFromUrl);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = async (queryValue?: string, yearsValue?: number) => {
    const finalQuery = (queryValue ?? query).trim();
    const finalYears = yearsValue ?? years;

    if (!finalQuery) {
      setError("Enter a search topic");
      setArticles([]);
      setHasSearched(false);
      return;
    }

    try {
      setLoading(true);
      setError("");
      setSuccessMessage("");
      setHasSearched(true);

      setSearchParams({
        query: finalQuery,
        years: String(finalYears),
      });

      const response = await fetch(
        `https://backend-n79m.onrender.com/api/harvest?query=${encodeURIComponent(finalQuery)}&years=${finalYears}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch articles");
      }

      const data: HarvestResponse = await response.json();
      setArticles(data.results || []);
    } catch {
      setError("Could not load articles");
      setArticles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (openalexId: string) => {
    try {
      setImportingId(openalexId);
      setError("");
      setSuccessMessage("");

      const response = await fetch("https://backend-n79m.onrender.com/api/harvest/import", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          openalex_id: openalexId,
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.message || "Failed to import article");
      }

      setSuccessMessage(data?.message || "Article imported successfully");
    } catch {
      setError("Import failed");
    } finally {
      setImportingId(null);
    }
  };

  return (
    <div className="articles-page">
      <div className="articles-header">
        <h1>Scientific Article Harvesting</h1>
        <p>Find articles by topic for the last N years</p>
      </div>

      <div className="search-panel">
        <input
          type="text"
          placeholder="For example: artificial intelligence in medicine"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />

        <input
          type="number"
          min={1}
          max={10}
          value={years}
          onChange={(e) => setYears(Number(e.target.value))}
          className="years-input"
        />

        <button onClick={() => handleSearch()} className="search-button">
          Search
        </button>

        <button onClick={() => navigate("/saved")} className="back-button">
          Saved Articles
        </button>
      </div>

      {loading && <p className="status-text">Loading articles...</p>}
      {error && <p className="error-text">{error}</p>}
      {successMessage && <p className="success-text">{successMessage}</p>}

      {!loading && !error && !hasSearched && (
        <p className="status-text">
          No search performed yet. Enter a topic and click Search.
        </p>
      )}

      {!loading && !error && hasSearched && articles.length === 0 && (
        <p className="status-text">No articles found for this query.</p>
      )}

      <div className="results-list">
        {articles.map((article, index) => (
          <div key={index} className="article-card">
            <h3>{article.title}</h3>

            <p>
              <strong>Authors:</strong>{" "}
              {article.authors?.length ? article.authors.join(", ") : "Unknown"}
            </p>

            <p>
              <strong>Year:</strong> {article.year ?? "—"}
            </p>

            <p>
              <strong>Journal:</strong> {article.journal ?? "—"}
            </p>

            <p>
              <strong>DOI:</strong> {article.doi ?? "—"}
            </p>

            <p>
              <strong>Citations:</strong> {article.cited_by_count ?? 0}
            </p>

            <p>
              <strong>URL:</strong>{" "}
              {article.url ? (
                <a href={article.url} target="_blank" rel="noreferrer">
                  Open article
                </a>
              ) : (
                "—"
              )}
            </p>

            <p>
              <strong>Abstract:</strong>{" "}
              {article.abstract
                ? article.abstract.length > 400
                  ? article.abstract.slice(0, 400) + "..."
                  : article.abstract
                : "No abstract available"}
            </p>

            <button
              onClick={() => handleImport(article.openalex_id)}
              className="import-button"
              disabled={importingId === article.openalex_id}
            >
              {importingId === article.openalex_id ? "Importing..." : "Import"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
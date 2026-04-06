import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Articles.css";

type SavedArticle = {
  id: string;
  title: string;
  abstract?: string | null;
  authors?: string[] | null;
  doi?: string | null;
  source?: string | null;
  cited_by_count?: number | null;
};

type Pagination = {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
};

export default function SavedArticles() {
  const [articles, setArticles] = useState<SavedArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [onlyWithDoi, setOnlyWithDoi] = useState(false);
  const [sortBy, setSortBy] = useState("newest");
  const [page, setPage] = useState(1);

  const [pagination, setPagination] = useState<Pagination>({
    page: 1,
    page_size: 6,
    total_items: 0,
    total_pages: 1,
  });

  const navigate = useNavigate();

  useEffect(() => {
    loadArticles();
  }, [page, sortBy, onlyWithDoi]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams({
        page: String(page),
        page_size: "6",
        sort_by: sortBy,
        only_with_doi: String(onlyWithDoi),
      });

      if (search.trim()) {
        params.append("search", search.trim());
      }

      const response = await fetch(`http://127.0.0.1:8000/api/articles?${params.toString()}`);

      if (!response.ok) {
        throw new Error("Failed to fetch saved articles");
      }

      const data = await response.json();

      setArticles(Array.isArray(data.items) ? data.items : []);
      setPagination(
        data.pagination || {
          page: 1,
          page_size: 6,
          total_items: 0,
          total_pages: 1,
        }
      );
    } catch {
      setError("Could not load saved articles");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setPage(1);

    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams({
        page: "1",
        page_size: "6",
        sort_by: sortBy,
        only_with_doi: String(onlyWithDoi),
      });

      if (search.trim()) {
        params.append("search", search.trim());
      }

      const response = await fetch(`http://127.0.0.1:8000/api/articles?${params.toString()}`);

      if (!response.ok) {
        throw new Error("Failed to fetch saved articles");
      }

      const data = await response.json();

      setArticles(Array.isArray(data.items) ? data.items : []);
      setPagination(
        data.pagination || {
          page: 1,
          page_size: 6,
          total_items: 0,
          total_pages: 1,
        }
      );
    } catch {
      setError("Could not load saved articles");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    const confirmed = window.confirm("Delete this article?");
    if (!confirmed) return;

    try {
      setError("");

      const response = await fetch(`http://127.0.0.1:8000/api/articles/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete article");
      }

      await loadArticles();
    } catch {
      setError("Failed to delete article");
    }
  };

  return (
    <div className="articles-page">
      <div className="articles-header">
        <h1>Saved Articles</h1>
        <p>Articles imported into the local database</p>
      </div>

      <div className="search-panel">
        <button onClick={() => navigate("/harvester")} className="back-button">
          ← Back to Articles
        </button>

        <input
          type="text"
          placeholder="Search by title, source or DOI"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />

        <button onClick={handleSearch} className="search-button">
          Search
        </button>

        <select
          value={sortBy}
          onChange={(e) => {
            setSortBy(e.target.value);
            setPage(1);
          }}
          className="sort-select"
        >
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="most_cited">Most cited</option>
          <option value="least_cited">Least cited</option>
          <option value="title_asc">Title A-Z</option>
          <option value="title_desc">Title Z-A</option>
        </select>

        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={onlyWithDoi}
            onChange={(e) => {
              setOnlyWithDoi(e.target.checked);
              setPage(1);
            }}
          />
          Only with DOI
        </label>
      </div>

      {!loading && !error && (
        <p className="status-text">
          Found: {pagination.total_items} article(s)
        </p>
      )}

      {loading && <p className="status-text">Loading saved articles...</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && articles.length === 0 && (
        <div className="empty-state">🔍 Nothing found. Try another search.</div>
      )}

      <div className="results-list">
        {articles.map((article) => (
          <div key={article.id} className="article-card">
            <h3>{article.title}</h3>

            <p>
              <strong>Authors:</strong>{" "}
              {Array.isArray(article.authors) && article.authors.length
                ? article.authors.join(", ")
                : "Unknown"}
            </p>

            <p>
              <strong>Source:</strong> {article.source ?? "—"}
            </p>

            <p>
              <strong>DOI:</strong> {article.doi ?? "—"}
            </p>

            <p>
              <strong>Citations:</strong> {article.cited_by_count ?? 0}
            </p>

            <p>
              <strong>Abstract:</strong>{" "}
              {article.abstract
                ? article.abstract.length > 300
                  ? article.abstract.slice(0, 300) + "..."
                  : article.abstract
                : "No abstract available"}
            </p>

            <button onClick={() => handleDelete(article.id)} className="delete-button">
              Delete
            </button>
          </div>
        ))}
      </div>

      {!loading && !error && pagination.total_pages > 1 && (
        <div className="pagination-bar">
          <button
            className="pagination-button"
            disabled={page <= 1}
            onClick={() => setPage((prev) => prev - 1)}
          >
            Prev
          </button>

          <span className="pagination-text">
            Page {pagination.page} of {pagination.total_pages}
          </span>

          <button
            className="pagination-button"
            disabled={page >= pagination.total_pages}
            onClick={() => setPage((prev) => prev + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
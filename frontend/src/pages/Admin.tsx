import { useEffect, useState } from "react";
import "./Articles.css";

type AdminUser = {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
};

type AdminArticle = {
  id: string;
  title: string;
  authors?: string[] | null;
  doi?: string | null;
  source?: string | null;
  cited_by_count?: number | null;
};

export default function Admin() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [articles, setArticles] = useState<AdminArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const loadAdminData = async () => {
      try {
        setLoading(true);
        setError("");
        setSuccessMessage("");

        const [usersRes, articlesRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/admin/users", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch("http://127.0.0.1:8000/api/admin/articles", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
        ]);

        const usersData = await usersRes.json().catch(() => []);
        const articlesData = await articlesRes.json().catch(() => []);

        if (!usersRes.ok || !articlesRes.ok) {
          throw new Error("Failed to load admin panel");
        }

        setUsers(Array.isArray(usersData) ? usersData : []);
        setArticles(Array.isArray(articlesData) ? articlesData : []);
      } catch {
        setError("Could not load admin panel");
      } finally {
        setLoading(false);
      }
    };

    loadAdminData();
  }, [token]);

  const handleDeleteUser = async (userId: string) => {
    const confirmed = window.confirm("Delete this user?");
    if (!confirmed) return;

    try {
      setError("");
      setSuccessMessage("");

      const response = await fetch(`http://127.0.0.1:8000/api/admin/users/${userId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.detail || "Failed to delete user");
      }

      setUsers((prev) => prev.filter((user) => user.id !== userId));
      setSuccessMessage("User deleted successfully");
    } catch (err: any) {
      setError(err.message || "Could not delete user");
    }
  };

  const handleDeleteArticle = async (articleId: string) => {
    const confirmed = window.confirm("Delete this article?");
    if (!confirmed) return;

    try {
      setError("");
      setSuccessMessage("");

      const response = await fetch(`http://127.0.0.1:8000/api/admin/articles/${articleId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.detail || "Failed to delete article");
      }

      setArticles((prev) => prev.filter((article) => article.id !== articleId));
      setSuccessMessage("Article deleted successfully");
    } catch (err: any) {
      setError(err.message || "Could not delete article");
    }
  };

  if (loading) {
    return (
      <div className="articles-page">
        <p className="status-text">Loading admin panel...</p>
      </div>
    );
  }

  return (
    <div className="articles-page">
      <div className="articles-header">
        <h1>Admin Panel</h1>
        <p>Manage users and saved articles</p>
      </div>

      {error && <p className="error-text">{error}</p>}
      {successMessage && <p className="success-text">{successMessage}</p>}

      <div style={{ marginBottom: "36px" }}>
        <h2 style={{ marginBottom: "16px" }}>Users</h2>

        {users.length === 0 ? (
          <p className="status-text">No users found.</p>
        ) : (
          <div className="users-grid">
            {users.map((user) => (
              <div key={user.id} className="article-card user-card">
                <h3>{user.full_name || "No name"}</h3>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Role:</strong> {user.role}</p>
                <p><strong>Status:</strong> {user.is_active ? "Active" : "Inactive"}</p>

                <button
                  onClick={() => handleDeleteUser(user.id)}
                  className="delete-button"
                >
                  Delete User
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 style={{ marginBottom: "16px" }}>Saved Articles</h2>

        {articles.length === 0 ? (
          <p className="status-text">No articles found.</p>
        ) : (
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
                <p><strong>Source:</strong> {article.source ?? "—"}</p>
                <p><strong>DOI:</strong> {article.doi ?? "—"}</p>
                <p><strong>Citations:</strong> {article.cited_by_count ?? 0}</p>

                <button
                  onClick={() => handleDeleteArticle(article.id)}
                  className="delete-button"
                >
                  Delete Article
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
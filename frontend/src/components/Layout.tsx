import { Link, Outlet, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import "./Layout.css";

type ProfileData = {
  role?: string;
};

export default function Layout() {
  const navigate = useNavigate();
  const [role, setRole] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const response = await fetch("http://127.0.0.1:8000/api/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data: ProfileData = await response.json().catch(() => ({}));

        if (response.ok && data?.role) {
          setRole(String(data.role).toLowerCase());
        }
      } catch {
        //
      }
    };

    loadProfile();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  return (
    <div className="layout-shell">
      <header className="layout-header">
        <div className="layout-brand">
          <Link to="/harvester" className="brand-link">
            Scientific Data Harvester
          </Link>
        </div>

        <nav className="layout-nav">
          <Link to="/harvester" className="nav-link">
            Articles
          </Link>

          <Link to="/saved" className="nav-link">
            Saved
          </Link>

          <Link to="/profile" className="nav-link">
            Профиль
          </Link>

          {role === "admin" && (
            <Link to="/admin" className="nav-link">
              Admin
            </Link>
          )}

          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </nav>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  );
}
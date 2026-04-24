import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Profile.css";

type ProfileData = {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
};

export default function Profile() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        setError("");

        const token = localStorage.getItem("access_token");

        if (!token) {
          navigate("/login");
          return;
        }

        const response = await fetch("https://backend-n79m.onrender.com/api/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          localStorage.removeItem("access_token");
          navigate("/login");
          return;
        }

        if (!response.ok) {
          throw new Error("Failed to load profile");
        }

        const data = await response.json();
        setProfile(data);
      } catch {
        setError("Could not load profile");
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [navigate]);

  if (loading) {
    return (
      <div className="profile-page">
        <p>Loading profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-page">
        <p className="profile-error">{error}</p>
      </div>
    );
  }

  const initials =
    profile?.full_name
      ?.split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

  const articlesCount = 12;
  const recentCount = 3;
  const statusText = profile?.is_active ? "Active" : "Inactive";

  return (
    <div className="profile-page">
      <div className="profile-top">
        <div className="profile-avatar">{initials}</div>

        <h1 className="profile-name">{profile?.full_name || "User"}</h1>
        <p className="profile-email">{profile?.email}</p>

        <p className="profile-bio">
          Researching AI in medicine. Interested in machine learning, scientific
          metadata and data analysis.
        </p>

        <div className="profile-actions">
          <span className="profile-role">
            {String(profile?.role).toLowerCase() === "admin"
              ? "АДМИН"
              : "ИССЛЕДОВАТЕЛЬ"}
          </span>

          <button
            className="edit-profile-button"
            onClick={() => navigate("/profile/edit")}
          >
            Редактировать профиль
          </button>
        </div>
      </div>

      <div className="profile-stats">
        <div className="stat-card">
          <span className="stat-number">{articlesCount}</span>
          <span className="stat-label">Saved Articles</span>
        </div>

        <div className="stat-card">
          <span className="stat-number">{recentCount}</span>
          <span className="stat-label">Recent</span>
        </div>

        <div className="stat-card">
          <span className="stat-number">{statusText}</span>
          <span className="stat-label">Status</span>
        </div>
      </div>

      <div className="activity-card">
        <h3>Recent Activity</h3>
        <p>You saved new scientific articles recently and updated your profile.</p>
      </div>
    </div>
  );
}
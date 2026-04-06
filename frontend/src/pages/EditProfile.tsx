import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./EditProfile.css";

export default function EditProfile() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem("access_token");

      const res = await fetch("http://127.0.0.1:8000/api/profile", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();

      setFullName(data.full_name || "");
      setEmail(data.email || "");
    };

    loadProfile();
  }, []);

  const handleSave = async () => {
    try {
      setLoading(true);
      setMessage("");

      const token = localStorage.getItem("access_token");

      const res = await fetch("http://127.0.0.1:8000/api/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          full_name: fullName,
          password: password || undefined,
        }),
      });

      if (!res.ok) throw new Error();

      setMessage("Профиль обновлен ✅");

      setTimeout(() => {
        navigate("/profile");
      }, 1000);
    } catch {
      setMessage("Ошибка обновления ❌");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="edit-page">
      <div className="edit-card">
        <h1>Редактировать профиль</h1>

        <div className="edit-form">
          <input
            placeholder="Имя"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

          <input
            placeholder="Email"
            value={email}
            disabled
          />

          <input
            type="password"
            placeholder="Новый пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <div className="edit-buttons">
            <button onClick={handleSave} disabled={loading}>
              {loading ? "Сохранение..." : "Сохранить"}
            </button>

            <button
              className="cancel"
              onClick={() => navigate("/profile")}
            >
              Отмена
            </button>
          </div>

          {message && <p className="edit-message">{message}</p>}
        </div>
      </div>
    </div>
  );
}
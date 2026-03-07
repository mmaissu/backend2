import { Link } from 'react-router-dom'
import './Landing.css'

export default function Landing() {
  return (
    <div className="landing">
      <section className="landing-hero">
        <div className="hero-glow" />
        <div className="hero-content">
          <span className="hero-badge">Scientific Data Harvester</span>
          <h1 className="hero-title">
            Собирайте и анализируйте
            <span className="hero-gradient"> метаданные научных публикаций</span>
          </h1>
          <p className="hero-subtitle">
            Единая платформа для хранения статей, DOI, авторов и ключевых слов.
            Поиск, фильтрация и управление вашей научной библиотекой.
          </p>
          <div className="hero-actions">
            <Link to="/register" className="btn-hero btn-primary">Начать бесплатно</Link>
            <Link to="/login" className="btn-hero btn-outline">Войти</Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="hero-card hero-card-1">
            <span className="card-icon">📄</span>
            <span>Статьи</span>
          </div>
          <div className="hero-card hero-card-2">
            <span className="card-icon">🔍</span>
            <span>Поиск</span>
          </div>
          <div className="hero-card hero-card-3">
            <span className="card-icon">📊</span>
            <span>Метаданные</span>
          </div>
        </div>
      </section>

      <section className="landing-about">
        <div className="about-inner">
          <h2>О чём этот сайт</h2>
          <p className="about-lead">
            <strong>Scientific Data Harvester</strong> — это веб-приложение для исследователей,
            студентов и научных сотрудников, которые хотят систематизировать и быстро находить
            информацию о научных публикациях.
          </p>
          <p>
            Загружайте метаданные статей: название, аннотацию, авторов, DOI, источник (журнал или конференцию),
            дату публикации и ключевые слова. Используйте поиск и фильтры, чтобы находить нужные материалы
            за секунды. Роли User и Admin позволяют гибко управлять доступом и редактированием.
          </p>
        </div>
      </section>

      <section className="landing-features">
        <h2>Возможности</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📚</div>
            <h3>База статей</h3>
            <p>Храните метаданные публикаций в одном месте. DOI, авторы, аннотации, ключевые слова.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔎</div>
            <h3>Поиск и фильтры</h3>
            <p>Полнотекстовый поиск по названию и аннотации. Фильтр по источнику, пагинация, сортировка.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔐</div>
            <h3>Безопасность</h3>
            <p>JWT-авторизация, роли User/Admin. Редактировать и удалять может автор или администратор.</p>
          </div>
        </div>
      </section>

      <section className="landing-cta">
        <div className="cta-gradient" />
        <div className="cta-content">
          <h2>Готовы начать?</h2>
          <p>Зарегистрируйтесь и добавьте первую статью за минуту.</p>
          <Link to="/register" className="btn-cta">Регистрация</Link>
        </div>
      </section>
    </div>
  )
}

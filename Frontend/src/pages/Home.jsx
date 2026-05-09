import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Button from '../components/ui/Button';
import './Home.css';

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="home">
      <section className="home-hero">
        <div className="container">
          <div className="home-hero-content">
            <span className="home-badge">AI-Powered Thumbnails</span>
            <h1 className="home-title">
              Thumbnails that<br />
              <span className="home-title-accent">demand attention</span>
            </h1>
            <p className="home-subtitle">
              Generate stunning, CTR-optimized thumbnails with AI. Perfect for YouTube, Instagram, TikTok, and more.
            </p>
            <div className="home-actions">
              {user ? (
                <Button size="lg" onClick={() => navigate('/project/new')}>
                  Create a Thumbnail
                </Button>
              ) : (
                <>
                  <Button size="lg" onClick={() => navigate('/register')}>
                    Get Started Free
                  </Button>
                  <Button variant="secondary" size="lg" onClick={() => navigate('/login')}>
                    Sign In
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="home-bg-shape" />
      </section>

      <section className="home-features">
        <div className="container">
          <h2 className="home-section-title">Built for creators</h2>
          <div className="home-features-grid">
            <div className="home-feature-card">
              <div className="home-feature-icon home-feature-icon--1">AI</div>
              <h3>AI Generation</h3>
              <p>Describe your vision and let Grok AI create stunning thumbnails in seconds.</p>
            </div>
            <div className="home-feature-card">
              <div className="home-feature-icon home-feature-icon--2">S</div>
              <h3>Smart Scoring</h3>
              <p>Get AI-powered CTR predictions and actionable feedback to improve your designs.</p>
            </div>
            <div className="home-feature-card">
              <div className="home-feature-icon home-feature-icon--3">M</div>
              <h3>Multi-Platform</h3>
              <p>Automatically generate variants optimized for YouTube, Shorts, Instagram, and LinkedIn.</p>
            </div>
            <div className="home-feature-card">
              <div className="home-feature-icon home-feature-icon--4">E</div>
              <h3>Prompt Enhancer</h3>
              <p>Not sure what to type? Let our AI enhance your prompts for better results.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="home-styles">
        <div className="container">
          <h2 className="home-section-title">Every style, covered</h2>
          <p className="home-section-desc">
            From YouTube thumbnails to viral shorts — choose from 16 expertly crafted styles.
          </p>
          <div className="home-styles-grid">
            {['YouTube Thumbnail', 'Gaming', 'Tech Review', 'Vlog', 'Tutorial', 'Podcast', 'Shorts', 'Square'].map((s) => (
              <div key={s} className="home-style-chip">{s}</div>
            ))}
          </div>
        </div>
      </section>

      <footer className="home-footer">
        <div className="container">
          <p>ThumbAI — AI thumbnail generation for modern creators</p>
        </div>
      </footer>
    </div>
  );
}

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../ui/Button';
import './Header.css';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-inner container">
        <Link to="/" className="header-logo">
          <span className="header-logo-mark">G</span>
          <span className="header-logo-text">ThumbGenii</span>
        </Link>

        <nav className="header-nav">
          {user ? (
            <>
              <Link to="/dashboard" className="header-link">Projects</Link>
              <Link to="/project/new" className="header-link">New Project</Link>
            </>
          ) : (
            <Link to="/" className="header-link">Home</Link>
          )}
        </nav>

        <div className="header-actions">
          {user ? (
            <div className="header-user">
              <div className="header-credits">
                <span className="header-credits-dot" />
                {user.credits_remaining} credits
              </div>
              <Link to="/profile" className="header-avatar">
                {user.name?.[0] || user.email[0]}
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout}>Logout</Button>
            </div>
          ) : (
            <div className="header-auth">
              <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>Log in</Button>
              <Button size="sm" onClick={() => navigate('/register')}>Sign up</Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { getStats, getPreferences, updatePreferences, changePassword } from '../services/users';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import './Profile.css';

export default function Profile() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [prefs, setPrefs] = useState(null);
  const [passwordForm, setPasswordForm] = useState({ current: '', newPass: '' });
  const [pwMsg, setPwMsg] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getStats(), getPreferences()])
      .then(([s, p]) => {
        setStats(s);
        setPrefs(p);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handlePrefToggle = async (key, value) => {
    const updated = { ...prefs, [key]: value };
    setPrefs(updated);
    try { await updatePreferences({ [key]: value }); } catch {}
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPwMsg('');
    try {
      await changePassword(passwordForm.current, passwordForm.newPass);
      setPwMsg('Password changed successfully');
      setPasswordForm({ current: '', newPass: '' });
    } catch (err) {
      setPwMsg(err.response?.data?.message || 'Failed to change password');
    }
  };

  if (loading) return <div className="profile-loading container">Loading...</div>;

  return (
    <div className="profile container">
      <h2>Profile & Settings</h2>

      <div className="profile-grid">
        <Card className="profile-section">
          <h4>Account</h4>
          <div className="profile-info">
            <div className="profile-avatar-lg">{user?.name?.[0] || user?.email[0]}</div>
            <div>
              <p className="profile-name">{user?.name || 'User'}</p>
              <p className="profile-email">{user?.email}</p>
              <p className="profile-plan">Plan: <strong>{user?.plan}</strong></p>
            </div>
          </div>
        </Card>

        {stats && (
          <Card className="profile-section">
            <h4>Usage</h4>
            <div className="profile-stats">
              <div className="profile-stat">
                <span className="profile-stat-value">{stats.credits_remaining}</span>
                <span className="profile-stat-label">Credits left</span>
              </div>
              <div className="profile-stat">
                <span className="profile-stat-value">{stats.generations_this_month}</span>
                <span className="profile-stat-label">This month</span>
              </div>
              <div className="profile-stat">
                <span className="profile-stat-value">{stats.generations_today}</span>
                <span className="profile-stat-label">Today</span>
              </div>
            </div>
          </Card>
        )}

        {prefs && (
          <Card className="profile-section">
            <h4>Preferences</h4>
            <div className="profile-prefs">
              <label className="profile-toggle">
                <span>Dark Mode</span>
                <input type="checkbox" checked={prefs.dark_mode} onChange={(e) => handlePrefToggle('dark_mode', e.target.checked)} />
                <span className="profile-toggle-slider" />
              </label>
              <label className="profile-toggle">
                <span>Email Notifications</span>
                <input type="checkbox" checked={prefs.email_notifications} onChange={(e) => handlePrefToggle('email_notifications', e.target.checked)} />
                <span className="profile-toggle-slider" />
              </label>
            </div>
          </Card>
        )}

        <Card className="profile-section">
          <h4>Change Password</h4>
          {pwMsg && <div className={`profile-pw-msg ${pwMsg.includes('success') ? 'profile-pw-msg--ok' : ''}`}>{pwMsg}</div>}
          <form onSubmit={handlePasswordChange} className="profile-pw-form">
            <Input type="password" label="Current Password" value={passwordForm.current} onChange={(e) => setPasswordForm({ ...passwordForm, current: e.target.value })} required />
            <Input type="password" label="New Password" value={passwordForm.newPass} onChange={(e) => setPasswordForm({ ...passwordForm, newPass: e.target.value })} required minLength={8} />
            <Button type="submit" size="sm">Update Password</Button>
          </form>
        </Card>
      </div>
    </div>
  );
}

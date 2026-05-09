import './Input.css';

export default function Input({ label, error, icon, className = '', ...props }) {
  return (
    <div className={`input-group ${className}`}>
      {label && <label className="input-label">{label}</label>}
      <div className="input-wrap">
        {icon && <span className="input-icon">{icon}</span>}
        <input className={`input-field ${icon ? 'input-field--with-icon' : ''}`} {...props} />
      </div>
      {error && <span className="input-error">{error}</span>}
    </div>
  );
}

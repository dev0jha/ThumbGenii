import './Button.css';

export default function Button({ children, variant = 'primary', size = 'md', fullWidth, loading, disabled, className = '', ...props }) {
  const cls = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    fullWidth ? 'btn--full' : '',
    loading ? 'btn--loading' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button className={cls} disabled={disabled || loading} {...props}>
      {loading ? <span className="btn__spinner" /> : children}
    </button>
  );
}

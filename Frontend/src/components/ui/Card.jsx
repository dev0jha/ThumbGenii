import './Card.css';

export default function Card({ children, className = '', padding = 'lg', hover, onClick, ...props }) {
  const cls = [
    'card',
    `card--pad-${padding}`,
    hover ? 'card--hover' : '',
    onClick ? 'card--clickable' : '',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={cls} onClick={onClick} role={onClick ? 'button' : undefined} tabIndex={onClick ? 0 : undefined} onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined} {...props}>
      {children}
    </div>
  );
}

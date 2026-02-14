function timeAgo(ts) {
    const s = Math.floor((Date.now() - ts) / 1000);
    if (s < 60) return 'just now';
    if (s < 3600) return `${Math.floor(s / 60)}m ago`;
    return `${Math.floor(s / 3600)}h ago`;
}

export default function QueryHistory({ history, onSelect }) {
    return (
        <div>
            {history.map((h, i) => (
                <div className="history-item" key={i} onClick={() => onSelect(h.query)}>
                    <div className="history-query" title={h.query}>{h.query}</div>
                    <div className="history-time">⏱ {timeAgo(h.time)}</div>
                </div>
            ))}
            {!history.length && (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: 24, textAlign: 'center' }}>
                    <p style={{ fontSize: '1.5rem', marginBottom: 8 }}>🕐</p>
                    <p>Queries will appear here</p>
                </div>
            )}
        </div>
    );
}

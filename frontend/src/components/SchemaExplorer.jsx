export default function SchemaExplorer({ tables, tableDetails, onToggle, expanded }) {
    return (
        <div>
            {tables.map(t => (
                <div className="schema-table" key={t.table_name}>
                    <div className="schema-table-header" onClick={() => onToggle(t.table_name)}>
                        <span>
                            <span style={{ display: 'inline-block', width: 16, textAlign: 'center' }}>
                                {expanded[t.table_name] ? '▾' : '▸'}
                            </span>{' '}
                            🗃️ {t.table_name}
                        </span>
                        <span className="badge">{t.row_count} rows</span>
                    </div>
                    {expanded[t.table_name] && tableDetails[t.table_name] && (
                        <div className="schema-columns">
                            {tableDetails[t.table_name].map((c, i) => (
                                <div className="schema-column" key={i}>
                                    {c.name.endsWith('_id') && c.name === `${t.table_name.replace(/s$/, '')}_id`
                                        ? <span className="col-key">🔑</span>
                                        : c.name.endsWith('_id')
                                            ? <span className="col-key">🔗</span>
                                            : <span style={{ width: 16, display: 'inline-block' }}>·</span>
                                    }
                                    <span className="col-name">{c.name}</span>
                                    <span className="col-type">{c.type}</span>
                                    {c.nullable && <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>null</span>}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            ))}
            {!tables.length && (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: 24, textAlign: 'center' }}>
                    <p style={{ fontSize: '1.5rem', marginBottom: 8 }}>📋</p>
                    <p>Connect to database to explore schema</p>
                </div>
            )}
        </div>
    );
}

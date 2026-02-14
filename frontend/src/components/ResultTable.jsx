import { useState, useMemo } from 'react';

function exportCSV(columns, data) {
    const header = columns.join(',');
    const rows = data.map(r =>
        r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')
    );
    const blob = new Blob([header + '\n' + rows.join('\n')], { type: 'text/csv' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `query_results_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
}

export default function ResultTable({ result }) {
    const [sortCol, setSortCol] = useState(null);
    const [sortDir, setSortDir] = useState('asc');
    const [page, setPage] = useState(0);
    const perPage = 15;

    if (!result?.success || !result.data?.length) return null;

    const toggleSort = (colIdx) => {
        if (sortCol === colIdx) {
            setSortDir(d => (d === 'asc' ? 'desc' : 'asc'));
        } else {
            setSortCol(colIdx);
            setSortDir('asc');
        }
        setPage(0);
    };

    const sortedData = useMemo(() => {
        if (sortCol === null) return result.data;
        return [...result.data].sort((a, b) => {
            const va = a[sortCol];
            const vb = b[sortCol];
            if (va == null && vb == null) return 0;
            if (va == null) return 1;
            if (vb == null) return -1;
            const na = Number(va), nb = Number(vb);
            if (!isNaN(na) && !isNaN(nb)) {
                return sortDir === 'asc' ? na - nb : nb - na;
            }
            const sa = String(va), sb = String(vb);
            return sortDir === 'asc' ? sa.localeCompare(sb) : sb.localeCompare(sa);
        });
    }, [result.data, sortCol, sortDir]);

    const totalPages = Math.ceil(sortedData.length / perPage);
    const pageData = sortedData.slice(page * perPage, (page + 1) * perPage);

    return (
        <div className="result-block">
            <div className="result-header">
                <span>📊 Results</span>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <span className="row-count">
                        {result.row_count} row{result.row_count !== 1 ? 's' : ''}
                    </span>
                    <button
                        className="export-btn"
                        onClick={() => exportCSV(result.columns, result.data)}
                    >
                        📥 Export CSV
                    </button>
                </div>
            </div>
            <div className="result-table-wrapper">
                <table className="result-table">
                    <thead>
                        <tr>
                            {result.columns.map((c, i) => (
                                <th
                                    key={i}
                                    onClick={() => toggleSort(i)}
                                    style={{ cursor: 'pointer', userSelect: 'none' }}
                                >
                                    {c}
                                    {sortCol === i && (
                                        <span style={{ marginLeft: 4, opacity: 0.7 }}>
                                            {sortDir === 'asc' ? '▲' : '▼'}
                                        </span>
                                    )}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {pageData.map((row, ri) => (
                            <tr key={ri}>
                                {row.map((v, ci) => (
                                    <td key={ci} title={v != null ? String(v) : ''}>
                                        {v ?? '—'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {totalPages > 1 && (
                <div className="result-pagination">
                    <button
                        disabled={page === 0}
                        onClick={() => setPage(p => p - 1)}
                    >
                        ← Prev
                    </button>
                    <span>
                        Page {page + 1} of {totalPages}
                    </span>
                    <button
                        disabled={page >= totalPages - 1}
                        onClick={() => setPage(p => p + 1)}
                    >
                        Next →
                    </button>
                </div>
            )}
        </div>
    );
}

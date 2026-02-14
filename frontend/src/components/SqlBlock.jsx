import { useState } from 'react';

export default function SqlBlock({ sql }) {
    const [copied, setCopied] = useState(false);

    const copy = () => {
        navigator.clipboard.writeText(sql);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
    };

    // Basic SQL keyword highlighting
    const highlighted = sql.replace(
        /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|AS|ORDER BY|GROUP BY|HAVING|LIMIT|OFFSET|COUNT|SUM|AVG|MAX|MIN|DISTINCT|BETWEEN|LIKE|IS|NULL|DESC|ASC|WITH|CASE|WHEN|THEN|ELSE|END|UNION|INSERT|UPDATE|DELETE|CREATE|TABLE|INDEX|INTO|VALUES|SET)\b/gi,
        '<span class="sql-keyword">$1</span>'
    );

    return (
        <div className="sql-block">
            <div className="sql-header">
                <span>🔍 SQL Query</span>
                <button className="copy-btn" onClick={copy}>
                    {copied ? '✓ Copied!' : '📋 Copy'}
                </button>
            </div>
            <pre
                className="sql-code"
                dangerouslySetInnerHTML={{ __html: highlighted }}
            />
        </div>
    );
}

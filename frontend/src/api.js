const API = '/api';

export async function sendMessage(message, sessionId) {
    const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

export async function executeSQL(query) {
    const res = await fetch(`${API}/database/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

export async function getTables() {
    const res = await fetch(`${API}/database/tables`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

export async function getTableInfo(name) {
    const res = await fetch(`${API}/database/tables/${name}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

export async function testConnection() {
    const res = await fetch(`${API}/database/test`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

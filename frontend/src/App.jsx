import { useState, useEffect, useRef } from 'react';
import { sendMessage, executeSQL, getTables, getTableInfo, testConnection } from './api';
import SqlBlock from './components/SqlBlock';
import ResultTable from './components/ResultTable';
import SchemaExplorer from './components/SchemaExplorer';
import QueryHistory from './components/QueryHistory';

// ─── Message Bubble ───────────────────────────────────

function Message({ msg }) {
    return (
        <div className={`message ${msg.role}`}>
            <div className="message-avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
            <div className="message-body">
                <div className="message-content">{msg.content}</div>
                {msg.sql_query && <SqlBlock sql={msg.sql_query} />}
                {msg.sql_result && <ResultTable result={msg.sql_result} />}
            </div>
        </div>
    );
}

// ─── Welcome Screen ───────────────────────────────────

const SUGGESTIONS = [
    "How many customers do we have?",
    "Show top 5 customers by income",
    "What's the total balance across all accounts?",
    "List all active loans with their amounts",
    "Show recent transactions over $1000",
    "Which branch has the most customers?",
];

function WelcomeScreen({ onSelect }) {
    return (
        <div className="welcome-screen">
            <div className="welcome-icon">⚡</div>
            <h2>Warehouse SQL Assistant</h2>
            <p>Ask questions about your banking data in natural language, or write SQL directly. I'll generate queries and show results instantly.</p>
            <div className="quick-actions">
                {SUGGESTIONS.map((s, i) => (
                    <button key={i} className="quick-action" onClick={() => onSelect(s)}>
                        {s}
                    </button>
                ))}
            </div>
        </div>
    );
}

// ─── Loading Indicator ────────────────────────────────

function LoadingMessage() {
    return (
        <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-body">
                <div className="message-content">
                    <div className="loading-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ─── Main App ─────────────────────────────────────────

export default function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [mode, setMode] = useState('chat');
    const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');
    const [sidebarTab, setSidebarTab] = useState('schema');
    const [tables, setTables] = useState([]);
    const [tableDetails, setTableDetails] = useState({});
    const [expanded, setExpanded] = useState({});
    const [history, setHistory] = useState([]);
    const [dbStatus, setDbStatus] = useState(null);
    const endRef = useRef(null);
    const inputRef = useRef(null);

    // Theme
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    // Auto-scroll
    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    // Load tables on mount
    useEffect(() => {
        getTables()
            .then(r => { if (r.success) setTables(r.tables); })
            .catch(() => { });
        testConnection()
            .then(r => setDbStatus(r.success))
            .catch(() => setDbStatus(false));
    }, []);

    const toggleTable = async (name) => {
        setExpanded(prev => ({ ...prev, [name]: !prev[name] }));
        if (!tableDetails[name]) {
            try {
                const info = await getTableInfo(name);
                if (info.success) {
                    setTableDetails(prev => ({ ...prev, [name]: info.columns }));
                }
            } catch { }
        }
    };

    const handleSend = async () => {
        const text = input.trim();
        if (!text || loading) return;
        setInput('');

        if (mode === 'sql') {
            setMessages(prev => [...prev, { role: 'user', content: text }]);
            setLoading(true);
            try {
                const result = await executeSQL(text);
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: result.success
                        ? `Query executed successfully — ${result.row_count} row${result.row_count !== 1 ? 's' : ''} returned.`
                        : `Error: ${result.error}`,
                    sql_query: result.query || text,
                    sql_result: result,
                }]);
                setHistory(prev => [{ query: text, time: Date.now() }, ...prev].slice(0, 50));
            } catch (e) {
                setMessages(prev => [...prev, { role: 'assistant', content: `Connection error: ${e.message}` }]);
            }
            setLoading(false);
            return;
        }

        // Chat mode — RAG pipeline
        setMessages(prev => [...prev, { role: 'user', content: text }]);
        setLoading(true);
        try {
            const data = await sendMessage(text, sessionId);
            if (!sessionId && data.session_id) setSessionId(data.session_id);
            const msg = data.message;
            setMessages(prev => [...prev, msg]);
            if (msg.sql_query) {
                setHistory(prev => [{ query: msg.sql_query, time: Date.now() }, ...prev].slice(0, 50));
            }
        } catch (e) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Connection error: ${e.message}. Make sure the backend is running on port 5000.`,
            }]);
        }
        setLoading(false);
    };

    const onKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const selectSuggestion = (text) => {
        setInput(text);
        inputRef.current?.focus();
    };

    const selectHistoryQuery = (query) => {
        setInput(query);
        setMode('sql');
        inputRef.current?.focus();
    };

    const clearChat = () => {
        setMessages([]);
        setSessionId(null);
    };

    return (
        <div className="app-container">
            {/* ─── Header ─── */}
            <header className="app-header">
                <div className="logo">
                    <div className="logo-icon">⚡</div>
                    Warehouse SQL Assistant
                </div>
                <div className="header-actions">
                    <div className={`status-badge ${dbStatus ? 'connected' : 'disconnected'}`}>
                        <span
                            style={{
                                width: 6, height: 6, borderRadius: '50%', display: 'inline-block',
                                background: dbStatus ? 'var(--success)' : 'var(--error)',
                            }}
                        />
                        {dbStatus ? 'Connected' : 'Disconnected'}
                    </div>
                    {messages.length > 0 && (
                        <button className="icon-btn" onClick={clearChat} title="New chat">
                            🗑️
                        </button>
                    )}
                    <button
                        className="icon-btn"
                        onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
                        title="Toggle theme"
                    >
                        {theme === 'dark' ? '☀️' : '🌙'}
                    </button>
                </div>
            </header>

            {/* ─── Main ─── */}
            <div className="app-main">
                {/* Sidebar */}
                <aside className="sidebar">
                    <div className="sidebar-header">
                        <div className="sidebar-tabs">
                            <button
                                className={`sidebar-tab ${sidebarTab === 'schema' ? 'active' : ''}`}
                                onClick={() => setSidebarTab('schema')}
                            >
                                📋 Schema
                            </button>
                            <button
                                className={`sidebar-tab ${sidebarTab === 'history' ? 'active' : ''}`}
                                onClick={() => setSidebarTab('history')}
                            >
                                🕐 History
                                {history.length > 0 && (
                                    <span style={{ marginLeft: 6, fontSize: '0.7rem', opacity: 0.7 }}>
                                        ({history.length})
                                    </span>
                                )}
                            </button>
                        </div>
                    </div>
                    <div className="sidebar-content">
                        {sidebarTab === 'schema' ? (
                            <SchemaExplorer
                                tables={tables}
                                tableDetails={tableDetails}
                                onToggle={toggleTable}
                                expanded={expanded}
                            />
                        ) : (
                            <QueryHistory history={history} onSelect={selectHistoryQuery} />
                        )}
                    </div>
                </aside>

                {/* Chat Area */}
                <main className="chat-area">
                    <div className="messages-container">
                        {messages.length === 0 ? (
                            <WelcomeScreen onSelect={selectSuggestion} />
                        ) : (
                            messages.map((msg, i) => <Message key={i} msg={msg} />)
                        )}
                        {loading && <LoadingMessage />}
                        <div ref={endRef} />
                    </div>

                    {/* Input */}
                    <div className="input-area">
                        <div style={{ maxWidth: 820, margin: '0 auto' }}>
                            <div className="mode-toggle">
                                <button
                                    className={`mode-btn ${mode === 'chat' ? 'active' : ''}`}
                                    onClick={() => setMode('chat')}
                                >
                                    💬 Chat
                                </button>
                                <button
                                    className={`mode-btn ${mode === 'sql' ? 'active' : ''}`}
                                    onClick={() => setMode('sql')}
                                >
                                    ⌨️ SQL
                                </button>
                            </div>
                            <div className="input-container">
                                <div className="input-wrapper">
                                    <input
                                        ref={inputRef}
                                        className="chat-input"
                                        value={input}
                                        onChange={e => setInput(e.target.value)}
                                        onKeyDown={onKeyDown}
                                        placeholder={
                                            mode === 'chat'
                                                ? 'Ask about your banking data...'
                                                : 'Write a SELECT query...'
                                        }
                                        disabled={loading}
                                        autoFocus
                                    />
                                </div>
                                <button
                                    className="send-btn"
                                    onClick={handleSend}
                                    disabled={loading || !input.trim()}
                                >
                                    {loading ? '⏳' : '🚀'} Send
                                </button>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

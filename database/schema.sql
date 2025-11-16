CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    event_date TEXT NOT NULL,  -- Changed from DATE to TEXT
    event_time TEXT,            -- Changed from TIME to TEXT
    location VARCHAR(500),
    url VARCHAR(1000) UNIQUE,
    description TEXT,
    category VARCHAR(50),
    source VARCHAR(100),
    price VARCHAR(100),
    is_virtual INTEGER DEFAULT 0,  -- 0 = in-person, 1 = virtual/online
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(title, event_date)
);

CREATE INDEX IF NOT EXISTS idx_event_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_source ON events(source);
-- ideas 테이블 생성
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id_a INTEGER NOT NULL,
    book_id_b INTEGER NOT NULL,
    connection_point TEXT NOT NULL,
    new_idea TEXT NOT NULL,
    why_it_works TEXT,
    example TEXT,
    user_context TEXT,
    distance REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id_a) REFERENCES books(id),
    FOREIGN KEY (book_id_b) REFERENCES books(id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_ideas_book_a ON ideas(book_id_a);
CREATE INDEX IF NOT EXISTS idx_ideas_book_b ON ideas(book_id_b);
CREATE INDEX IF NOT EXISTS idx_ideas_created_at ON ideas(created_at DESC);

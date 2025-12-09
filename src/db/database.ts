import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

// SQLite 데이터베이스 연결
const dbPath = join(process.cwd(), 'knowledge-debt.db');
const db = new Database(dbPath, { verbose: console.log });

// 외래 키 제약 조건 활성화
db.pragma('foreign_keys = ON');

// 데이터베이스 초기화
export function initDatabase() {
  try {
    // ESM 환경에서 __dirname 대체
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);
    const schemaPath = join(__dirname, 'schema.sql');
    const schema = readFileSync(schemaPath, 'utf-8');
    
    // 스키마 실행
    db.exec(schema);
    
    console.log('✅ Database initialized successfully!');
  } catch (error) {
    console.error('❌ Failed to initialize database:', error);
    throw error;
  }
}

// ============================================
// Book 관련 타입 정의
// ============================================

export interface Book {
  id?: number;
  title: string;
  author: string;
  purchase_date?: string;
  genre?: string;
  cover_image_url?: string;
  page_count: number;
  created_at?: string;
  updated_at?: string;
}

export interface DebtLedger {
  id?: number;
  book_id: number;
  initial_debt_points: number;
  current_remaining_points: number;
  status: 'debt' | 'partial' | 'asset';
  accumulated_mileage: number;
  created_at?: string;
  updated_at?: string;
}

export interface Activity {
  id?: number;
  book_id: number;
  activity_type: string;
  reduction_points: number;
  content?: string;
  activity_date?: string;
  created_at?: string;
}

export interface Highlight {
  id?: number;
  book_id: number;
  original_text: string;
  page_number?: number;
  my_thoughts?: string;
  created_at?: string;
  updated_at?: string;
}

export interface BookWithDebt extends Book {
  initial_debt_points: number;
  current_remaining_points: number;
  accumulated_mileage: number;
  status: 'debt' | 'partial' | 'asset';
  progress_percentage: number;
  total_activities: number;
  total_highlights: number;
}

export interface DashboardStats {
  total_books: number;
  debt_books: number;
  partial_books: number;
  asset_books: number;
  total_initial_debt: number;
  total_remaining_debt: number;
  total_mileage: number;
  overall_progress: number;
}

// ============================================
// Books 쿼리
// ============================================

export const bookQueries = {
  // 모든 책 가져오기 (부채 정보 포함)
  getAll: () => {
    const stmt = db.prepare('SELECT * FROM v_books_with_debt ORDER BY created_at DESC');
    return stmt.all() as BookWithDebt[];
  },

  // ID로 책 가져오기
  getById: (id: number) => {
    const stmt = db.prepare('SELECT * FROM v_books_with_debt WHERE id = ?');
    return stmt.get(id) as BookWithDebt | undefined;
  },

  // 상태별 책 가져오기
  getByStatus: (status: 'debt' | 'partial' | 'asset') => {
    const stmt = db.prepare('SELECT * FROM v_books_with_debt WHERE status = ? ORDER BY updated_at DESC');
    return stmt.all(status) as BookWithDebt[];
  },

  // 장르별 책 가져오기
  getByGenre: (genre: string) => {
    const stmt = db.prepare('SELECT * FROM v_books_with_debt WHERE genre = ? ORDER BY created_at DESC');
    return stmt.all(genre) as BookWithDebt[];
  },

  // 새 책 추가 (자동으로 debt_ledger 생성됨 - 트리거)
  create: (book: Omit<Book, 'id' | 'created_at' | 'updated_at'>) => {
    const stmt = db.prepare(`
      INSERT INTO books (title, author, purchase_date, genre, cover_image_url, page_count)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      book.title,
      book.author,
      book.purchase_date || new Date().toISOString().split('T')[0],
      book.genre || null,
      book.cover_image_url || null,
      book.page_count
    );
    return result.lastInsertRowid;
  },

  // 책 업데이트
  update: (id: number, book: Partial<Book>) => {
    const fields = [];
    const values = [];
    
    if (book.title !== undefined) {
      fields.push('title = ?');
      values.push(book.title);
    }
    if (book.author !== undefined) {
      fields.push('author = ?');
      values.push(book.author);
    }
    if (book.genre !== undefined) {
      fields.push('genre = ?');
      values.push(book.genre);
    }
    if (book.cover_image_url !== undefined) {
      fields.push('cover_image_url = ?');
      values.push(book.cover_image_url);
    }
    if (book.page_count !== undefined) {
      fields.push('page_count = ?');
      values.push(book.page_count);
    }
    
    if (fields.length === 0) return;
    
    fields.push('updated_at = CURRENT_TIMESTAMP');
    values.push(id);
    
    const stmt = db.prepare(`UPDATE books SET ${fields.join(', ')} WHERE id = ?`);
    return stmt.run(...values);
  },

  // 책 삭제
  delete: (id: number) => {
    const stmt = db.prepare('DELETE FROM books WHERE id = ?');
    return stmt.run(id);
  },
};

// ============================================
// Activities 쿼리
// ============================================

export const activityQueries = {
  // 책의 모든 활동 가져오기
  getByBookId: (bookId: number) => {
    const stmt = db.prepare('SELECT * FROM activities WHERE book_id = ? ORDER BY created_at DESC');
    return stmt.all(bookId) as Activity[];
  },

  // 최근 활동 가져오기
  getRecent: (limit: number = 10) => {
    const stmt = db.prepare('SELECT * FROM v_recent_activities LIMIT ?');
    return stmt.all(limit);
  },

  // 활동 추가 (자동으로 debt_ledger 업데이트됨 - 트리거)
  create: (activity: Omit<Activity, 'id' | 'created_at'>) => {
    const stmt = db.prepare(`
      INSERT INTO activities (book_id, activity_type, reduction_points, content, activity_date)
      VALUES (?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      activity.book_id,
      activity.activity_type,
      activity.reduction_points,
      activity.content || null,
      activity.activity_date || new Date().toISOString().split('T')[0]
    );
    return result.lastInsertRowid;
  },

  // 활동 삭제
  delete: (id: number) => {
    const stmt = db.prepare('DELETE FROM activities WHERE id = ?');
    return stmt.run(id);
  },
};

// ============================================
// Highlights 쿼리
// ============================================

export const highlightQueries = {
  // 책의 모든 하이라이트 가져오기
  getByBookId: (bookId: number) => {
    const stmt = db.prepare('SELECT * FROM highlights WHERE book_id = ? ORDER BY page_number, created_at');
    return stmt.all(bookId) as Highlight[];
  },

  // 하이라이트 추가 (자동으로 activity 생성 + 포인트 차감 - 트리거)
  create: (highlight: Omit<Highlight, 'id' | 'created_at' | 'updated_at'>) => {
    const stmt = db.prepare(`
      INSERT INTO highlights (book_id, original_text, page_number, my_thoughts)
      VALUES (?, ?, ?, ?)
    `);
    const result = stmt.run(
      highlight.book_id,
      highlight.original_text,
      highlight.page_number || null,
      highlight.my_thoughts || null
    );
    return result.lastInsertRowid;
  },

  // 하이라이트 업데이트
  update: (id: number, highlight: Partial<Highlight>) => {
    const fields = [];
    const values = [];
    
    if (highlight.original_text !== undefined) {
      fields.push('original_text = ?');
      values.push(highlight.original_text);
    }
    if (highlight.page_number !== undefined) {
      fields.push('page_number = ?');
      values.push(highlight.page_number);
    }
    if (highlight.my_thoughts !== undefined) {
      fields.push('my_thoughts = ?');
      values.push(highlight.my_thoughts);
    }
    
    if (fields.length === 0) return;
    
    fields.push('updated_at = CURRENT_TIMESTAMP');
    values.push(id);
    
    const stmt = db.prepare(`UPDATE highlights SET ${fields.join(', ')} WHERE id = ?`);
    return stmt.run(...values);
  },

  // 하이라이트 삭제
  delete: (id: number) => {
    const stmt = db.prepare('DELETE FROM highlights WHERE id = ?');
    return stmt.run(id);
  },
};

// ============================================
// Dashboard 쿼리
// ============================================

export const dashboardQueries = {
  // 통계 정보 가져오기
  getStats: () => {
    const stmt = db.prepare('SELECT * FROM v_dashboard_stats');
    return stmt.get() as DashboardStats;
  },

  // 전체 마일리지 합계
  getTotalMileage: () => {
    const stmt = db.prepare('SELECT SUM(accumulated_mileage) as total FROM debt_ledger');
    const result = stmt.get() as { total: number };
    return result.total || 0;
  },
};

// 데이터베이스 연결 종료
export function closeDatabase() {
  db.close();
  console.log('✅ Database connection closed.');
}

export default db;

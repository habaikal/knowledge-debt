-- ============================================
-- 지식 부채 관리 시스템 (Knowledge Debt System)
-- ============================================

-- 1. 책 정보 테이블
CREATE TABLE IF NOT EXISTS books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  author TEXT NOT NULL,
  purchase_date DATE NOT NULL DEFAULT CURRENT_DATE,
  genre TEXT,
  cover_image_url TEXT,
  page_count INTEGER NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 부채 장부 테이블
CREATE TABLE IF NOT EXISTS debt_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL UNIQUE,
  initial_debt_points INTEGER NOT NULL,
  current_remaining_points INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'debt' CHECK(status IN ('debt', 'partial', 'asset')),
  accumulated_mileage INTEGER DEFAULT 0, -- 순자산 (0 미만으로 내려갈 때 누적)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 3. 탕감 활동 기록 테이블
CREATE TABLE IF NOT EXISTS activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL,
  activity_type TEXT NOT NULL, -- 'highlight', 'review', 'summary', 'share', 'reread', etc.
  reduction_points INTEGER NOT NULL DEFAULT 0, -- 탕감 포인트 (음수로 저장)
  content TEXT,
  activity_date DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 4. 하이라이트/메모 테이블
CREATE TABLE IF NOT EXISTS highlights (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL,
  original_text TEXT NOT NULL,
  page_number INTEGER,
  my_thoughts TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- ============================================
-- 트리거 설정
-- ============================================

-- 트리거 1: 책 추가 시 자동으로 부채 장부 생성
-- 초기 부채 = 300pt + (페이지수 × 0.5pt)
CREATE TRIGGER IF NOT EXISTS create_debt_on_book_insert
AFTER INSERT ON books
BEGIN
  INSERT INTO debt_ledger (book_id, initial_debt_points, current_remaining_points)
  VALUES (
    NEW.id,
    300 + (NEW.page_count * 0.5),
    300 + (NEW.page_count * 0.5)
  );
END;

-- 트리거 2: 하이라이트 추가 시 자동으로 활동 기록 + 20pt 탕감
CREATE TRIGGER IF NOT EXISTS create_activity_on_highlight
AFTER INSERT ON highlights
BEGIN
  -- activities 테이블에 기록
  INSERT INTO activities (book_id, activity_type, reduction_points, content)
  VALUES (NEW.book_id, 'highlight', -20, '하이라이트 추가: ' || substr(NEW.original_text, 1, 50));
  
  -- debt_ledger에서 포인트 차감
  UPDATE debt_ledger
  SET current_remaining_points = current_remaining_points - 20,
      updated_at = CURRENT_TIMESTAMP
  WHERE book_id = NEW.book_id;
END;

-- 트리거 3: 활동 추가 시 부채 포인트 업데이트
CREATE TRIGGER IF NOT EXISTS update_debt_on_activity
AFTER INSERT ON activities
WHEN NEW.activity_type != 'highlight' -- highlight는 별도 트리거에서 처리
BEGIN
  UPDATE debt_ledger
  SET current_remaining_points = current_remaining_points + NEW.reduction_points,
      updated_at = CURRENT_TIMESTAMP
  WHERE book_id = NEW.book_id;
END;

-- 트리거 4: 부채 포인트 변경 시 상태 자동 업데이트
CREATE TRIGGER IF NOT EXISTS update_status_on_debt_change
AFTER UPDATE OF current_remaining_points ON debt_ledger
BEGIN
  UPDATE debt_ledger
  SET 
    status = CASE
      WHEN NEW.current_remaining_points <= 0 THEN 'asset'
      WHEN NEW.current_remaining_points <= (NEW.initial_debt_points * 0.5) THEN 'partial'
      ELSE 'debt'
    END,
    -- 0 미만일 경우 순자산(마일리지)으로 누적
    accumulated_mileage = CASE
      WHEN NEW.current_remaining_points < 0 THEN accumulated_mileage + ABS(NEW.current_remaining_points)
      ELSE accumulated_mileage
    END,
    -- 마일리지로 전환된 포인트는 0으로 설정
    current_remaining_points = CASE
      WHEN NEW.current_remaining_points < 0 THEN 0
      ELSE NEW.current_remaining_points
    END,
    updated_at = CURRENT_TIMESTAMP
  WHERE id = NEW.id;
END;

-- ============================================
-- 인덱스 생성 (성능 최적화)
-- ============================================

CREATE INDEX IF NOT EXISTS idx_books_purchase_date ON books(purchase_date);
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_debt_ledger_status ON debt_ledger(status);
CREATE INDEX IF NOT EXISTS idx_activities_book_id ON activities(book_id);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(activity_date);
CREATE INDEX IF NOT EXISTS idx_highlights_book_id ON highlights(book_id);

-- ============================================
-- 뷰 생성 (자주 사용하는 쿼리)
-- ============================================

-- 책 상세 정보 (부채 정보 포함)
CREATE VIEW IF NOT EXISTS v_books_with_debt AS
SELECT 
  b.id,
  b.title,
  b.author,
  b.purchase_date,
  b.genre,
  b.cover_image_url,
  b.page_count,
  d.initial_debt_points,
  d.current_remaining_points,
  d.accumulated_mileage,
  d.status,
  -- 진행률 계산 (초기 부채 대비 탕감된 비율)
  CAST((d.initial_debt_points - d.current_remaining_points) AS REAL) / d.initial_debt_points * 100 AS progress_percentage,
  -- 활동 횟수
  (SELECT COUNT(*) FROM activities WHERE book_id = b.id) AS total_activities,
  -- 하이라이트 수
  (SELECT COUNT(*) FROM highlights WHERE book_id = b.id) AS total_highlights,
  b.created_at,
  d.updated_at
FROM books b
LEFT JOIN debt_ledger d ON b.id = d.book_id;

-- 통계 대시보드 뷰
CREATE VIEW IF NOT EXISTS v_dashboard_stats AS
SELECT
  COUNT(*) AS total_books,
  SUM(CASE WHEN status = 'debt' THEN 1 ELSE 0 END) AS debt_books,
  SUM(CASE WHEN status = 'partial' THEN 1 ELSE 0 END) AS partial_books,
  SUM(CASE WHEN status = 'asset' THEN 1 ELSE 0 END) AS asset_books,
  SUM(initial_debt_points) AS total_initial_debt,
  SUM(current_remaining_points) AS total_remaining_debt,
  SUM(accumulated_mileage) AS total_mileage,
  -- 전체 진행률
  CAST((SUM(initial_debt_points) - SUM(current_remaining_points)) AS REAL) / SUM(initial_debt_points) * 100 AS overall_progress
FROM debt_ledger;

-- 최근 활동 뷰 (책 정보 포함)
CREATE VIEW IF NOT EXISTS v_recent_activities AS
SELECT
  a.id,
  a.book_id,
  b.title AS book_title,
  b.author,
  a.activity_type,
  a.reduction_points,
  a.content,
  a.activity_date,
  a.created_at
FROM activities a
JOIN books b ON a.book_id = b.id
ORDER BY a.created_at DESC;


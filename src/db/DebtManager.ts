import db from './database';
import { ACTIVITY_POINTS } from '../constants/activities';

/**
 * 책 상태 인터페이스
 */
export interface BookStatus {
  book_id: number;
  title: string;
  author: string;
  initial_debt: number;
  current_debt: number;
  status: 'debt' | 'partial' | 'asset';
  progress_percentage: number;
  accumulated_mileage: number;
  total_activities: number;
  total_highlights: number;
}

/**
 * 지식 부채 관리자 클래스
 */
export class DebtManager {
  private db: typeof db;

  constructor(database = db) {
    this.db = database;
  }

  /**
   * 1. 책 등록 및 부채 자동 생성
   * @param title 책 제목
   * @param author 저자
   * @param pages 페이지 수
   * @param options 추가 옵션 (장르, 구매일, 표지 이미지 등)
   * @returns 생성된 책 ID
   */
  add_book(
    title: string,
    author: string,
    pages: number,
    options?: {
      genre?: string;
      purchase_date?: string;
      cover_image_url?: string;
    }
  ): number {
    const stmt = this.db.prepare(`
      INSERT INTO books (title, author, page_count, genre, purchase_date, cover_image_url)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      title,
      author,
      pages,
      options?.genre || null,
      options?.purchase_date || new Date().toISOString().split('T')[0],
      options?.cover_image_url || null
    );

    const bookId = Number(result.lastInsertRowid);

    // 트리거에 의해 자동으로 debt_ledger 생성됨
    console.log(`✅ 책 등록 완료: "${title}" (ID: ${bookId})`);
    console.log(`   초기 부채: ${300 + pages * 0.5}pt`);

    return bookId;
  }

  /**
   * 2. 활동 기록 및 포인트 차감
   * @param book_id 책 ID
   * @param activity_type 활동 유형 (17종)
   * @param content 활동 내용
   * @param activity_date 활동 날짜 (선택, 기본값: 오늘)
   * @returns 생성된 활동 ID
   */
  record_activity(
    book_id: number,
    activity_type: keyof typeof ACTIVITY_POINTS,
    content?: string,
    activity_date?: string
  ): number {
    // 활동 유형 검증
    if (!(activity_type in ACTIVITY_POINTS)) {
      throw new Error(
        `❌ 유효하지 않은 활동 유형: ${activity_type}\n` +
        `   지원되는 유형: ${Object.keys(ACTIVITY_POINTS).join(', ')}`
      );
    }

    const reductionPoints = -ACTIVITY_POINTS[activity_type];

    // highlight는 add_highlight에서만 처리
    if (activity_type === 'highlight') {
      console.warn('⚠️  highlight는 add_highlight() 메서드를 사용하세요.');
    }

    const stmt = this.db.prepare(`
      INSERT INTO activities (book_id, activity_type, reduction_points, content, activity_date)
      VALUES (?, ?, ?, ?, ?)
    `);

    const result = stmt.run(
      book_id,
      activity_type,
      reductionPoints,
      content || null,
      activity_date || new Date().toISOString().split('T')[0]
    );

    const activityId = Number(result.lastInsertRowid);

    // 트리거에 의해 자동으로 포인트 차감 및 상태 업데이트됨
    console.log(`✨ 활동 기록: ${activity_type} (${reductionPoints}pt)`);

    // 현재 상태 출력
    const status = this.get_status(book_id);
    console.log(`   현재 부채: ${status.current_debt}pt (${status.status})`);

    return activityId;
  }

  /**
   * 3. 하이라이트 추가 + 자동 탕감
   * @param book_id 책 ID
   * @param text 원문
   * @param page 페이지 번호
   * @param thought 나의 생각/메모
   * @returns 생성된 하이라이트 ID
   */
  add_highlight(
    book_id: number,
    text: string,
    page?: number,
    thought?: string
  ): number {
    const stmt = this.db.prepare(`
      INSERT INTO highlights (book_id, original_text, page_number, my_thoughts)
      VALUES (?, ?, ?, ?)
    `);

    const result = stmt.run(
      book_id,
      text,
      page || null,
      thought || null
    );

    const highlightId = Number(result.lastInsertRowid);

    // 트리거에 의해 자동으로 activity 생성 + 20pt 차감됨
    console.log(`✏️  하이라이트 추가: "${text.substring(0, 30)}..." (-20pt)`);

    // 현재 상태 출력
    const status = this.get_status(book_id);
    console.log(`   현재 부채: ${status.current_debt}pt (${status.status})`);

    return highlightId;
  }

  /**
   * 4. 책의 현재 부채 상태 반환
   * @param book_id 책 ID
   * @returns 부채 상태 정보
   */
  get_status(book_id: number): BookStatus {
    const stmt = this.db.prepare(`
      SELECT 
        id as book_id,
        title,
        author,
        initial_debt_points as initial_debt,
        current_remaining_points as current_debt,
        status,
        progress_percentage,
        accumulated_mileage,
        total_activities,
        total_highlights
      FROM v_books_with_debt
      WHERE id = ?
    `);

    const result = stmt.get(book_id) as BookStatus | undefined;

    if (!result) {
      throw new Error(`❌ 책을 찾을 수 없습니다. (ID: ${book_id})`);
    }

    return result;
  }

  /**
   * 5. 전체 부채 포인트 합계 (양수만, 아직 완료하지 못한 책들)
   * @returns 전체 잔여 부채 합계
   */
  get_total_debt(): number {
    const stmt = this.db.prepare(`
      SELECT SUM(current_remaining_points) as total
      FROM debt_ledger
      WHERE status IN ('debt', 'partial')
    `);

    const result = stmt.get() as { total: number | null };
    return result.total || 0;
  }

  /**
   * 6. 자산으로 전환된 책 수
   * @returns 자산화 완료된 책의 개수
   */
  get_total_asset(): number {
    const stmt = this.db.prepare(`
      SELECT COUNT(*) as count
      FROM debt_ledger
      WHERE status = 'asset'
    `);

    const result = stmt.get() as { count: number };
    return result.count;
  }

  /**
   * 7. 순자산(마일리지) 합계
   * @returns 전체 마일리지 포인트
   */
  get_surplus(): number {
    const stmt = this.db.prepare(`
      SELECT SUM(accumulated_mileage) as total
      FROM debt_ledger
    `);

    const result = stmt.get() as { total: number | null };
    return result.total || 0;
  }

  /**
   * 전체 통계 조회
   * @returns 대시보드 통계
   */
  get_dashboard_stats() {
    const stmt = this.db.prepare(`
      SELECT * FROM v_dashboard_stats
    `);

    return stmt.get() as {
      total_books: number;
      debt_books: number;
      partial_books: number;
      asset_books: number;
      total_initial_debt: number;
      total_remaining_debt: number;
      total_mileage: number;
      overall_progress: number;
    };
  }

  /**
   * 모든 책 목록 조회
   * @param status 상태 필터 (선택)
   * @returns 책 목록
   */
  get_all_books(status?: 'debt' | 'partial' | 'asset'): BookStatus[] {
    let query = `
      SELECT 
        id as book_id,
        title,
        author,
        initial_debt_points as initial_debt,
        current_remaining_points as current_debt,
        status,
        progress_percentage,
        accumulated_mileage,
        total_activities,
        total_highlights
      FROM v_books_with_debt
    `;

    if (status) {
      query += ` WHERE status = ?`;
      const stmt = this.db.prepare(query);
      return stmt.all(status) as BookStatus[];
    } else {
      query += ` ORDER BY updated_at DESC`;
      const stmt = this.db.prepare(query);
      return stmt.all() as BookStatus[];
    }
  }

  /**
   * 책의 활동 내역 조회
   * @param book_id 책 ID
   * @returns 활동 내역 배열
   */
  get_activities(book_id: number) {
    const stmt = this.db.prepare(`
      SELECT 
        id,
        activity_type,
        reduction_points,
        content,
        activity_date,
        created_at
      FROM activities
      WHERE book_id = ?
      ORDER BY created_at DESC
    `);

    return stmt.all(book_id);
  }

  /**
   * 책의 하이라이트 목록 조회
   * @param book_id 책 ID
   * @returns 하이라이트 배열
   */
  get_highlights(book_id: number) {
    const stmt = this.db.prepare(`
      SELECT 
        id,
        original_text,
        page_number,
        my_thoughts,
        created_at
      FROM highlights
      WHERE book_id = ?
      ORDER BY page_number, created_at
    `);

    return stmt.all(book_id);
  }

  /**
   * 최근 활동 내역 조회 (모든 책)
   * @param limit 조회할 개수
   * @returns 최근 활동 내역
   */
  get_recent_activities(limit: number = 10) {
    const stmt = this.db.prepare(`
      SELECT * FROM v_recent_activities
      LIMIT ?
    `);

    return stmt.all(limit);
  }

  /**
   * 활동 유형별 통계
   * @returns 활동 유형별 횟수 및 총 탕감 포인트
   */
  get_activity_stats() {
    const stmt = this.db.prepare(`
      SELECT 
        activity_type,
        COUNT(*) as count,
        SUM(ABS(reduction_points)) as total_reduction
      FROM activities
      GROUP BY activity_type
      ORDER BY total_reduction DESC
    `);

    return stmt.all();
  }

  /**
   * 요약 리포트 출력
   */
  print_summary() {
    const stats = this.get_dashboard_stats();
    
    console.log('\n📊 ===== 지식 부채 현황 =====');
    console.log(`📚 전체 책: ${stats.total_books}권`);
    console.log(`   🔴 부채: ${stats.debt_books}권`);
    console.log(`   🟡 상환중: ${stats.partial_books}권`);
    console.log(`   🟢 자산: ${stats.asset_books}권`);
    console.log(`\n💰 재정 상태:`);
    console.log(`   초기 부채: ${stats.total_initial_debt}pt`);
    console.log(`   잔여 부채: ${stats.total_remaining_debt}pt`);
    console.log(`   마일리지: ${stats.total_mileage}pt`);
    console.log(`   전체 진행률: ${stats.overall_progress.toFixed(1)}%`);
    console.log('========================\n');
  }
}

// 싱글톤 인스턴스 export
export const debtManager = new DebtManager();


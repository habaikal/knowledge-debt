import { debtManager } from './DebtManager';
import { initDatabase } from './database';
import { ACTIVITY_POINTS } from '../constants/activities';

/**
 * DebtManager 사용 예제
 */
function example() {
  console.log('🚀 DebtManager 사용 예제\n');

  // 데이터베이스 초기화
  initDatabase();

  // 1. 책 등록
  console.log('📚 1. 책 등록하기');
  const bookId = debtManager.add_book(
    '데이터베이스 인터널스',
    '알렉스 페트로프',
    500,
    { genre: '기술서적' }
  );
  console.log('');

  // 2. 독서 시작 (일부 읽기)
  console.log('📖 2. 독서 시작');
  debtManager.record_activity(bookId, 'read', '1장 읽기 시작');
  console.log('');

  // 3. 하이라이트 추가 (여러 개)
  console.log('✏️  3. 하이라이트 추가');
  debtManager.add_highlight(
    bookId,
    'B-트리는 균형 잡힌 트리 구조로 데이터를 효율적으로 저장한다.',
    42,
    'MySQL의 InnoDB 엔진에서 사용하는 구조구나!'
  );
  
  debtManager.add_highlight(
    bookId,
    'LSM 트리는 쓰기 성능을 최적화한다.',
    78,
    'Cassandra, RocksDB에서 사용되는 이유를 이해했다.'
  );
  console.log('');

  // 4. 다양한 활동 추가
  console.log('🎯 4. 다양한 활동하기');
  
  // 감상 기록
  debtManager.record_activity(
    bookId,
    'feeling',
    '복잡한 내용이지만 그림과 예제가 이해를 돕는다.'
  );

  // 독서 일지
  debtManager.record_activity(
    bookId,
    'diary',
    '2장까지 완독. LSM 트리와 B-트리의 차이를 정리했다.'
  );

  // 블로그 작성
  debtManager.record_activity(
    bookId,
    'blog',
    '블로그에 "데이터베이스 인덱스 구조 비교" 포스팅'
  );

  // 토론 참여
  debtManager.record_activity(
    bookId,
    'discussion',
    '사내 스터디에서 B-트리 vs LSM 트리 토론 진행'
  );
  console.log('');

  // 5. 더 많은 활동으로 자산화하기
  console.log('💪 5. 집중적으로 활동하기');
  
  // 프로젝트 적용 (60pt)
  debtManager.record_activity(
    bookId,
    'project',
    '프로젝트에 인덱스 최적화 적용'
  );

  // 발표 (50pt)
  debtManager.record_activity(
    bookId,
    'presentation',
    '팀 미팅에서 "효율적인 DB 인덱스 설계" 발표'
  );

  // 실천/적용 (50pt)
  debtManager.record_activity(
    bookId,
    'action',
    '실제 서비스에 복합 인덱스 추가 → 쿼리 속도 3배 향상'
  );
  console.log('');

  // 6. 현재 상태 확인
  console.log('📊 6. 현재 상태 확인');
  const status = debtManager.get_status(bookId);
  console.log(`   책: ${status.title}`);
  console.log(`   저자: ${status.author}`);
  console.log(`   초기 부채: ${status.initial_debt}pt`);
  console.log(`   현재 부채: ${status.current_debt}pt`);
  console.log(`   진행률: ${status.progress_percentage.toFixed(1)}%`);
  console.log(`   상태: ${status.status}`);
  console.log(`   마일리지: ${status.accumulated_mileage}pt`);
  console.log(`   총 활동: ${status.total_activities}회`);
  console.log(`   하이라이트: ${status.total_highlights}개`);
  console.log('');

  // 7. 전체 통계
  console.log('📈 7. 전체 통계');
  console.log(`   전체 부채: ${debtManager.get_total_debt()}pt`);
  console.log(`   자산화된 책: ${debtManager.get_total_asset()}권`);
  console.log(`   순자산(마일리지): ${debtManager.get_surplus()}pt`);
  console.log('');

  // 8. 요약 리포트
  debtManager.print_summary();

  // 9. 활동 내역 조회
  console.log('📝 9. 활동 내역');
  const activities = debtManager.get_activities(bookId);
  activities.slice(0, 5).forEach((activity: any) => {
    console.log(`   - ${activity.activity_type}: ${activity.content} (${activity.reduction_points}pt)`);
  });
  console.log('');

  // 10. 하이라이트 조회
  console.log('✨ 10. 하이라이트 목록');
  const highlights = debtManager.get_highlights(bookId);
  highlights.forEach((highlight: any) => {
    console.log(`   [p.${highlight.page_number}] "${highlight.original_text.substring(0, 40)}..."`);
    if (highlight.my_thoughts) {
      console.log(`      💭 ${highlight.my_thoughts}`);
    }
  });
  console.log('');

  // 11. 활동 유형 안내
  console.log('📋 11. 지원되는 활동 유형 (17종)');
  Object.entries(ACTIVITY_POINTS).forEach(([type, points]) => {
    console.log(`   ${type.padEnd(15)} → -${points}pt`);
  });
}

// 예제 실행
if (import.meta.url === `file://${process.argv[1]}`) {
  example();
}

export default example;


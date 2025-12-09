import { initDatabase, bookQueries, activityQueries, highlightQueries } from './database';

/**
 * 샘플 데이터 추가
 */
export function seedDatabase() {
  console.log('🌱 Seeding database...');

  // 책 1: 얇은 책 (빨리 자산화 가능)
  const book1Id = bookQueries.create({
    title: '아주 작은 습관의 힘',
    author: '제임스 클리어',
    purchase_date: '2024-01-15',
    genre: '자기계발',
    cover_image_url: 'https://example.com/atomic-habits.jpg',
    page_count: 400
  });
  console.log(`📚 Book 1 created (ID: ${book1Id})`);

  // 책 2: 중간 두께 책
  const book2Id = bookQueries.create({
    title: '클린 코드',
    author: '로버트 C. 마틴',
    purchase_date: '2024-02-01',
    genre: '프로그래밍',
    cover_image_url: 'https://example.com/clean-code.jpg',
    page_count: 584
  });
  console.log(`📚 Book 2 created (ID: ${book2Id})`);

  // 책 3: 두꺼운 책 (부채 많음)
  const book3Id = bookQueries.create({
    title: '해리 포터와 불의 잔',
    author: 'J.K. 롤링',
    purchase_date: '2024-03-10',
    genre: '판타지',
    cover_image_url: 'https://example.com/harry-potter.jpg',
    page_count: 752
  });
  console.log(`📚 Book 3 created (ID: ${book3Id})`);

  // 책 1에 하이라이트 추가 (각 -20pt)
  highlightQueries.create({
    book_id: book1Id as number,
    original_text: '1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.',
    page_number: 15,
    my_thoughts: '복리의 힘을 습관에 적용한 개념이 인상적이다.'
  });

  highlightQueries.create({
    book_id: book1Id as number,
    original_text: '습관은 자아 정체성의 구체화다.',
    page_number: 45,
    my_thoughts: '행동이 정체성을 만든다는 역발상이 신선하다.'
  });

  highlightQueries.create({
    book_id: book1Id as number,
    original_text: '환경을 설계하라. 의지력에 의존하지 마라.',
    page_number: 82,
    my_thoughts: '시스템이 의지보다 강하다는 것을 실감한다.'
  });

  console.log(`✨ 3 highlights added to Book 1`);

  // 책 1에 추가 활동 (서평 작성)
  activityQueries.create({
    book_id: book1Id as number,
    activity_type: 'review',
    reduction_points: -100,
    content: '블로그에 서평 작성 (1000자 이상)',
    activity_date: '2024-01-20'
  });

  // 책 1에 추가 활동 (요약 작성)
  activityQueries.create({
    book_id: book1Id as number,
    activity_type: 'summary',
    reduction_points: -150,
    content: '핵심 내용 요약 및 실천 계획 수립',
    activity_date: '2024-01-22'
  });

  console.log(`📝 2 additional activities added to Book 1`);

  // 책 2에 하이라이트 추가
  highlightQueries.create({
    book_id: book2Id as number,
    original_text: '나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.',
    page_number: 23,
    my_thoughts: 'Later equals never. 기술 부채의 핵심을 찌르는 말이다.'
  });

  highlightQueries.create({
    book_id: book2Id as number,
    original_text: '함수는 한 가지 일을 해야 한다. 그 한 가지를 잘해야 한다.',
    page_number: 89,
    my_thoughts: '단일 책임 원칙의 가장 명확한 표현.'
  });

  console.log(`✨ 2 highlights added to Book 2`);

  // 책 2에 코드 리팩토링 활동
  activityQueries.create({
    book_id: book2Id as number,
    activity_type: 'practice',
    reduction_points: -80,
    content: '책의 원칙을 적용해 레거시 코드 리팩토링',
    activity_date: '2024-02-10'
  });

  console.log(`💻 1 practice activity added to Book 2`);

  // 책 3은 아직 읽지 않음 (부채 상태 유지)
  console.log(`📖 Book 3 remains in debt status (not started yet)`);

  // 통계 출력
  const book1 = bookQueries.getById(book1Id as number);
  const book2 = bookQueries.getById(book2Id as number);
  const book3 = bookQueries.getById(book3Id as number);

  console.log('\n📊 Current Status:');
  console.log(`Book 1: ${book1?.status?.toUpperCase()} - ${book1?.progress_percentage.toFixed(1)}% complete`);
  console.log(`  Remaining: ${book1?.current_remaining_points}pt / Initial: ${book1?.initial_debt_points}pt`);
  console.log(`Book 2: ${book2?.status?.toUpperCase()} - ${book2?.progress_percentage.toFixed(1)}% complete`);
  console.log(`  Remaining: ${book2?.current_remaining_points}pt / Initial: ${book2?.initial_debt_points}pt`);
  console.log(`Book 3: ${book3?.status?.toUpperCase()} - ${book3?.progress_percentage.toFixed(1)}% complete`);
  console.log(`  Remaining: ${book3?.current_remaining_points}pt / Initial: ${book3?.initial_debt_points}pt`);

  console.log('\n✅ Database seeded successfully!');
}

// 직접 실행
initDatabase();
seedDatabase();


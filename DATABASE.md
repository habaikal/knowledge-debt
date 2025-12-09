# 지식 부채 관리 시스템 - 데이터베이스 설계

## 📖 개념

책을 구매하면 **"지식 부채(Knowledge Debt)"**가 발생합니다. 책을 읽고, 밑줄을 긋고, 요약하고, 실천하면서 부채를 탕감해나가는 시스템입니다.

### 부채 계산 공식

```
초기 부채 = 300pt (기본) + 페이지수 × 0.5pt
```

### 상태 전환

- **debt** (부채): 잔여 포인트 > 초기 부채의 50%
- **partial** (상환중): 잔여 포인트 ≤ 초기 부채의 50%
- **asset** (자산): 잔여 포인트 ≤ 0

### 순자산(마일리지)

부채를 완전히 탕감한 후(0pt)에도 활동을 계속하면, 초과 탕감분이 **마일리지**로 누적됩니다.

---

## 🗂️ 테이블 구조

### 1. books (책 정보)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| title | TEXT | 책 제목 (필수) |
| author | TEXT | 저자 (필수) |
| purchase_date | DATE | 구매일 (기본값: 오늘) |
| genre | TEXT | 장르 |
| cover_image_url | TEXT | 표지 이미지 URL |
| page_count | INTEGER | 페이지 수 (필수) |
| created_at | DATETIME | 생성 시각 |
| updated_at | DATETIME | 수정 시각 |

### 2. debt_ledger (부채 장부)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| book_id | INTEGER | 책 ID (외래 키, UNIQUE) |
| initial_debt_points | INTEGER | 초기 부채 포인트 |
| current_remaining_points | INTEGER | 현재 잔여 포인트 |
| status | TEXT | 상태 (debt/partial/asset) |
| accumulated_mileage | INTEGER | 누적 마일리지 (순자산) |
| created_at | DATETIME | 생성 시각 |
| updated_at | DATETIME | 수정 시각 |

### 3. activities (탕감 활동 기록)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| book_id | INTEGER | 책 ID (외래 키) |
| activity_type | TEXT | 활동 유형 (highlight/review/summary/share/reread 등) |
| reduction_points | INTEGER | 탕감 포인트 (음수로 저장) |
| content | TEXT | 활동 내용 |
| activity_date | DATE | 활동 날짜 |
| created_at | DATETIME | 생성 시각 |

### 4. highlights (하이라이트/메모)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | 기본 키 (자동 증가) |
| book_id | INTEGER | 책 ID (외래 키) |
| original_text | TEXT | 원문 (필수) |
| page_number | INTEGER | 페이지 번호 |
| my_thoughts | TEXT | 나의 생각/메모 |
| created_at | DATETIME | 생성 시각 |
| updated_at | DATETIME | 수정 시각 |

---

## ⚙️ 트리거 (자동화)

### 1. create_debt_on_book_insert
- **시점**: 책 추가 시
- **동작**: debt_ledger 레코드 자동 생성
- **계산**: 초기 부채 = 300 + (페이지수 × 0.5)

### 2. create_activity_on_highlight
- **시점**: 하이라이트 추가 시
- **동작**: 
  - activities에 'highlight' 유형 기록
  - 부채 20pt 자동 차감

### 3. update_debt_on_activity
- **시점**: 활동 추가 시 (highlight 제외)
- **동작**: debt_ledger의 잔여 포인트 업데이트

### 4. update_status_on_debt_change
- **시점**: 잔여 포인트 변경 시
- **동작**:
  - 상태 자동 업데이트 (debt/partial/asset)
  - 0pt 미만 시 초과분을 마일리지로 전환
  - 잔여 포인트를 0으로 리셋

---

## 📊 뷰 (Views)

### v_books_with_debt
책 정보 + 부채 정보 + 통계를 통합한 뷰

```sql
SELECT * FROM v_books_with_debt;
```

**포함 정보:**
- 모든 책 정보
- 부채 상태 (초기/현재/마일리지)
- 진행률 (%)
- 활동 횟수
- 하이라이트 수

### v_dashboard_stats
전체 통계 대시보드

```sql
SELECT * FROM v_dashboard_stats;
```

**포함 정보:**
- 전체 책 수
- 상태별 책 수 (debt/partial/asset)
- 전체 부채 (초기/현재)
- 전체 마일리지
- 전체 진행률

### v_recent_activities
최근 활동 내역 (책 정보 포함)

```sql
SELECT * FROM v_recent_activities LIMIT 10;
```

---

## 💡 활동 유형 예시

| 활동 유형 | 탕감 포인트 | 설명 |
|----------|-----------|------|
| highlight | -20pt | 하이라이트 1개 추가 |
| review | -100pt | 서평 작성 |
| summary | -150pt | 요약 작성 |
| share | -50pt | 지식 공유 (SNS, 블로그 등) |
| practice | -80pt | 실천/적용 |
| reread | -30pt | 재독 |
| discussion | -60pt | 토론/북클럽 참여 |
| teaching | -120pt | 타인에게 가르치기 |

> 💡 탕감 포인트는 자유롭게 조정 가능합니다!

---

## 🚀 사용 예시

### 1. 새 책 추가

```typescript
import { bookQueries } from './db/database';

const bookId = bookQueries.create({
  title: '클린 코드',
  author: '로버트 C. 마틴',
  genre: '프로그래밍',
  page_count: 584
});

// ✅ 자동으로 debt_ledger 생성됨
// 초기 부채 = 300 + (584 × 0.5) = 592pt
```

### 2. 하이라이트 추가

```typescript
import { highlightQueries } from './db/database';

highlightQueries.create({
  book_id: 1,
  original_text: '나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.',
  page_number: 23,
  my_thoughts: 'Later equals never.'
});

// ✅ 자동으로 activity 기록 + 20pt 차감
```

### 3. 서평 작성 활동 추가

```typescript
import { activityQueries } from './db/database';

activityQueries.create({
  book_id: 1,
  activity_type: 'review',
  reduction_points: -100,
  content: '블로그에 서평 작성 (1000자 이상)'
});

// ✅ 100pt 차감 + 상태 자동 업데이트
```

### 4. 책 목록 조회

```typescript
import { bookQueries } from './db/database';

// 모든 책 (부채 정보 포함)
const allBooks = bookQueries.getAll();

// 상태별 조회
const debtBooks = bookQueries.getByStatus('debt');
const assetBooks = bookQueries.getByStatus('asset');

// 특정 책 조회
const book = bookQueries.getById(1);
console.log(`진행률: ${book.progress_percentage}%`);
console.log(`상태: ${book.status}`);
```

### 5. 대시보드 통계

```typescript
import { dashboardQueries } from './db/database';

const stats = dashboardQueries.getStats();
console.log(`전체 책: ${stats.total_books}권`);
console.log(`자산화: ${stats.asset_books}권`);
console.log(`전체 마일리지: ${stats.total_mileage}pt`);
console.log(`전체 진행률: ${stats.overall_progress}%`);
```

---

## 🎯 사용 시나리오

### 시나리오 1: 새 책 구매 → 자산화까지

1. **구매** (400페이지 책)
   ```
   초기 부채: 300 + (400 × 0.5) = 500pt
   상태: debt
   ```

2. **10개 하이라이트 추가**
   ```
   탕감: 10 × 20pt = 200pt
   잔여: 500 - 200 = 300pt
   상태: partial (50% 이하)
   ```

3. **서평 작성**
   ```
   탕감: 100pt
   잔여: 300 - 100 = 200pt
   상태: partial
   ```

4. **요약 + 실천**
   ```
   탕감: 150 + 80 = 230pt
   잔여: 200 - 230 = -30pt → 0pt
   마일리지: +30pt
   상태: asset ✅
   ```

### 시나리오 2: 마일리지 누적

자산화 이후에도 계속 활동하면:

```
현재: 0pt (asset), 마일리지 30pt

+ 재독 활동: -30pt
→ 현재: 0pt, 마일리지: 60pt

+ 강의 활동: -120pt
→ 현재: 0pt, 마일리지: 180pt
```

---

## 🔧 데이터베이스 초기화

```typescript
import { initDatabase } from './db/database';
import { seedDatabase } from './db/seed';

// 스키마 생성
initDatabase();

// 샘플 데이터 추가 (선택)
seedDatabase();
```

---

## 📈 확장 아이디어

1. **레벨 시스템**: 마일리지 누적에 따라 레벨 업
2. **배지 시스템**: 특정 조건 달성 시 배지 획득
3. **목표 설정**: 월별/연간 독서 목표 설정
4. **통계 차트**: 시간에 따른 부채 감소 추이 시각화
5. **알림 시스템**: 부채가 오래된 책 알림
6. **소셜 기능**: 친구와 진행률 비교

---

## 📝 라이선스

MIT


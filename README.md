# 📚 Knowledge Debt - 지식 부채 관리 시스템

> 책을 사면 부채가 생긴다. 읽고, 밑줄 긋고, 실천하면서 갚아나가자.

## 🎯 프로젝트 개요

**Knowledge Debt**는 구매한 책을 "지식 부채"로 보고, 독서와 실천을 통해 부채를 탕감해나가는 게이미피케이션 독서 관리 시스템입니다.

### 핵심 개념

```
📖 책 구매 = 부채 발생 (300pt + 페이지수 × 0.5pt)
   ↓
✨ 독서 활동 (하이라이트, 서평, 요약, 실천)
   ↓
📉 부채 탕감 (debt → partial → asset)
   ↓
🎁 순자산(마일리지) 누적
```

## 🚀 기술 스택

- **React 19** + **TypeScript** - 타입 안전한 UI
- **Vite** - 초고속 빌드 도구
- **Tailwind CSS 4** - 모던 스타일링
- **Framer Motion** - 부드러운 애니메이션
- **SQLite (better-sqlite3)** - 경량 데이터베이스
- **LocalStorage** - 브라우저 데이터 저장 (웹 데모용)

## 📦 설치 및 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 [http://localhost:5173](http://localhost:5173)을 열어 앱을 확인하세요.

### 3. (선택) 데이터베이스 초기화 (Node.js 환경)

```bash
npm run db:init
npm run db:seed  # 샘플 데이터 추가
```

## 📁 프로젝트 구조

```
knowledge-debt/
├── src/
│   ├── components/          # React 컴포넌트
│   │   ├── TaskList.tsx
│   │   └── AddTaskForm.tsx
│   ├── db/                  # 데이터베이스
│   │   ├── schema.sql       # 📋 스키마 정의 (4개 테이블 + 4개 트리거 + 3개 뷰)
│   │   ├── database.ts      # 🔧 데이터베이스 설정 및 쿼리
│   │   └── seed.ts          # 🌱 샘플 데이터
│   ├── types.ts             # TypeScript 타입 정의
│   ├── App.tsx              # 메인 앱
│   ├── App.css
│   ├── index.css            # Tailwind CSS
│   └── main.tsx
├── DATABASE.md              # 📖 데이터베이스 설계 문서
├── README.md                # 이 파일
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

## 🗂️ 데이터베이스 구조

### 테이블

1. **books** - 책 정보 (제목, 저자, 장르, 페이지수 등)
2. **debt_ledger** - 부채 장부 (초기 부채, 잔여 포인트, 상태, 마일리지)
3. **activities** - 탕감 활동 기록 (유형, 포인트, 내용, 날짜)
4. **highlights** - 하이라이트/메모 (원문, 페이지, 생각)

### 자동화 트리거

1. 책 추가 시 → 부채 자동 생성
2. 하이라이트 추가 시 → 활동 기록 + 20pt 차감
3. 활동 추가 시 → 부채 포인트 업데이트
4. 포인트 변경 시 → 상태 자동 전환 + 마일리지 누적

### 뷰 (Views)

1. **v_books_with_debt** - 책 + 부채 통합 정보
2. **v_dashboard_stats** - 전체 통계
3. **v_recent_activities** - 최근 활동 내역

> 📖 자세한 데이터베이스 설계는 [DATABASE.md](./DATABASE.md)를 참고하세요.

## ✨ 주요 기능

### 1. 부채 계산 시스템

```typescript
초기 부채 = 300pt (기본) + 페이지수 × 0.5pt

예시:
- 300페이지 책 → 300 + 150 = 450pt
- 500페이지 책 → 300 + 250 = 550pt
- 800페이지 책 → 300 + 400 = 700pt
```

### 2. 상태 전환

| 상태 | 조건 | 설명 |
|------|------|------|
| 🔴 **debt** | 잔여 > 50% | 부채 상태 (읽기 시작) |
| 🟡 **partial** | 잔여 ≤ 50% | 상환 중 (열심히 읽는 중) |
| 🟢 **asset** | 잔여 ≤ 0 | 자산화 완료! |

### 3. 활동 유형별 탕감

| 활동 | 탕감 | 비고 |
|------|------|------|
| ✏️ 하이라이트 | -20pt | 자동 기록 |
| 📝 서평 작성 | -100pt | 블로그, SNS 등 |
| 📋 요약 작성 | -150pt | 핵심 내용 정리 |
| 💬 지식 공유 | -50pt | 공유, 추천 |
| 💪 실천/적용 | -80pt | 실생활 적용 |
| 🔁 재독 | -30pt | 반복 학습 |
| 🎓 가르치기 | -120pt | 타인에게 설명 |

### 4. 마일리지 시스템

부채를 완전히 갚은 후에도 활동을 계속하면 **순자산(마일리지)**로 누적됩니다!

```
현재: 0pt (자산화 완료)
  ↓
+ 재독: -30pt
  ↓
마일리지: 30pt 누적 🎁
```

## 🎮 사용 시나리오

### 시나리오: 400페이지 프로그래밍 책

```
📖 1단계: 구매
   초기 부채: 500pt
   상태: 🔴 debt

✏️ 2단계: 독서 + 하이라이트 10개
   탕감: 200pt
   잔여: 300pt
   상태: 🟡 partial (50% 달성!)

📝 3단계: 블로그 서평 작성
   탕감: 100pt
   잔여: 200pt
   상태: 🟡 partial

💪 4단계: 요약 + 프로젝트 적용
   탕감: 230pt (150 + 80)
   잔여: -30pt → 0pt
   마일리지: 30pt
   상태: 🟢 asset (완료!)

🎓 5단계: 동료에게 강의
   탕감: 120pt
   마일리지: 150pt (누적)
```

## 🛠️ 개발 가이드

### 책 추가

```typescript
import { bookQueries } from './db/database';

const bookId = bookQueries.create({
  title: '클린 코드',
  author: '로버트 C. 마틴',
  genre: '프로그래밍',
  page_count: 584
});
```

### 하이라이트 추가

```typescript
import { highlightQueries } from './db/database';

highlightQueries.create({
  book_id: 1,
  original_text: '좋은 코드는 스스로 설명한다.',
  page_number: 42,
  my_thoughts: '주석보다 명확한 코드가 낫다.'
});
// ✅ 자동으로 20pt 차감됨
```

### 활동 기록

```typescript
import { activityQueries } from './db/database';

activityQueries.create({
  book_id: 1,
  activity_type: 'review',
  reduction_points: -100,
  content: '블로그 서평 작성 완료'
});
```

### 통계 조회

```typescript
import { dashboardQueries } from './db/database';

const stats = dashboardQueries.getStats();
console.log(`자산화된 책: ${stats.asset_books}권`);
console.log(`전체 마일리지: ${stats.total_mileage}pt`);
```

## 🎨 UI 구현 아이디어

1. **대시보드**
   - 전체 통계 (부채/자산 비율)
   - 마일리지 현황
   - 진행률 차트

2. **책 목록**
   - 상태별 필터 (debt/partial/asset)
   - 진행률 프로그레스 바
   - 정렬 (구매일, 진행률, 부채량)

3. **책 상세 페이지**
   - 부채 현황 시각화
   - 하이라이트 목록
   - 활동 타임라인
   - 빠른 활동 추가 버튼

4. **활동 추가 모달**
   - 활동 유형 선택
   - 탕감 포인트 자동 계산
   - 내용 입력

5. **애니메이션**
   - 상태 전환 시 축하 효과
   - 마일리지 획득 애니메이션
   - 진행률 증가 효과

## 📈 확장 아이디어

- [ ] 레벨 시스템 (마일리지 기반)
- [ ] 배지/업적 시스템
- [ ] 월별/연간 목표 설정
- [ ] 독서 통계 차트
- [ ] 알림 시스템 (오래된 부채 알림)
- [ ] 소셜 기능 (친구와 비교)
- [ ] 독서 챌린지
- [ ] 독서 일지

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

## 📄 라이선스

MIT

---

<p align="center">
  Made with 💙 by futurewave
</p>

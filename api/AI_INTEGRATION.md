# 🔗 AI 에이전트 통합 가이드

AI 에이전트가 FastAPI와 완전히 통합되어 데이터베이스와 연동됩니다.

## 🎯 전체 플로우

```
1. 책 등록 (POST /books)
   ↓
2. 하이라이트 추가 (POST /highlights)
   ↓ -20pt 자동 탕감
3. AI 행동 제안 (POST /ai/suggest-actions)
   ↓
4. 제안 선택 & 실행 (POST /ai/execute-action)
   ↓ 활동 유형별 포인트 자동 차감
5. 부채 상태 자동 업데이트
```

## 📋 API 엔드포인트

### 1. POST /ai/suggest-actions

하이라이트를 분석하여 탕감 행동을 제안합니다.

**Request:**
```json
{
  "book_id": 1,
  "highlight_id": 1,
  "user_context": "소프트웨어 엔지니어, 재택근무"
}
```

**Response:**
```json
{
  "book_id": 1,
  "book_title": "아주 작은 습관의 힘",
  "highlight_id": 1,
  "highlight_text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
  "user_context": "소프트웨어 엔지니어, 재택근무",
  "suggestions": [
    {
      "action": "오늘부터 매일 아침 코드 리뷰 10분을 캘린더에 등록하고 완료 체크한다",
      "duration": "10분",
      "difficulty": "쉬움",
      "activity_type": "action",
      "estimated_points": 50
    },
    {
      "action": "지난 달과 이번 달의 커밋 수를 비교하여 1% 개선 여부를 그래프로 시각화한다",
      "duration": "30분",
      "difficulty": "보통",
      "activity_type": "visual",
      "estimated_points": 35
    },
    {
      "action": "팀 회의에서 '점진적 개선의 복리 효과'를 주제로 5분 발표한다",
      "duration": "15분",
      "difficulty": "보통",
      "activity_type": "presentation",
      "estimated_points": 50
    }
  ]
}
```

### 2. POST /ai/execute-action

제안된 행동을 선택하여 실행합니다.

**Request:**
```json
{
  "book_id": 1,
  "suggestion": {
    "action": "오늘부터 매일 아침 코드 리뷰 10분을 캘린더에 등록하고 완료 체크한다",
    "duration": "10분",
    "difficulty": "쉬움",
    "activity_type": "action",
    "estimated_points": 50
  },
  "content": "캘린더 등록 완료 및 첫 리뷰 시작"
}
```

**Response:**
```json
{
  "id": 5,
  "book_id": 1,
  "activity_type": "action",
  "reduction_points": -50,
  "content": "[AI 제안] 캘린더 등록 완료 및 첫 리뷰 시작",
  "activity_date": "2024-12-09",
  "created_at": "2024-12-09T10:30:00"
}
```

**자동 처리:**
- ✅ activities 테이블에 기록
- ✅ 50pt 자동 차감
- ✅ 부채 상태 자동 업데이트

## 🧪 테스트 방법

### 1. Python 스크립트로 전체 플로우 테스트

```bash
cd api

# 환경변수 설정
export GOOGLE_API_KEY='your-api-key'

# 서버 실행 (터미널 1)
uvicorn main:app --reload

# 테스트 실행 (터미널 2)
python test_ai_flow.py
```

**테스트 시나리오:**
1. 책 등록 → 초기 부채 생성
2. 하이라이트 추가 → -20pt
3. AI 제안 요청 → 3가지 행동 제안
4. 첫 번째 제안 실행 → 포인트 차감
5. 최종 상태 확인

### 2. cURL로 테스트

```bash
# 1. 책 등록
BOOK_ID=$(curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "아주 작은 습관의 힘",
    "author": "제임스 클리어",
    "page_count": 400
  }' | jq -r '.id')

echo "Book ID: $BOOK_ID"

# 2. 하이라이트 추가
HIGHLIGHT_ID=$(curl -X POST "http://localhost:8000/highlights" \
  -H "Content-Type: application/json" \
  -d "{
    \"book_id\": $BOOK_ID,
    \"original_text\": \"1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.\",
    \"page_number\": 15
  }" | jq -r '.id')

echo "Highlight ID: $HIGHLIGHT_ID"

# 3. AI 제안 요청
curl -X POST "http://localhost:8000/ai/suggest-actions" \
  -H "Content-Type: application/json" \
  -d "{
    \"book_id\": $BOOK_ID,
    \"highlight_id\": $HIGHLIGHT_ID,
    \"user_context\": \"소프트웨어 엔지니어\"
  }" | jq

# 4. 제안 실행 (응답에서 첫 번째 suggestion을 복사해서 사용)
curl -X POST "http://localhost:8000/ai/execute-action" \
  -H "Content-Type: application/json" \
  -d "{
    \"book_id\": $BOOK_ID,
    \"suggestion\": {
      \"action\": \"여기에 제안된 행동 붙여넣기\",
      \"duration\": \"10분\",
      \"difficulty\": \"쉬움\",
      \"activity_type\": \"action\",
      \"estimated_points\": 50
    }
  }" | jq
```

### 3. Swagger UI에서 테스트

1. http://localhost:8000/docs 접속
2. POST /books → 책 등록 → book_id 확인
3. POST /highlights → 하이라이트 추가 → highlight_id 확인
4. POST /ai/suggest-actions → 제안 받기
5. POST /ai/execute-action → 제안 실행
6. GET /books/{id} → 결과 확인

## 🎨 프론트엔드 통합 예시

### React Component

```typescript
// AI 제안 받기
const getSuggestions = async (bookId: number, highlightId: number) => {
  const response = await fetch('http://localhost:8000/ai/suggest-actions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      book_id: bookId,
      highlight_id: highlightId,
      user_context: '소프트웨어 엔지니어'
    })
  });
  
  const data = await response.json();
  return data.suggestions;
};

// 제안 실행
const executeSuggestion = async (bookId: number, suggestion: any) => {
  const response = await fetch('http://localhost:8000/ai/execute-action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      book_id: bookId,
      suggestion: suggestion
    })
  });
  
  const activity = await response.json();
  
  // 성공 토스트 표시
  toast.success(
    `🎉 ${activity.reduction_points}pt 탕감 완료!`,
    { duration: 3000 }
  );
  
  return activity;
};

// 사용 예시
const handleHighlightClick = async (highlight) => {
  // AI 제안 받기
  const suggestions = await getSuggestions(bookId, highlight.id);
  
  // 모달로 제안 표시
  setSuggestions(suggestions);
  setShowModal(true);
};

const handleSuggestionSelect = async (suggestion) => {
  // 제안 실행
  await executeSuggestion(bookId, suggestion);
  
  // 부채 상태 새로고침
  refreshBookStatus();
};
```

## 🔄 자동화 아이디어

### 1. 하이라이트 추가 시 자동 제안
```python
@app.post("/highlights-with-ai")
def add_highlight_with_suggestions(highlight: schemas.HighlightCreate):
    # 1. 하이라이트 추가
    db_highlight = crud.create_highlight(db, highlight)
    
    # 2. 자동으로 AI 제안 생성
    suggestions = suggest_actions(
        book_id=highlight.book_id,
        highlight_id=db_highlight.id
    )
    
    return {
        "highlight": db_highlight,
        "suggestions": suggestions
    }
```

### 2. 일일 추천 시스템
```python
@app.get("/ai/daily-suggestions")
def get_daily_suggestions(user_id: int):
    # 미완료 책들의 하이라이트에서 랜덤 선택
    # AI 제안 생성
    # 매일 아침 푸시 알림
    pass
```

### 3. 진행률 부스트
```python
@app.get("/ai/boost-suggestions/{book_id}")
def boost_book_progress(book_id: int):
    # 부채가 많은 책에 대해
    # 모든 하이라이트 분석
    # 가장 실행하기 쉬운 행동 제안
    pass
```

## 📊 통계 및 모니터링

### AI 제안 사용률 추적
```sql
-- AI 제안으로 생성된 활동 수
SELECT COUNT(*) 
FROM activities 
WHERE content LIKE '[AI 제안]%';

-- 가장 많이 선택된 활동 유형
SELECT activity_type, COUNT(*) 
FROM activities 
WHERE content LIKE '[AI 제안]%'
GROUP BY activity_type 
ORDER BY COUNT(*) DESC;
```

## 🚨 주의사항

### 1. API 할당량
- gemini-2.0-flash-exp: 분당 15회, 일당 1,500회
- 할당량 초과 시 캐싱 또는 대기 로직 추가

### 2. 오류 처리
```python
try:
    suggestions = suggest_actions(...)
except HTTPException as e:
    if e.status_code == 429:
        # 할당량 초과
        return cached_suggestions or default_suggestions
    else:
        raise
```

### 3. 비용 최적화
- 동일한 하이라이트에 대한 제안은 캐싱
- 사용자 컨텍스트가 같으면 재사용
- 배치 처리로 API 호출 최소화

## 🎉 활용 시나리오

1. **스마트 독서 코칭**: 하이라이트마다 맞춤 행동 제안
2. **진행률 가속화**: 부채 많은 책에 쉬운 행동 추천
3. **습관 형성**: 매일 아침 실행 가능한 행동 알림
4. **소셜 기능**: 친구들과 AI 제안 공유
5. **게임화**: AI 제안 완료 시 추가 보너스 포인트

---

Made with 🤖 + 💙 using Google Gemini API


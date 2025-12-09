# 🎨 Mix Ideas API - 두 책 연결 아이디어 생성

두 권의 책을 연결하여 새로운 아이디어를 생성하고, 자동으로 저장 및 부채 탕감을 수행하는 엔드포인트입니다.

## 🎯 핵심 기능

1. **두 가지 모드**
   - **Manual**: 사용자가 직접 두 책 선택
   - **Random**: 시스템이 랜덤하게 연결 가능한 책 조합 제안

2. **자동 저장**
   - 생성된 아이디어를 `ideas` 테이블에 저장
   - 연결된 두 책 정보 보관

3. **자동 부채 탕감**
   - 두 책 모두에 `connect` 활동 기록
   - 각 -40pt씩, 총 -80pt 탕감

## 📊 Database Schema

### ideas 테이블

```sql
CREATE TABLE ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id_a INTEGER NOT NULL,           -- 첫 번째 책 ID
    book_id_b INTEGER NOT NULL,           -- 두 번째 책 ID
    connection_point TEXT NOT NULL,       -- 연결점
    new_idea TEXT NOT NULL,               -- 새로운 아이디어
    why_it_works TEXT,                    -- 작동 이유 (JSON)
    example TEXT,                         -- 예시
    user_context TEXT,                    -- 사용자 컨텍스트
    distance REAL,                        -- 의미적 거리
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id_a) REFERENCES books(id),
    FOREIGN KEY (book_id_b) REFERENCES books(id)
);
```

## 🚀 API 엔드포인트

### POST /ai/mix-ideas

두 책을 연결하여 아이디어 생성

#### Request

**Manual Mode:**
```json
{
  "mode": "manual",
  "book_id_a": 1,
  "book_id_b": 5,
  "user_context": "스타트업 창업 준비 중"
}
```

**Random Mode:**
```json
{
  "mode": "random",
  "user_context": "혁신적인 비즈니스 아이디어 필요"
}
```

#### Response

```json
{
  "idea": {
    "id": 1,
    "book_id_a": 1,
    "book_id_b": 5,
    "connection_point": "점진적 개선과 기술 부채의 역설적 관계",
    "new_idea": "개발자를 위한 '코드 습관 트래커' 앱...",
    "why_it_works": "[\"복리 효과\", \"시각화\", \"습관화\"]",
    "example": "매일 출근 후 10분 코드 청소...",
    "user_context": "스타트업 창업 준비 중",
    "distance": 1.24,
    "created_at": "2024-12-09T10:30:00"
  },
  "book_a": {
    "id": 1,
    "title": "아주 작은 습관의 힘",
    "author": "제임스 클리어",
    "genre": "자기계발"
  },
  "book_b": {
    "id": 5,
    "title": "클린 코드",
    "author": "로버트 C. 마틴",
    "genre": "프로그래밍"
  },
  "activities_created": [
    {
      "id": 42,
      "book_id": 1,
      "activity_type": "connect",
      "reduction_points": -40,
      "content": "'클린 코드'와 연결: 점진적 개선과 기술 부채..."
    },
    {
      "id": 43,
      "book_id": 5,
      "activity_type": "connect",
      "reduction_points": -40,
      "content": "'아주 작은 습관의 힘'와 연결: 점진적 개선..."
    }
  ],
  "total_reduction": -80
}
```

### GET /ideas

저장된 아이디어 목록 조회

```bash
curl "http://localhost:8000/ideas?skip=0&limit=20"
```

**Response:**
```json
[
  {
    "id": 1,
    "book_id_a": 1,
    "book_id_b": 5,
    "connection_point": "...",
    "new_idea": "...",
    "why_it_works": "[...]",
    "example": "...",
    "created_at": "2024-12-09T10:30:00"
  }
]
```

### GET /ideas/{idea_id}

아이디어 상세 조회

```bash
curl "http://localhost:8000/ideas/1"
```

**Response:**
```json
{
  "idea": {
    "id": 1,
    "connection_point": "...",
    "new_idea": "...",
    "why_it_works": ["이유1", "이유2", "이유3"]
  },
  "book_a": { "id": 1, "title": "..." },
  "book_b": { "id": 5, "title": "..." }
}
```

### GET /books/{book_id}/ideas

특정 책과 연결된 아이디어들

```bash
curl "http://localhost:8000/books/1/ideas"
```

**Response:**
```json
{
  "book_id": 1,
  "book_title": "아주 작은 습관의 힘",
  "total_ideas": 3,
  "ideas": [...]
}
```

## 🧪 테스트

### 자동 테스트 실행

```bash
cd api

# 환경 변수 설정
export GOOGLE_API_KEY='your-api-key'

# 테스트 실행
python3 test_mix_ideas.py
```

**테스트 시나리오:**
1. 기존 책 확인 (없으면 자동 생성)
2. Manual Mode 테스트
3. Random Mode 테스트
4. 생성된 아이디어 목록 조회
5. 특정 책의 아이디어 조회

### 수동 테스트 (curl)

```bash
# 1. Manual Mode
curl -X POST "http://localhost:8000/ai/mix-ideas" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "manual",
    "book_id_a": 1,
    "book_id_b": 2,
    "user_context": "새로운 관점 필요"
  }'

# 2. Random Mode
curl -X POST "http://localhost:8000/ai/mix-ideas" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "random",
    "user_context": "혁신적 아이디어"
  }'

# 3. 아이디어 목록
curl "http://localhost:8000/ideas"

# 4. 특정 아이디어
curl "http://localhost:8000/ideas/1"

# 5. 특정 책의 아이디어
curl "http://localhost:8000/books/1/ideas"
```

## 💡 활용 시나리오

### 1. 독서 모임 아이디어 생성

```python
# 참가자들이 읽은 책 2권 선택
request = {
    "mode": "manual",
    "book_id_a": 12,  # 참가자 A의 책
    "book_id_b": 25,  # 참가자 B의 책
    "user_context": "독서 모임에서 토론할 주제 필요"
}

response = requests.post("/ai/mix-ideas", json=request)
idea = response.json()

print(f"토론 주제: {idea['idea']['connection_point']}")
print(f"아이디어: {idea['idea']['new_idea']}")
```

### 2. 개인 학습 아카이브

```python
# 정기적으로 랜덤 아이디어 생성
for _ in range(5):
    response = requests.post("/ai/mix-ideas", json={
        "mode": "random",
        "user_context": "나의 독서 인사이트"
    })
    
    idea = response.json()
    # 생성된 아이디어는 자동으로 저장됨
    print(f"💡 {idea['idea']['connection_point']}")
```

### 3. 책 추천 시스템

```python
# 사용자가 최근 읽은 책과 연결된 아이디어 찾기
response = requests.get(f"/books/{user_recent_book_id}/ideas")
ideas = response.json()

if ideas['total_ideas'] > 0:
    print("이 책과 연결된 다른 책들:")
    for idea in ideas['ideas']:
        other_book_id = (
            idea['book_id_b'] 
            if idea['book_id_a'] == user_recent_book_id 
            else idea['book_id_a']
        )
        print(f"📚 책 ID {other_book_id}: {idea['connection_point']}")
```

## 📊 통계 및 분석

### 가장 많이 연결된 책 찾기

```python
# 모든 아이디어 가져오기
response = requests.get("/ideas?limit=1000")
ideas = response.json()

# 책별 연결 횟수 카운트
book_connections = {}
for idea in ideas:
    for book_id in [idea['book_id_a'], idea['book_id_b']]:
        book_connections[book_id] = book_connections.get(book_id, 0) + 1

# 상위 5개
top_books = sorted(
    book_connections.items(), 
    key=lambda x: x[1], 
    reverse=True
)[:5]

print("가장 많이 연결된 책:")
for book_id, count in top_books:
    print(f"📚 책 ID {book_id}: {count}개 연결")
```

## 🎨 프론트엔드 통합

### React 컴포넌트

```typescript
const MixIdeasButton = ({ bookId }) => {
  const [loading, setLoading] = useState(false);
  const [idea, setIdea] = useState(null);

  const handleMixIdeas = async (mode: 'manual' | 'random') => {
    setLoading(true);
    
    const request = mode === 'manual'
      ? { mode: 'manual', book_id_a: bookId, book_id_b: otherBookId }
      : { mode: 'random', user_context: '새로운 아이디어' };
    
    const response = await fetch('/api/ai/mix-ideas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    const data = await response.json();
    setIdea(data);
    setLoading(false);
    
    // 토스트 메시지
    toast.success(`🎉 두 책이 연결되어 -80pt 탕감되었습니다!`);
  };

  return (
    <div>
      <button onClick={() => handleMixIdeas('random')}>
        🎲 랜덤 아이디어 생성
      </button>
      
      {idea && (
        <div className="mt-4 p-6 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg">
          <h3 className="text-lg font-bold mb-2">
            🔗 {idea.idea.connection_point}
          </h3>
          <p className="mb-4">{idea.idea.new_idea}</p>
          
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <p className="text-sm text-gray-600">책 A</p>
              <p className="font-semibold">{idea.book_a.title}</p>
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-600">책 B</p>
              <p className="font-semibold">{idea.book_b.title}</p>
            </div>
          </div>
          
          <div className="bg-white/50 p-3 rounded">
            <p className="text-sm font-semibold mb-2">✅ 작동 이유:</p>
            <ul className="text-sm space-y-1">
              {JSON.parse(idea.idea.why_it_works).map((reason, i) => (
                <li key={i}>• {reason}</li>
              ))}
            </ul>
          </div>
          
          <div className="mt-4 text-center">
            <span className="inline-block bg-green-500 text-white px-4 py-2 rounded-full">
              💰 총 {idea.total_reduction}pt 탕감!
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 아이디어 목록 페이지

```typescript
const IdeasPage = () => {
  const [ideas, setIdeas] = useState([]);

  useEffect(() => {
    fetch('/api/ideas')
      .then(res => res.json())
      .then(setIdeas);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">💡 생성된 아이디어</h1>
      
      {ideas.map(idea => (
        <div key={idea.id} className="border rounded-lg p-6 hover:shadow-lg transition">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-xl font-bold">
              🔗 {idea.connection_point}
            </h3>
            <span className="text-sm text-gray-500">
              {new Date(idea.created_at).toLocaleDateString()}
            </span>
          </div>
          
          <p className="mb-4 text-gray-700">{idea.new_idea}</p>
          
          {idea.example && (
            <p className="text-sm text-gray-600 italic">
              📌 {idea.example}
            </p>
          )}
          
          <button
            onClick={() => navigate(`/ideas/${idea.id}`)}
            className="mt-4 text-blue-600 hover:underline"
          >
            자세히 보기 →
          </button>
        </div>
      ))}
    </div>
  );
};
```

## 🔥 고급 활용

### 자동 아이디어 생성 스케줄러

```python
import schedule
import time

def daily_idea_generation():
    """매일 자동으로 랜덤 아이디어 생성"""
    response = requests.post("/ai/mix-ideas", json={
        "mode": "random",
        "user_context": "매일의 새로운 인사이트"
    })
    
    if response.status_code == 200:
        idea = response.json()
        print(f"✅ 아이디어 생성: {idea['idea']['connection_point']}")
        
        # 이메일 또는 슬랙 알림 전송
        send_notification(idea)

# 매일 오전 9시 실행
schedule.every().day.at("09:00").do(daily_idea_generation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 아이디어 품질 분석

```python
# 거리(distance)가 높을수록 창의적
response = requests.get("/ideas")
ideas = response.json()

creative_ideas = sorted(
    [i for i in ideas if i['distance']],
    key=lambda x: x['distance'],
    reverse=True
)[:10]

print("가장 창의적인 아이디어 Top 10:")
for i, idea in enumerate(creative_ideas, 1):
    print(f"{i}. 거리: {idea['distance']:.2f} - {idea['connection_point']}")
```

## 📈 KPI 모니터링

- **총 생성된 아이디어 수**: `SELECT COUNT(*) FROM ideas`
- **평균 의미적 거리**: `SELECT AVG(distance) FROM ideas`
- **가장 활발한 책**: 가장 많이 연결된 책
- **사용자 활동**: `connect` 활동 수
- **총 탕감 포인트**: `connect` 활동 × 40pt

## ⚠️ 주의사항

1. **API 키 필수**: GOOGLE_API_KEY 설정 필요
2. **하이라이트 필요**: 두 책 모두 최소 1개 이상의 하이라이트
3. **할당량**: Gemini API 무료 1,500회/일
4. **중복 방지**: 같은 책 조합으로 여러 번 생성 가능 (다른 컨텍스트)

## 🎯 다음 단계

1. **아이디어 투표 기능**: 사용자들이 좋은 아이디어에 투표
2. **아이디어 실행 추적**: 실제로 실행한 아이디어 기록
3. **아이디어 공유**: 커뮤니티에 공유
4. **아이디어 진화**: 기존 아이디어를 발전시키기
5. **시각화**: 책 간 연결 네트워크 그래프

---

Made with 🎨 using Google Gemini API

책들을 연결하여 새로운 세계를 만들어보세요! ✨


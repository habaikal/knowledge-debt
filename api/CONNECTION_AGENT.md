# 🔗 Connection Agent - 세렌디피티 아이디어 생성기

전혀 다른 분야의 두 책 하이라이트를 연결해서 새로운 비즈니스 아이디어와 인사이트를 생성하는 AI 에이전트입니다.

## 🎯 핵심 개념

**세렌디피티 (Serendipity)**: 우연한 발견을 통한 창의적 사고

- 🧠 다른 분야의 개념을 강제로 연결
- 💡 예상치 못한 아이디어 발견
- 🚀 혁신적인 비즈니스 모델 창출

## 📦 구성 요소

### 1. Connection Agent
- Gemini API 기반 창의적 사고 전문가
- 두 개념을 연결하는 논리적 고리 발견
- 구체적이고 실행 가능한 아이디어 제시

### 2. Random Mix
- 벡터 DB에서 유사도가 **낮은** 하이라이트 자동 매칭
- 의도적으로 서로 다른 개념 선택
- 거리(distance)가 클수록 더 다른 개념

## 🚀 사용 방법

### API 엔드포인트

#### 1. POST /ai/connect-ideas

두 하이라이트를 연결해서 새로운 아이디어 생성

**방법 A: 수동 선택**

```bash
curl -X POST "http://localhost:8000/ai/connect-ideas" \
  -H "Content-Type: application/json" \
  -d '{
    "highlight_id_a": 1,
    "highlight_id_b": 5,
    "user_context": "스타트업 창업 준비 중"
  }'
```

**방법 B: 자동 매칭 (Random Mix)**

```bash
curl -X POST "http://localhost:8000/ai/connect-ideas" \
  -H "Content-Type: application/json" \
  -d '{
    "use_random_mix": true,
    "user_context": "새로운 비즈니스 모델 필요"
  }'
```

**Response:**

```json
{
  "highlight_a": {
    "id": "highlight_1",
    "text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
    "metadata": {
      "book_id": "1",
      "book_title": "아주 작은 습관의 힘",
      "author": "제임스 클리어",
      "genre": "자기계발"
    }
  },
  "highlight_b": {
    "id": "highlight_5",
    "text": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
    "metadata": {
      "book_id": "2",
      "book_title": "클린 코드",
      "author": "로버트 C. 마틴",
      "genre": "프로그래밍"
    }
  },
  "result": {
    "connection_point": "점진적 개선과 기술 부채의 역설적 관계",
    "new_idea": "개발자를 위한 '코드 습관 트래커' 앱. 매일 1%씩 코드 품질을 개선하도록 유도하되, 리팩토링을 미루면 '기술 부채 포인트'가 누적되어 시각화된다. 습관처럼 매일 작은 리팩토링을 하면 장기적으로 깨끗한 코드베이스를 유지할 수 있다.",
    "why_it_works": [
      "복리 효과: 매일의 작은 리팩토링이 축적되어 큰 품질 향상",
      "시각화: 기술 부채를 포인트로 보여줘 심리적 압박 생성",
      "습관화: 코드 리뷰를 일상적 습관으로 만들어 지속 가능"
    ],
    "example": "매일 출근 후 10분 '코드 청소 시간' 알림 → 한 달 후 레거시 코드 30% 개선"
  },
  "distance": 1.24
}
```

#### 2. GET /vector/random-mix

유사도가 낮은 하이라이트 무작위 매칭

```bash
curl "http://localhost:8000/vector/random-mix?n=2&min_distance=0.7"
```

**Parameters:**
- `n`: 매칭할 하이라이트 수 (2-5)
- `min_distance`: 최소 거리 (0.0-2.0, 높을수록 더 다름)

## 🧪 테스트

```bash
cd api

# 환경 변수 설정
export GOOGLE_API_KEY='your-api-key'

# 통합 테스트 실행
python test_connection.py
```

**테스트 시나리오:**
1. 두 권의 책 등록 (자기계발 + 프로그래밍)
2. 각 책에 하이라이트 추가
3. Random Mix로 전혀 다른 하이라이트 매칭
4. 수동 선택으로 아이디어 연결
5. Random Mix 자동 매칭으로 아이디어 연결

## 💡 활용 시나리오

### 1. 비즈니스 아이디어 생성

```python
# 전혀 다른 분야 책 2권 선택
request = {
    "use_random_mix": True,
    "user_context": "새로운 SaaS 비즈니스 아이디어 필요"
}

response = requests.post("/ai/connect-ideas", json=request)
idea = response.json()

print(f"💡 {idea['result']['new_idea']}")
```

**예시 출력:**
- 습관 형성 + 도시 설계 → "걷기를 유도하는 도시 리워드 앱"
- 심리학 + 프로그래밍 → "감정 상태 기반 코드 제안 IDE"

### 2. 크리에이티브 워크샵

```python
# 팀 브레인스토밍용
for _ in range(5):
    response = requests.post("/ai/connect-ideas", json={
        "use_random_mix": True,
        "user_context": "혁신적인 교육 서비스"
    })
    
    idea = response.json()
    print(f"💡 {idea['result']['connection_point']}")
    print(f"   {idea['result']['new_idea']}")
```

### 3. 개인 인사이트 발견

```python
# 최근 읽은 책 2권 연결
request = {
    "highlight_id_a": 42,
    "highlight_id_b": 87,
    "user_context": "커리어 전환을 고민 중"
}

response = requests.post("/ai/connect-ideas", json=request)
insight = response.json()

print(f"🔗 {insight['result']['connection_point']}")
print(f"✨ {insight['result']['new_idea']}")
```

## 🎨 프론트엔드 통합

### React 컴포넌트 예시

```typescript
const IdeaGenerator = () => {
  const [idea, setIdea] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateRandomIdea = async () => {
    setLoading(true);
    
    const response = await fetch('/ai/connect-ideas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        use_random_mix: true,
        user_context: '새로운 관점이 필요합니다'
      })
    });
    
    const data = await response.json();
    setIdea(data);
    setLoading(false);
  };

  return (
    <div className="p-6 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
      <h2 className="text-2xl font-bold text-white mb-4">
        🎲 세렌디피티 아이디어 생성기
      </h2>
      
      <button
        onClick={generateRandomIdea}
        disabled={loading}
        className="px-6 py-3 bg-white text-purple-600 rounded-lg hover:bg-purple-50"
      >
        {loading ? '생성 중...' : '🚀 랜덤 아이디어 생성'}
      </button>
      
      {idea && (
        <div className="mt-6 bg-white/10 backdrop-blur-md p-6 rounded-lg">
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-white/20 p-4 rounded">
              <p className="text-white/60 text-sm">책 A</p>
              <p className="text-white font-semibold">
                {idea.highlight_a.metadata.book_title}
              </p>
              <p className="text-white/80 text-sm mt-2">
                "{idea.highlight_a.text}"
              </p>
            </div>
            
            <div className="bg-white/20 p-4 rounded">
              <p className="text-white/60 text-sm">책 B</p>
              <p className="text-white font-semibold">
                {idea.highlight_b.metadata.book_title}
              </p>
              <p className="text-white/80 text-sm mt-2">
                "{idea.highlight_b.text}"
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <h3 className="text-white/60 text-sm mb-2">🔗 연결점</h3>
              <p className="text-white font-medium">
                {idea.result.connection_point}
              </p>
            </div>
            
            <div>
              <h3 className="text-white/60 text-sm mb-2">💡 새로운 아이디어</h3>
              <p className="text-white">
                {idea.result.new_idea}
              </p>
            </div>
            
            <div>
              <h3 className="text-white/60 text-sm mb-2">✅ 작동 이유</h3>
              <ul className="space-y-2">
                {idea.result.why_it_works.map((reason, i) => (
                  <li key={i} className="text-white/90 text-sm">
                    {i + 1}. {reason}
                  </li>
                ))}
              </ul>
            </div>
            
            {idea.result.example && (
              <div>
                <h3 className="text-white/60 text-sm mb-2">📌 예시</h3>
                <p className="text-white/80 text-sm">
                  {idea.result.example}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
```

### BookDetail에 추가

```typescript
const BookDetail = ({ book }) => {
  const [connections, setConnections] = useState([]);
  const [randomIdea, setRandomIdea] = useState(null);

  const handleGenerateIdea = async (highlightId) => {
    const response = await fetch('/ai/connect-ideas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        highlight_id_a: highlightId,
        use_random_mix: true,
        user_context: '이 개념을 다른 관점에서 보고 싶습니다'
      })
    });
    
    const data = await response.json();
    setRandomIdea(data);
  };

  return (
    <div>
      <h2>{book.title}</h2>
      
      <section className="highlights">
        <h3>💡 하이라이트</h3>
        {book.highlights.map(h => (
          <div key={h.id} className="highlight-card">
            <p>{h.text}</p>
            <button onClick={() => handleGenerateIdea(h.id)}>
              🎲 랜덤 아이디어 생성
            </button>
          </div>
        ))}
      </section>
      
      {randomIdea && (
        <IdeaResultModal idea={randomIdea} />
      )}
    </div>
  );
};
```

## 🔧 커스터마이징

### 시스템 프롬프트 수정

`connection_agent.py`의 `SYSTEM_PROMPT`를 수정하여 다른 스타일의 아이디어를 생성할 수 있습니다:

```python
# 비즈니스 중심
SYSTEM_PROMPT = "너는 비즈니스 전략가야. 수익 모델에 집중해서..."

# 학술 연구 중심
SYSTEM_PROMPT = "너는 학제간 연구자야. 학문적 통찰에 집중해서..."

# 예술/창작 중심
SYSTEM_PROMPT = "너는 크리에이티브 디렉터야. 예술적 표현에 집중해서..."
```

### Temperature 조정

```python
generation_config={
    "temperature": 1.5,  # 더 창의적 (0.0-2.0)
    "top_p": 0.95,
    "top_k": 40,
}
```

### Random Mix 거리 조정

```python
# 더 다른 개념 선택
random_highlights = vector_store.find_random_mix(
    n=2, 
    min_distance=1.0  # 기본 0.7
)
```

## 📊 실전 예시

### 예시 1: 자기계발 × 프로그래밍

**입력:**
- 책A: "아주 작은 습관의 힘" - "1%의 개선이 매일 쌓이면..."
- 책B: "클린 코드" - "나쁜 코드는 나중에 치워도 괜찮다는 거짓말..."

**출력:**
```
🔗 연결점: 점진적 개선과 기술 부채의 역설적 관계

💡 아이디어:
개발자를 위한 '코드 습관 트래커' 앱. 매일 1%씩 코드 품질을 
개선하도록 유도하되, 리팩토링을 미루면 '기술 부채 포인트'가 
누적되어 시각화된다.

✅ 작동 이유:
1. 복리 효과: 매일의 작은 리팩토링이 축적
2. 시각화: 부채를 포인트로 보여줘 압박감 생성
3. 습관화: 코드 품질 관리를 일상적 습관으로
```

### 예시 2: 심리학 × 도시 설계

**입력:**
- 책A: "넛지" - "선택 설계로 행동을 유도할 수 있다"
- 책B: "도시는 무엇으로 사는가" - "보행 친화적 거리가 혁신을 촉진한다"

**출력:**
```
🔗 연결점: 공간 설계를 통한 행동 유도

💡 아이디어:
'워크 리워드' 앱. 걷기 친화적인 경로를 추천하되, 
그 경로에 있는 로컬 비즈니스와 제휴하여 보행 거리에 
따라 할인 쿠폰을 제공. 건강 + 지역 경제 활성화.

✅ 작동 이유:
1. 넛지 효과: 보상으로 걷기 행동 유도
2. 네트워크 효과: 지역 상점들이 참여할수록 가치 증가
3. 지속 가능성: 건강과 경제적 인센티브 동시 제공
```

## 🎯 베스트 프랙티스

1. **다양한 장르 확보**: 최소 3-4개 이상의 다른 분야 책을 읽어야 효과적
2. **구체적인 컨텍스트**: user_context를 구체적으로 작성할수록 실용적인 아이디어
3. **반복 생성**: 첫 번째 아이디어가 마음에 안 들면 여러 번 재생성
4. **팀 활용**: 워크샵이나 브레인스토밍 세션에서 활용
5. **실행 가능성 검증**: 생성된 아이디어를 실제로 실행 가능한지 검토

## ⚠️ 주의사항

- API 키 필수 (GOOGLE_API_KEY)
- Gemini API 무료 할당량: 1,500회/일
- 하이라이트가 최소 2개 이상 필요
- 너무 비슷한 분야는 흥미로운 연결이 어려울 수 있음

## 🔮 향후 확장 아이디어

1. **다중 연결**: 3-4개 개념을 동시에 연결
2. **이미지 생성**: 아이디어를 시각화한 이미지 자동 생성
3. **실행 계획**: 아이디어를 구체적인 액션 플랜으로 변환
4. **커뮤니티 투표**: 생성된 아이디어에 사용자들이 투표
5. **아이디어 저장소**: 좋은 아이디어를 북마크하고 공유

---

Made with 🧠 using Google Gemini API

세렌디피티를 통해 새로운 세계를 발견하세요! ✨


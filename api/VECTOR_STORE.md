# 🧠 벡터 저장소 (ChromaDB)

책의 하이라이트를 벡터로 저장하여 유사도 기반 검색과 책 간 연결을 찾는 시스템입니다.

## 🎯 기능

1. **하이라이트 벡터화**: 텍스트를 고차원 벡터로 변환
2. **유사도 검색**: 의미적으로 유사한 하이라이트 찾기
3. **책 간 연결**: 비슷한 주제나 개념을 다루는 책 발견
4. **로컬 저장**: persistent 모드로 데이터 영구 보관

## 📦 설치

```bash
cd api
pip install chromadb sentence-transformers
```

## 🚀 사용 방법

### 1. 임베딩 모델 선택

#### 옵션 A: 로컬 임베딩 (기본, 무료)

```bash
# 환경변수 설정 (선택)
export EMBEDDING_TYPE=local

# 서버 실행
uvicorn main:app --reload
```

**모델:** `sentence-transformers/all-MiniLM-L6-v2`
- ✅ 완전 무료
- ✅ 인터넷 없이 작동
- ✅ 빠름 (CPU 충분)
- ⚠️ 첫 실행 시 모델 다운로드 (90MB)

#### 옵션 B: Gemini 임베딩 (무료)

```bash
# 환경변수 설정
export EMBEDDING_TYPE=gemini
export GOOGLE_API_KEY='your-api-key'

# 서버 실행
uvicorn main:app --reload
```

**모델:** `text-embedding-004`
- ✅ 고품질 임베딩
- ✅ 무료 할당량: 1,500회/일
- ⚠️ API 키 필요
- ⚠️ 인터넷 필요

### 2. Python 코드

```python
from vector_store import get_vector_store

# VectorStore 인스턴스
store = get_vector_store()

# 하이라이트 추가
store.add_highlight(
    highlight_id=1,
    text="1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
    metadata={
        "book_id": 1,
        "book_title": "아주 작은 습관의 힘",
        "author": "제임스 클리어",
        "genre": "자기계발",
        "page": 15
    }
)

# 유사한 하이라이트 검색
similar = store.find_similar(
    text="점진적으로 개선하는 것이 중요하다",
    n=5
)

for item in similar:
    print(f"{item['text']} - {item['metadata']['book_title']}")

# 책 간 연결 찾기
connections = store.find_connections(book_id=1, n=3)
for conn in connections:
    print(f"{conn['book_title']} - {conn['connection_count']}개 연결점")
```

### 3. API 엔드포인트

#### GET /vector/similar

유사한 하이라이트 검색

```bash
curl "http://localhost:8000/vector/similar?text=작은%20습관의%20힘&n=5"
```

**Response:**
```json
{
  "query": "작은 습관의 힘",
  "count": 5,
  "results": [
    {
      "id": "highlight_1",
      "text": "1%의 개선이 매일 쌓이면...",
      "metadata": {
        "book_id": "1",
        "book_title": "아주 작은 습관의 힘",
        "author": "제임스 클리어",
        "genre": "자기계발",
        "page": "15"
      },
      "distance": 0.342
    }
  ]
}
```

#### GET /vector/connections/{book_id}

책 간 연결 찾기

```bash
curl "http://localhost:8000/vector/connections/1?n=3"
```

**Response:**
```json
{
  "book_id": 1,
  "book_title": "아주 작은 습관의 힘",
  "connections": [
    {
      "book_id": "3",
      "book_title": "티핑 포인트",
      "author": "말콤 글래드웰",
      "genre": "사회학",
      "connection_count": 5,
      "similar_highlights": [
        {
          "text": "작은 변화가 큰 차이를 만든다.",
          "page": "100"
        }
      ]
    }
  ]
}
```

#### GET /vector/stats

벡터 DB 통계

```bash
curl "http://localhost:8000/vector/stats"
```

**Response:**
```json
{
  "total_vectors": 42,
  "embedding_type": "local",
  "persist_directory": "./chroma_db"
}
```

## 🧪 테스트

```bash
cd api

# 독립 실행 테스트
python vector_store.py
```

**테스트 시나리오:**
1. 4개 하이라이트 추가
2. 유사도 검색 테스트
3. 책 간 연결 찾기

## 🔄 자동 통합

하이라이트를 추가하면 자동으로 벡터 DB에도 저장됩니다:

```bash
# POST /highlights 호출 시
# 1. SQLite에 저장
# 2. 벡터 DB에 자동 저장 ✨
curl -X POST "http://localhost:8000/highlights" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "original_text": "습관은 자아 정체성의 구체화다.",
    "page_number": 45
  }'
```

## 📊 활용 시나리오

### 1. 유사한 인사이트 발견

```python
# "복리 효과"에 대한 하이라이트 검색
results = store.find_similar("복리의 힘", n=10)

# 여러 책에서 비슷한 개념 발견
for result in results:
    print(f"📚 {result['metadata']['book_title']}")
    print(f"   {result['text']}")
```

### 2. 읽을 책 추천

```python
# 방금 읽은 책과 연결된 책 찾기
connections = store.find_connections(book_id=1, n=5)

print("다음에 읽을 책 추천:")
for conn in connections:
    print(f"📚 {conn['book_title']}")
    print(f"   이유: {conn['connection_count']}개의 유사한 개념")
```

### 3. 지식 맵 생성

```python
# 모든 책 간 연결 분석
knowledge_graph = {}

for book_id in [1, 2, 3, 4, 5]:
    connections = store.find_connections(book_id, n=10)
    knowledge_graph[book_id] = connections

# 지식 네트워크 시각화
```

### 4. 스마트 검색

```python
# 자연어로 검색
query = "생산성을 높이는 방법"
results = store.find_similar(query, n=5)

# 여러 책에서 관련 하이라이트 발견
```

## 🎨 프론트엔드 통합

```typescript
// 유사 하이라이트 검색
const searchSimilar = async (text: string) => {
  const response = await fetch(
    `/vector/similar?text=${encodeURIComponent(text)}&n=5`
  );
  const data = await response.json();
  return data.results;
};

// 연결된 책 찾기
const findConnections = async (bookId: number) => {
  const response = await fetch(`/vector/connections/${bookId}?n=3`);
  const data = await response.json();
  return data.connections;
};

// UI 예시
const HighlightCard = ({ highlight }) => {
  const [similar, setSimilar] = useState([]);
  
  const handleFindSimilar = async () => {
    const results = await searchSimilar(highlight.text);
    setSimilar(results);
    setShowModal(true);
  };
  
  return (
    <div>
      <p>{highlight.text}</p>
      <button onClick={handleFindSimilar}>
        🔍 유사한 하이라이트 찾기
      </button>
    </div>
  );
};

const BookDetail = ({ book }) => {
  const [connections, setConnections] = useState([]);
  
  useEffect(() => {
    findConnections(book.id).then(setConnections);
  }, [book.id]);
  
  return (
    <div>
      <h2>{book.title}</h2>
      
      <section>
        <h3>📚 연결된 책들</h3>
        {connections.map(conn => (
          <div key={conn.book_id}>
            <h4>{conn.book_title}</h4>
            <p>{conn.connection_count}개의 유사한 개념</p>
          </div>
        ))}
      </section>
    </div>
  );
};
```

## 📁 데이터 저장 위치

```
api/
├── chroma_db/           # 벡터 DB (persistent)
│   ├── highlights/      # 컬렉션 데이터
│   └── chroma.sqlite3   # 메타데이터
└── knowledge_debt.db    # SQLite DB
```

## 🔧 고급 설정

### 컬렉션 초기화

```python
store = get_vector_store()
store.reset()  # ⚠️ 모든 벡터 삭제
```

### 커스텀 설정

```python
from vector_store import VectorStore

# 커스텀 경로
store = VectorStore(
    collection_name="my_highlights",
    persist_directory="./my_vectors"
)
```

## 📊 성능

| 작업 | 로컬 (CPU) | Gemini API |
|------|------------|------------|
| 임베딩 | ~50ms | ~200ms |
| 검색 | ~10ms | ~10ms |
| 비용 | 무료 | 무료 (1500회/일) |

## 🐛 문제 해결

### 모델 다운로드 오류

```bash
# sentence-transformers 캐시 확인
ls ~/.cache/torch/sentence_transformers/

# 수동 다운로드
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Gemini API 오류

```bash
# API 키 확인
echo $GOOGLE_API_KEY

# 할당량 확인
# https://aistudio.google.com/app/apikey
```

### ChromaDB 오류

```bash
# 데이터베이스 재생성
rm -rf ./chroma_db
# 서버 재시작
```

## 🎉 활용 아이디어

1. **지식 그래프**: 책들 간의 연결을 시각화
2. **스마트 추천**: 읽은 책 기반으로 다음 책 추천
3. **자동 태깅**: 유사한 하이라이트끼리 자동 그룹화
4. **크로스 레퍼런스**: 다른 책에서 비슷한 내용 자동 발견
5. **AI 요약**: 여러 책의 유사 개념을 종합 요약

---

Made with 🧠 using ChromaDB


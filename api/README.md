# 지식 부채 관리 시스템 REST API

FastAPI로 구현한 지식 부채 관리 시스템의 백엔드 API입니다.

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
cd api
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
uvicorn main:app --reload --port 8000
```

또는

```bash
python main.py
```

### 3. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 API 엔드포인트

### 📚 Books (책 관리)

#### POST /books
새로운 책을 등록합니다.

**Request Body:**
```json
{
  "title": "클린 코드",
  "author": "로버트 C. 마틴",
  "genre": "프로그래밍",
  "page_count": 584,
  "cover_image_url": "https://example.com/cover.jpg"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "클린 코드",
  "author": "로버트 C. 마틴",
  "genre": "프로그래밍",
  "page_count": 584,
  "purchase_date": "2024-12-09",
  "created_at": "2024-12-09T10:00:00"
}
```

- 자동으로 부채 생성: `300 + (584 × 0.5) = 592pt`

#### GET /books
책 목록을 조회합니다.

**Query Parameters:**
- `status`: 상태 필터 (optional)
  - `debt`: 부채 + 상환중
  - `partial`: 상환중만
  - `asset`: 자산만
- `skip`: 페이지네이션 시작 (default: 0)
- `limit`: 페이지네이션 크기 (default: 100)

**Example:**
```bash
GET /books?status=debt&limit=10
```

#### GET /books/{id}
특정 책의 상세 정보를 조회합니다.

**Response:**
```json
{
  "id": 1,
  "title": "클린 코드",
  "author": "로버트 C. 마틴",
  "initial_debt_points": 592,
  "current_remaining_points": 392,
  "status": "partial",
  "progress_percentage": 33.8,
  "total_activities": 5,
  "total_highlights": 3,
  "activities": [...],
  "highlights": [...]
}
```

### ✨ Activities (활동 기록)

#### POST /activities
탕감 활동을 기록합니다.

**Request Body:**
```json
{
  "book_id": 1,
  "activity_type": "blog",
  "content": "블로그에 서평 작성 완료"
}
```

**Response:**
```json
{
  "id": 1,
  "book_id": 1,
  "activity_type": "blog",
  "reduction_points": -35,
  "content": "블로그에 서평 작성 완료",
  "activity_date": "2024-12-09",
  "created_at": "2024-12-09T10:30:00"
}
```

**활동 유형 및 포인트:**
- `read`: 10pt
- `highlight`: 20pt
- `feeling`: 20pt
- `diary`: 25pt
- `writing`: 30pt
- `quiz`: 30pt
- `recommend`: 30pt
- `visual`: 35pt
- `blog`: 35pt
- `connect`: 40pt
- `discussion`: 40pt
- `letter`: 40pt
- `study`: 45pt
- `action`: 50pt
- `video`: 50pt
- `presentation`: 50pt
- `project`: 60pt

### 📊 Dashboard (대시보드)

#### GET /dashboard
전체 통계를 조회합니다.

**Response:**
```json
{
  "total_books": 10,
  "debt_books": 4,
  "partial_books": 3,
  "asset_books": 3,
  "total_initial_debt": 5000,
  "total_remaining_debt": 2500,
  "total_mileage": 150,
  "overall_progress": 50.0,
  "asset_conversion_rate": 30.0
}
```

### ✏️ Highlights (하이라이트)

#### POST /highlights
하이라이트를 추가합니다.

**Request Body:**
```json
{
  "book_id": 1,
  "original_text": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
  "page_number": 23,
  "my_thoughts": "Later equals never."
}
```

- 자동으로 20pt 탕감
- 자동으로 'highlight' 활동 생성

#### GET /highlights/{book_id}
특정 책의 하이라이트 목록을 조회합니다.

**Example:**
```bash
GET /highlights/1
```

## 🔄 자동화 기능

### 1. 책 등록 시
- ✅ 자동으로 `debt_ledger` 레코드 생성
- ✅ 초기 부채 계산: `300 + (페이지수 × 0.5)`
- ✅ 초기 상태: `debt`

### 2. 활동 기록 시
- ✅ 활동 유형에 따른 포인트 자동 차감
- ✅ 부채 상태 자동 업데이트
  - `debt`: 잔여 > 50%
  - `partial`: 잔여 ≤ 50%
  - `asset`: 잔여 ≤ 0
- ✅ 0pt 미만 시 마일리지 자동 전환

### 3. 하이라이트 추가 시
- ✅ 자동으로 20pt 탕감
- ✅ 자동으로 'highlight' 활동 생성

## 🗄️ 데이터베이스

### SQLite
- 파일: `knowledge_debt.db`
- 테이블: `books`, `debt_ledger`, `activities`, `highlights`

### 스키마 자동 생성
서버 시작 시 자동으로 테이블이 생성됩니다.

## 🔗 CORS 설정

다음 origin에서의 요청을 허용합니다:
- `http://localhost:5173` (Vite)
- `http://localhost:3000` (Create React App)

추가 origin이 필요하면 `main.py`의 `allow_origins`를 수정하세요.

## 📝 예제 사용

### cURL

```bash
# 책 등록
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{"title":"클린 코드","author":"로버트 C. 마틴","page_count":584}'

# 책 목록 조회
curl "http://localhost:8000/books"

# 활동 기록
curl -X POST "http://localhost:8000/activities" \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"activity_type":"blog","content":"블로그 작성"}'

# 대시보드 통계
curl "http://localhost:8000/dashboard"
```

### Python

```python
import requests

# 책 등록
response = requests.post('http://localhost:8000/books', json={
    'title': '클린 코드',
    'author': '로버트 C. 마틴',
    'page_count': 584
})
print(response.json())

# 활동 기록
response = requests.post('http://localhost:8000/activities', json={
    'book_id': 1,
    'activity_type': 'blog',
    'content': '블로그 작성 완료'
})
print(response.json())
```

### JavaScript (React)

```javascript
// 책 등록
const addBook = async () => {
  const response = await fetch('http://localhost:8000/books', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: '클린 코드',
      author: '로버트 C. 마틴',
      page_count: 584
    })
  });
  const data = await response.json();
  console.log(data);
};

// 책 목록 조회
const fetchBooks = async () => {
  const response = await fetch('http://localhost:8000/books');
  const books = await response.json();
  console.log(books);
};
```

## 🧪 테스트

Swagger UI(http://localhost:8000/docs)에서 각 엔드포인트를 테스트할 수 있습니다.

## 📄 라이선스

MIT


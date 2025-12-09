# 환경 변수 설정 가이드

## 🔑 Google Gemini API 키 발급

1. **Google AI Studio 접속**
   - 링크: https://aistudio.google.com/app/apikey

2. **API 키 생성**
   - "Create API Key" 버튼 클릭
   - 프로젝트 선택 또는 새 프로젝트 생성
   - API 키 복사

3. **무료 할당량**
   - **gemini-2.0-flash-exp**: 분당 15회, 일당 1,500회
   - **text-embedding-004**: 분당 1,500회, 일당 100,000회

## ⚙️ 설정 방법

### 1. .env 파일 생성

```bash
cd api
cp .env.example .env
```

### 2. API 키 입력

`.env` 파일을 열어서 발급받은 API 키를 입력하세요:

```bash
GOOGLE_API_KEY=AIzaSyA...your_actual_api_key_here
EMBEDDING_TYPE=local
```

### 3. 서버 재시작

```bash
# 서버가 실행 중이면 중지 (Ctrl+C)
# 다시 시작
python3 -m uvicorn main:app --reload --port 8000
```

## 🧪 API 키 테스트

### 방법 1: Connection Agent 테스트

```bash
cd api
export GOOGLE_API_KEY='your_api_key_here'
python3 connection_agent.py
```

### 방법 2: API 엔드포인트 호출

```bash
# 행동 제안 테스트
curl -X POST "http://localhost:8000/ai/suggest-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "highlight_id": 1,
    "user_context": "테스트"
  }'
```

## 📋 사용되는 기능

### Gemini API가 필요한 기능:

1. **POST /ai/suggest-actions**
   - 하이라이트 기반 행동 제안
   - 모델: `gemini-2.0-flash-exp`

2. **POST /ai/connect-ideas**
   - 두 하이라이트 연결하여 아이디어 생성
   - 모델: `gemini-2.0-flash-exp`

3. **POST /ai/mix-ideas**
   - 두 책 연결하여 아이디어 생성
   - 모델: `gemini-2.0-flash-exp`

4. **벡터 임베딩 (선택 사항)**
   - EMBEDDING_TYPE=gemini로 설정 시
   - 모델: `text-embedding-004`

## 🔒 보안 주의사항

1. **절대 공개하지 마세요**
   - `.env` 파일은 절대 Git에 커밋하지 않습니다
   - `.gitignore`에 이미 추가되어 있습니다

2. **API 키 노출 시**
   - Google AI Studio에서 즉시 키를 삭제하세요
   - 새 키를 발급받으세요

3. **할당량 관리**
   - 무료 티어 제한을 초과하지 않도록 주의
   - AI Studio에서 사용량 모니터링 가능

## 🆓 무료 대안

API 키가 없어도 사용 가능한 기능:

1. **로컬 임베딩**
   ```bash
   EMBEDDING_TYPE=local
   ```
   - sentence-transformers 사용
   - 인터넷 연결 불필요
   - 완전 무료

2. **기본 CRUD 기능**
   - 책 등록/조회/삭제
   - 활동 기록
   - 하이라이트 추가
   - 대시보드 통계

3. **벡터 검색**
   - 유사한 하이라이트 찾기
   - 책 간 연결 찾기
   - Random Mix

## ❓ 문제 해결

### "GOOGLE_API_KEY not set" 오류

```bash
# 환경 변수가 제대로 로드되지 않은 경우
cd api

# .env 파일 확인
cat .env

# 직접 환경 변수 설정
export GOOGLE_API_KEY='your_api_key'

# 서버 재시작
python3 -m uvicorn main:app --reload --port 8000
```

### "Invalid API key" 오류

1. API 키가 올바른지 확인
2. Google AI Studio에서 키가 활성화되어 있는지 확인
3. 키에 공백이나 특수문자가 없는지 확인

### "Quota exceeded" 오류

1. Google AI Studio에서 사용량 확인
2. 내일까지 대기 (일일 제한)
3. 또는 새 프로젝트에서 새 키 발급

## 📚 추가 정보

- **Google AI Studio**: https://aistudio.google.com
- **Gemini API 문서**: https://ai.google.dev/docs
- **가격 정책**: https://ai.google.dev/pricing

---

궁금한 점이 있으면 API 문서를 참고하세요! 🚀


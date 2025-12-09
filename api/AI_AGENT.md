# 🤖 탕감 행동 제안 AI 에이전트

Google Gemini API를 사용한 지능형 독서 코치 에이전트입니다.

## 🎯 기능

책에서 밑줄 친 문장을 분석하여:
- 💡 당장 내일 실행 가능한 구체적인 행동 3가지 제안
- 🎨 사용자 직업/상황에 맞춘 개인화
- ⏱️ 각 행동의 소요시간, 난이도, 활동 유형 포함
- 🎯 물리적이고 측정 가능한 행동만 제안

## 🚀 설정

### 1. API 키 발급

1. [Google AI Studio](https://aistudio.google.com) 접속
2. 무료 API 키 발급 (로그인 필요)
3. API 키 복사

### 2. 환경변수 설정

```bash
# Linux/Mac
export GOOGLE_API_KEY='your-api-key-here'

# Windows (PowerShell)
$env:GOOGLE_API_KEY='your-api-key-here'

# 또는 .env 파일 생성
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

### 3. 의존성 설치

```bash
pip install google-generativeai
```

## 📊 사용 가능한 모델

| 모델 | 속도 | 무료 한도 | 용도 |
|------|------|-----------|------|
| gemini-2.0-flash-exp | ⚡ 빠름 | 분당 15회, 일당 1,500회 | 일반 사용 (권장) |
| gemini-2.5-pro | 🎯 정확 | 분당 2회, 일당 50회 | 고품질 제안 |

## 🔧 사용 방법

### 1. Python 스크립트

```python
from ai_agent import create_agent

# 에이전트 생성
agent = create_agent()

# 행동 제안 생성
result = agent.suggest_and_format(
    book_title="아주 작은 습관의 힘",
    highlight_text="1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
    user_context="소프트웨어 엔지니어, 재택근무"
)

print(result)
```

### 2. 명령줄 테스트

```bash
cd api
python ai_agent.py
```

### 3. FastAPI 엔드포인트

```bash
# 서버 실행
uvicorn main:app --reload

# API 호출
curl -X POST "http://localhost:8000/ai/suggest-actions" \
  -H "Content-Type: application/json" \
  -d '{
    "book_title": "아주 작은 습관의 힘",
    "highlight_text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
    "user_context": "소프트웨어 엔지니어"
  }'
```

## 📋 응답 형식

```json
{
  "book_title": "아주 작은 습관의 힘",
  "highlight": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
  "user_context": "소프트웨어 엔지니어",
  "suggestions": [
    {
      "action": "오늘부터 매일 아침 독서 10분을 스마트폰 알람으로 설정하고, 체크리스트 앱에 기록한다",
      "duration": "10분",
      "difficulty": "쉬움",
      "activity_type": "action",
      "estimated_points": 50
    },
    {
      "action": "지난 달과 이번 달의 코드 리뷰 횟수를 비교해서 1% 개선 여부를 엑셀로 계산하고 그래프로 시각화한다",
      "duration": "30분",
      "difficulty": "보통",
      "activity_type": "visual",
      "estimated_points": 35
    },
    {
      "action": "팀 스탠드업 미팅에서 '작은 습관의 복리 효과'를 주제로 5분간 발표하고, 각자의 1% 개선 목표를 공유한다",
      "duration": "15분",
      "difficulty": "보통",
      "activity_type": "presentation",
      "estimated_points": 50
    }
  ]
}
```

## 🎨 활동 유형 및 포인트

| 유형 | 포인트 | 설명 |
|------|--------|------|
| action | 50pt | 직접 실천/적용 |
| presentation | 50pt | 발표/프레젠테이션 |
| study | 45pt | 스터디/학습 |
| discussion | 40pt | 토론/대화 |
| visual | 35pt | 시각화/정리 |
| blog | 35pt | 블로그 작성 |
| writing | 30pt | 글쓰기/서평 |
| diary | 25pt | 독서일지 |

## 💡 예제

### 예제 1: 자기계발

**입력:**
```json
{
  "book_title": "아주 작은 습관의 힘",
  "highlight_text": "환경을 설계하라. 의지력에 의존하지 마라.",
  "user_context": "직장인, 다이어트 중"
}
```

**출력 예시:**
1. 냉장고 정리 (10분, 쉬움, action, 50pt)
2. 운동복을 현관에 배치 (5분, 쉬움, action, 50pt)
3. 환경 설계 블로그 작성 (30분, 보통, blog, 35pt)

### 예제 2: 기술서적

**입력:**
```json
{
  "book_title": "클린 코드",
  "highlight_text": "함수는 한 가지 일을 해야 한다.",
  "user_context": "주니어 개발자"
}
```

**출력 예시:**
1. 최근 작성한 함수 리팩토링 (1시간, 보통, action, 50pt)
2. 팀원과 함수 설계 토론 (20분, 보통, discussion, 40pt)
3. 리팩토링 전후 비교 블로그 작성 (45분, 보통, blog, 35pt)

## 🔒 보안 주의사항

- ⚠️ API 키는 절대 코드에 하드코딩하지 마세요
- ⚠️ .env 파일은 .gitignore에 추가하세요
- ⚠️ 프로덕션에서는 환경변수나 비밀 관리 도구 사용

## 🐛 문제 해결

### API 키 오류
```
❌ GOOGLE_API_KEY 환경변수가 설정되지 않았습니다
```

**해결:** 환경변수 설정 확인
```bash
echo $GOOGLE_API_KEY  # Linux/Mac
echo %GOOGLE_API_KEY%  # Windows
```

### JSON 파싱 오류
```
❌ JSON 파싱 실패
```

**원인:** Gemini가 JSON 외 텍스트 포함
**해결:** 프롬프트에 "반드시 JSON만 출력" 강조

### 할당량 초과
```
❌ 429 Too Many Requests
```

**원인:** 무료 할당량 초과 (분당 15회)
**해결:** 
- 요청 간격 늘리기
- gemini-2.5-pro로 변경 (분당 2회)
- 24시간 후 재시도

## 📚 참고 문서

- [Google AI Studio](https://aistudio.google.com)
- [Gemini API 문서](https://ai.google.dev/docs)
- [Python SDK](https://github.com/google/generative-ai-python)

## 🎉 활용 아이디어

1. **자동 활동 생성**: 하이라이트 추가 시 자동으로 행동 제안
2. **일일 추천**: 매일 아침 미완료 책의 하이라이트 기반 행동 추천
3. **진행률 부스트**: 부채가 많은 책에 AI 제안으로 빠른 탕감
4. **개인화 코칭**: 사용자 이력 분석하여 맞춤 제안
5. **소셜 기능**: 제안된 행동을 친구와 공유

---

Made with ❤️ using Google Gemini API


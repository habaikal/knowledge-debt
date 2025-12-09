import os
import json
from typing import Optional, List
import google.generativeai as genai
from pydantic import BaseModel

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# ============================================
# Pydantic 모델
# ============================================

class ActionSuggestion(BaseModel):
    """행동 제안 모델"""
    action: str  # 행동 설명
    duration: str  # 예상 소요시간 (예: "10분", "30분", "1시간")
    difficulty: str  # 난이도 (쉬움, 보통, 어려움)
    activity_type: str  # 활동 유형 (action, writing, discussion 등)


class AgentRequest(BaseModel):
    """에이전트 요청 모델"""
    book_title: str
    highlight_text: str
    user_context: Optional[str] = None  # 사용자 직업/상황


class AgentResponse(BaseModel):
    """에이전트 응답 모델"""
    suggestions: List[ActionSuggestion]
    raw_response: Optional[str] = None


# ============================================
# 시스템 프롬프트
# ============================================

SYSTEM_PROMPT = """너는 20년 경력의 독서 코치야. 
사용자가 책에서 밑줄 친 문장을 보내면, 그 문장을 바탕으로 당장 내일 실행할 수 있는 구체적인 행동 3가지를 제안해.

**중요 규칙:**
1. 행동은 반드시 물리적이고 측정 가능해야 해
2. "생각한다", "고민한다" 같은 추상적 행동은 금지
3. 각 행동은 구체적인 동사로 시작 (예: "작성한다", "측정한다", "기록한다")
4. 사용자의 직업이나 상황이 주어지면 그에 맞춰 개인화해줘
5. 각 행동에 적합한 활동 유형을 선택해줘

**활동 유형 종류:**
- action: 직접 실천/적용 (50pt)
- writing: 글쓰기/서평 (30pt)
- discussion: 토론/대화 (40pt)
- study: 스터디/학습 (45pt)
- visual: 시각화/정리 (35pt)
- blog: 블로그 작성 (35pt)
- diary: 독서일지 (25pt)

**응답 형식 (반드시 JSON으로만 답변):**
```json
{
  "suggestions": [
    {
      "action": "구체적인 행동 설명",
      "duration": "예상 소요시간",
      "difficulty": "난이도",
      "activity_type": "활동 유형"
    }
  ]
}
```

예시 - 입력: "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다."
예시 - 출력:
```json
{
  "suggestions": [
    {
      "action": "오늘부터 매일 아침 독서 10분을 스마트폰 알람으로 설정하고, 체크리스트 앱에 기록한다",
      "duration": "10분",
      "difficulty": "쉬움",
      "activity_type": "action"
    },
    {
      "action": "지난 달과 이번 달의 운동 기록을 비교해서 1% 개선 여부를 엑셀로 계산하고 그래프로 시각화한다",
      "duration": "30분",
      "difficulty": "보통",
      "activity_type": "visual"
    },
    {
      "action": "팀원들과 점심시간에 '작은 습관의 복리 효과'를 주제로 15분간 토론하고, 각자의 1% 개선 목표를 공유한다",
      "duration": "15분",
      "difficulty": "보통",
      "activity_type": "discussion"
    }
  ]
}
```

이제 사용자의 밑줄 문장을 분석하고 행동을 제안해줘."""


# ============================================
# 에이전트 클래스
# ============================================

class DebtReductionAgent:
    """탕감 행동 제안 에이전트"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Args:
            model_name: 사용할 Gemini 모델
                - gemini-2.0-flash-exp: 빠르고 무료 (분당 15회)
                - gemini-2.5-pro: 고성능 (분당 2회)
        """
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다")
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
    
    def generate_suggestions(
        self,
        book_title: str,
        highlight_text: str,
        user_context: Optional[str] = None
    ) -> AgentResponse:
        """
        밑줄 문장을 바탕으로 행동 제안 생성
        
        Args:
            book_title: 책 제목
            highlight_text: 밑줄 친 문장
            user_context: 사용자 직업/상황 (선택)
        
        Returns:
            AgentResponse: 행동 제안 목록
        """
        # 프롬프트 구성
        user_prompt = f"""
**책 제목:** {book_title}

**밑줄 친 문장:**
"{highlight_text}"
"""
        
        if user_context:
            user_prompt += f"""
**사용자 상황:**
{user_context}
"""
        
        user_prompt += """

위 문장을 바탕으로 당장 내일 실행 가능한 구체적인 행동 3가지를 JSON 형식으로 제안해줘.
반드시 JSON만 출력하고, 다른 설명은 하지 마."""
        
        try:
            # Gemini API 호출
            response = self.model.generate_content(
                [SYSTEM_PROMPT, user_prompt]
            )
            
            raw_text = response.text.strip()
            
            # JSON 추출 (코드 블록 제거)
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
            # JSON 파싱
            data = json.loads(raw_text)
            suggestions = [ActionSuggestion(**item) for item in data["suggestions"]]
            
            return AgentResponse(
                suggestions=suggestions,
                raw_response=response.text
            )
        
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {e}\n응답: {response.text}")
        except Exception as e:
            raise ValueError(f"에이전트 실행 실패: {e}")
    
    def suggest_and_format(
        self,
        book_title: str,
        highlight_text: str,
        user_context: Optional[str] = None
    ) -> dict:
        """
        행동 제안을 생성하고 보기 좋게 포맷팅
        
        Returns:
            dict: 포맷팅된 결과
        """
        result = self.generate_suggestions(book_title, highlight_text, user_context)
        
        return {
            "book_title": book_title,
            "highlight": highlight_text,
            "user_context": user_context,
            "suggestions": [
                {
                    "action": s.action,
                    "duration": s.duration,
                    "difficulty": s.difficulty,
                    "activity_type": s.activity_type,
                    "estimated_points": self._get_points_for_type(s.activity_type)
                }
                for s in result.suggestions
            ]
        }
    
    @staticmethod
    def _get_points_for_type(activity_type: str) -> int:
        """활동 유형별 포인트 반환"""
        points_map = {
            'read': 10, 'highlight': 20, 'feeling': 20, 'diary': 25,
            'writing': 30, 'quiz': 30, 'recommend': 30,
            'visual': 35, 'blog': 35,
            'connect': 40, 'discussion': 40, 'letter': 40,
            'study': 45, 'action': 50, 'video': 50, 'presentation': 50,
            'project': 60,
        }
        return points_map.get(activity_type, 20)


# ============================================
# 헬퍼 함수
# ============================================

def create_agent(model_name: str = "gemini-2.0-flash-exp") -> DebtReductionAgent:
    """에이전트 인스턴스 생성"""
    return DebtReductionAgent(model_name=model_name)


# ============================================
# 테스트 코드
# ============================================

if __name__ == "__main__":
    # 환경변수 확인
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY 환경변수를 설정해주세요")
        print("   export GOOGLE_API_KEY='your-api-key'")
        exit(1)
    
    print("🤖 탕감 행동 제안 에이전트 테스트\n")
    
    # 에이전트 생성
    agent = create_agent()
    
    # 테스트 케이스
    test_cases = [
        {
            "book_title": "아주 작은 습관의 힘",
            "highlight": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
            "context": "소프트웨어 엔지니어, 재택근무"
        },
        {
            "book_title": "클린 코드",
            "highlight": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
            "context": "주니어 개발자, 스타트업 재직"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"📚 테스트 {i}: {test['book_title']}")
        print(f"💭 밑줄: {test['highlight']}")
        print(f"👤 상황: {test['context']}\n")
        
        try:
            result = agent.suggest_and_format(
                book_title=test['book_title'],
                highlight_text=test['highlight'],
                user_context=test['context']
            )
            
            print("✨ 제안된 행동:")
            for j, suggestion in enumerate(result['suggestions'], 1):
                print(f"\n{j}. {suggestion['action']}")
                print(f"   ⏱️  소요시간: {suggestion['duration']}")
                print(f"   📊 난이도: {suggestion['difficulty']}")
                print(f"   🎯 활동 유형: {suggestion['activity_type']} (-{suggestion['estimated_points']}pt)")
            
            print("\n" + "="*80 + "\n")
        
        except Exception as e:
            print(f"❌ 오류 발생: {e}\n")


"""
의미적 브릿지 에이전트
두 책의 하이라이트를 연결해서 새로운 인사이트를 생성
"""
import os
import json
from typing import Optional, Dict
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


# ============================================
# Pydantic 모델
# ============================================

class HighlightInfo(BaseModel):
    """하이라이트 정보"""
    text: str
    book_title: str
    author: str
    genre: str


class MixRequest(BaseModel):
    """Mix 요청 모델"""
    highlight_a: HighlightInfo
    highlight_b: HighlightInfo
    similarity_score: float


class MixResult(BaseModel):
    """Mix 결과 모델"""
    connection_point: str  # 두 개념의 공통 주제
    new_idea: str  # 구체적인 아이디어/인사이트
    why_it_works: str  # 이 연결이 의미 있는 이유
    action_suggestion: str  # 실천 가능한 다음 단계


# ============================================
# 시스템 프롬프트
# ============================================

SYSTEM_PROMPT = """너는 창의적 사고 전문가야. 서로 다른 분야의 두 책에서 의미적으로 연결된 개념들을 받으면,
이 둘의 교차점에서 새로운 비즈니스 아이디어나 인사이트를 만들어내.

**너의 임무:**
1. 두 하이라이트에서 공통된 핵심 주제나 패턴을 찾아
2. 이 공통점을 바탕으로 새롭고 실용적인 아이디어를 제안해
3. 왜 이 연결이 의미 있는지 설명해
4. 당장 실천할 수 있는 구체적인 행동을 제안해

**규칙:**
- 아이디어는 반드시 구체적이고 실행 가능해야 해
- 두 개념의 교차점에서 나온 통찰이어야 해
- 억지스러운 연결보다는 실제로 적용 가능한 인사이트를 찾아

**응답 형식 (반드시 JSON으로만 답변):**
```json
{
  "connection_point": "두 개념이 만나는 공통 주제",
  "new_idea": "이 교차점에서 발견한 구체적인 아이디어나 인사이트",
  "why_it_works": "이 연결이 왜 의미 있고 실용적인지",
  "action_suggestion": "이 인사이트를 바탕으로 당장 할 수 있는 구체적인 행동"
}
```
"""


# ============================================
# Mix 에이전트 클래스
# ============================================

class MixAgent:
    """의미적 브릿지 에이전트"""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=SYSTEM_PROMPT
        )

    def generate_connection(self, request: MixRequest) -> Optional[MixResult]:
        """두 하이라이트의 연결점과 인사이트 생성"""
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다")

        # 프롬프트 구성
        prompt = f"""
다음 두 책에서 발췌한 하이라이트를 연결해줘.

**책 A: {request.highlight_a.book_title}** (저자: {request.highlight_a.author}, 장르: {request.highlight_a.genre})
> "{request.highlight_a.text}"

**책 B: {request.highlight_b.book_title}** (저자: {request.highlight_b.author}, 장르: {request.highlight_b.genre})
> "{request.highlight_b.text}"

의미적 유사도: {request.similarity_score:.2%}

이 두 개념의 교차점에서 어떤 새로운 인사이트를 발견할 수 있을까?
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # JSON 파싱
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            result_dict = json.loads(json_str)

            return MixResult(
                connection_point=result_dict.get("connection_point", ""),
                new_idea=result_dict.get("new_idea", ""),
                why_it_works=result_dict.get("why_it_works", ""),
                action_suggestion=result_dict.get("action_suggestion", "")
            )

        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"원본 응답: {response_text}")
            raise ValueError(f"AI 응답 파싱 실패: {e}")
        except Exception as e:
            print(f"Mix 생성 실패: {e}")
            raise


# 싱글톤 인스턴스
_mix_agent: Optional[MixAgent] = None


def get_mix_agent() -> MixAgent:
    """Mix 에이전트 인스턴스 반환"""
    global _mix_agent
    if _mix_agent is None:
        _mix_agent = MixAgent()
    return _mix_agent

"""
두 책의 하이라이트를 연결해서 새로운 아이디어를 생성하는 에이전트
세렌디피티(우연한 발견)를 통한 창의적 사고 촉진
"""
import os
import json
from typing import Dict, Optional
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if not GOOGLE_API_KEY:
    print("⚠️  GOOGLE_API_KEY not set. Connection agent will not work.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)


class ConnectionAgent:
    """두 하이라이트를 연결해서 새로운 아이디어를 생성하는 에이전트"""
    
    SYSTEM_PROMPT = """너는 20년 경력의 창의적 사고 전문가야.

**당신의 역할:**
전혀 다른 분야의 두 책에서 뽑은 개념을 받으면, 이 둘을 강제로 연결해서 
새로운 비즈니스 아이디어나 인사이트를 만들어내는 것이다.

**중요 원칙:**
1. 연결이 억지스러워 보여도 괜찮다 - 세렌디피티(우연한 발견)가 목적이다
2. 구체적이고 실행 가능한 아이디어를 제시하라
3. "왜 이게 작동할 수 있는지" 논리적 근거를 제시하라
4. 기존에 없던 새로운 관점을 제시하라

**출력 형식 (JSON):**
{
  "connection_point": "두 개념을 연결하는 핵심 고리 (한 문장)",
  "new_idea": "새로운 비즈니스 아이디어 또는 인사이트 (구체적으로 2-3문장)",
  "why_it_works": "이 아이디어가 작동할 수 있는 이유 (논리적 근거 3가지)",
  "example": "실제 적용 예시 (선택, 있으면 좋음)"
}

**예시:**
책A: "아주 작은 습관의 힘" - "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다"
책B: "도시는 무엇으로 사는가" - "도시의 밀도가 높을수록 혁신이 일어난다"

출력:
{
  "connection_point": "점진적 축적과 밀도 효과의 결합",
  "new_idea": "개인 학습 데이터를 매일 1% 축적하되, 다양한 분야의 사람들과 밀집된 네트워크를 형성하는 '하이브리드 학습 플랫폼'. 매일 10분 마이크로 러닝 + 다른 분야 학습자 3명과 강제 매칭하여 크로스 인사이트를 공유하게 만든다.",
  "why_it_works": [
    "복리 효과: 매일의 작은 학습이 축적되어 지수적 성장",
    "밀도 효과: 다양한 분야 사람들의 아이디어 충돌로 혁신 촉진",
    "강제 연결: 우연한 만남을 시스템화하여 세렌디피티 창출"
  ],
  "example": "개발자가 요리사, 디자이너와 매칭되어 '요리 레시피를 코드처럼 버전 관리하는 앱' 아이디어 도출"
}

**주의사항:**
- 반드시 JSON 형식으로만 출력하라
- 창의적이되 현실 가능성도 고려하라
- 너무 뻔한 연결은 피하라
"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Args:
            model_name: 사용할 Gemini 모델
        """
        self.model_name = model_name
        if GOOGLE_API_KEY:
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 1.2,  # 높은 창의성
                    "top_p": 0.95,
                    "top_k": 40,
                }
            )
        else:
            self.model = None
    
    def connect_ideas(
        self,
        highlight_a: Dict,
        highlight_b: Dict,
        user_context: Optional[str] = None
    ) -> Dict:
        """
        두 하이라이트를 연결해서 새로운 아이디어 생성
        
        Args:
            highlight_a: {
                "text": str,
                "book_title": str,
                "author": str,
                "genre": str
            }
            highlight_b: 동일 형식
            user_context: 사용자 상황 (선택)
        
        Returns:
            {
                "connection_point": str,
                "new_idea": str,
                "why_it_works": List[str],
                "example": str (optional)
            }
        """
        if not self.model:
            raise Exception("GOOGLE_API_KEY not set")
        
        # 프롬프트 구성
        user_prompt = f"""
**책 A:**
- 제목: {highlight_a['book_title']}
- 저자: {highlight_a['author']}
- 장르: {highlight_a['genre']}
- 하이라이트: "{highlight_a['text']}"

**책 B:**
- 제목: {highlight_b['book_title']}
- 저자: {highlight_b['author']}
- 장르: {highlight_b['genre']}
- 하이라이트: "{highlight_b['text']}"
"""
        
        if user_context:
            user_prompt += f"\n**사용자 상황:**\n{user_context}\n"
        
        user_prompt += "\n위 두 개념을 연결해서 새로운 아이디어를 만들어줘. JSON 형식으로 출력해."
        
        try:
            # Gemini API 호출
            response = self.model.generate_content(
                [self.SYSTEM_PROMPT, user_prompt]
            )
            
            # JSON 파싱
            result_text = response.text.strip()
            
            # JSON 블록 추출 (```json ... ``` 제거)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            # why_it_works를 리스트로 변환 (문자열로 온 경우)
            if isinstance(result.get('why_it_works'), str):
                result['why_it_works'] = [result['why_it_works']]
            
            return result
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw response: {response.text}")
            
            # 파싱 실패 시 기본 구조 반환
            return {
                "connection_point": "두 개념의 연결",
                "new_idea": response.text[:200] if response.text else "아이디어 생성 실패",
                "why_it_works": ["응답 파싱 실패"],
                "raw_response": response.text
            }
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


# 싱글톤 인스턴스
_connection_agent = None

def get_connection_agent() -> ConnectionAgent:
    """ConnectionAgent 싱글톤 인스턴스"""
    global _connection_agent
    if _connection_agent is None:
        _connection_agent = ConnectionAgent()
    return _connection_agent


# ============================================
# 테스트
# ============================================

if __name__ == "__main__":
    print("🧪 ConnectionAgent 테스트\n")
    
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_API_KEY가 설정되지 않았습니다.")
        print("   export GOOGLE_API_KEY='your-api-key'")
        exit(1)
    
    agent = ConnectionAgent()
    
    # 테스트 데이터: 완전히 다른 분야
    highlight_a = {
        "text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
        "book_title": "아주 작은 습관의 힘",
        "author": "제임스 클리어",
        "genre": "자기계발"
    }
    
    highlight_b = {
        "text": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
        "book_title": "클린 코드",
        "author": "로버트 C. 마틴",
        "genre": "프로그래밍"
    }
    
    print("📚 책 A:", highlight_a['book_title'])
    print(f"   \"{highlight_a['text']}\"\n")
    
    print("📚 책 B:", highlight_b['book_title'])
    print(f"   \"{highlight_b['text']}\"\n")
    
    print("🔗 아이디어 연결 중...\n")
    
    try:
        result = agent.connect_ideas(
            highlight_a=highlight_a,
            highlight_b=highlight_b,
            user_context="스타트업 창업을 준비 중"
        )
        
        print("✨ 새로운 아이디어:\n")
        print(f"🔗 연결점: {result['connection_point']}\n")
        print(f"💡 아이디어:\n{result['new_idea']}\n")
        print(f"✅ 작동 이유:")
        for i, reason in enumerate(result['why_it_works'], 1):
            print(f"   {i}. {reason}")
        
        if 'example' in result and result['example']:
            print(f"\n📌 예시: {result['example']}")
        
        print("\n✅ 테스트 완료!")
    
    except Exception as e:
        print(f"❌ 에러: {e}")


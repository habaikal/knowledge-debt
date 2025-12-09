"""
AI 에이전트 전체 플로우 테스트
"""
import requests
import os

BASE_URL = "http://localhost:8000"

def test_full_ai_flow():
    """
    전체 플로우 테스트:
    1. 책 등록
    2. 하이라이트 추가
    3. AI 행동 제안 요청
    4. 제안된 행동 실행
    5. 부채 확인
    """
    
    print("🚀 AI 에이전트 전체 플로우 테스트 시작\n")
    
    # API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY 환경변수를 설정해주세요")
        print("   export GOOGLE_API_KEY='your-api-key'")
        return
    
    # 1. 책 등록
    print("📚 1. 책 등록")
    book_response = requests.post(f"{BASE_URL}/books", json={
        "title": "아주 작은 습관의 힘",
        "author": "제임스 클리어",
        "genre": "자기계발",
        "page_count": 400
    })
    
    if book_response.status_code != 200:
        print(f"❌ 책 등록 실패: {book_response.text}")
        return
    
    book = book_response.json()
    book_id = book["id"]
    print(f"✅ 책 등록 완료 (ID: {book_id})")
    print(f"   초기 부채: {300 + 400 * 0.5}pt\n")
    
    # 2. 하이라이트 추가
    print("✏️  2. 하이라이트 추가")
    highlight_response = requests.post(f"{BASE_URL}/highlights", json={
        "book_id": book_id,
        "original_text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
        "page_number": 15,
        "my_thoughts": "복리의 힘을 습관에 적용한 개념"
    })
    
    if highlight_response.status_code != 200:
        print(f"❌ 하이라이트 추가 실패: {highlight_response.text}")
        return
    
    highlight = highlight_response.json()
    highlight_id = highlight["id"]
    print(f"✅ 하이라이트 추가 완료 (ID: {highlight_id})")
    print(f"   자동 탕감: -20pt\n")
    
    # 3. AI 행동 제안 요청
    print("🤖 3. AI 행동 제안 요청")
    suggest_response = requests.post(f"{BASE_URL}/ai/suggest-actions", json={
        "book_id": book_id,
        "highlight_id": highlight_id,
        "user_context": "소프트웨어 엔지니어, 재택근무, 생산성 향상에 관심"
    })
    
    if suggest_response.status_code != 200:
        print(f"❌ AI 제안 실패: {suggest_response.text}")
        return
    
    suggestions = suggest_response.json()
    print(f"✅ AI 제안 완료")
    print(f"   책: {suggestions['book_title']}")
    print(f"   밑줄: {suggestions['highlight_text'][:50]}...\n")
    
    print("💡 제안된 행동:")
    for i, suggestion in enumerate(suggestions['suggestions'], 1):
        print(f"\n{i}. {suggestion['action']}")
        print(f"   ⏱️  소요시간: {suggestion['duration']}")
        print(f"   📊 난이도: {suggestion['difficulty']}")
        print(f"   🎯 활동 유형: {suggestion['activity_type']}")
        print(f"   💰 예상 탕감: {suggestion['estimated_points']}pt")
    
    # 4. 첫 번째 제안 실행
    print("\n\n🎯 4. 첫 번째 제안 실행")
    selected_suggestion = suggestions['suggestions'][0]
    
    execute_response = requests.post(f"{BASE_URL}/ai/execute-action", json={
        "book_id": book_id,
        "suggestion": selected_suggestion
    })
    
    if execute_response.status_code != 200:
        print(f"❌ 행동 실행 실패: {execute_response.text}")
        return
    
    activity = execute_response.json()
    print(f"✅ 행동 실행 완료 (Activity ID: {activity['id']})")
    print(f"   활동: {activity['activity_type']}")
    print(f"   탕감: {activity['reduction_points']}pt\n")
    
    # 5. 최종 부채 확인
    print("📊 5. 최종 상태 확인")
    book_detail_response = requests.get(f"{BASE_URL}/books/{book_id}")
    
    if book_detail_response.status_code != 200:
        print(f"❌ 상태 조회 실패: {book_detail_response.text}")
        return
    
    book_detail = book_detail_response.json()
    print(f"✅ 현재 상태:")
    print(f"   초기 부채: {book_detail['initial_debt_points']}pt")
    print(f"   현재 부채: {book_detail['current_remaining_points']}pt")
    print(f"   진행률: {book_detail['progress_percentage']:.1f}%")
    print(f"   상태: {book_detail['status']}")
    print(f"   총 활동: {book_detail['total_activities']}회")
    print(f"   하이라이트: {book_detail['total_highlights']}개")
    
    print("\n" + "="*80)
    print("🎉 전체 플로우 테스트 완료!")
    print("="*80)


def test_suggest_only():
    """제안만 테스트 (이미 생성된 데이터 사용)"""
    print("🤖 AI 제안 테스트\n")
    
    # 기존 책과 하이라이트 사용 (ID는 실제 데이터에 맞게 조정)
    book_id = 1
    highlight_id = 1
    
    suggest_response = requests.post(f"{BASE_URL}/ai/suggest-actions", json={
        "book_id": book_id,
        "highlight_id": highlight_id,
        "user_context": "프리랜서 디자이너, 크리에이티브 작업"
    })
    
    if suggest_response.status_code == 200:
        suggestions = suggest_response.json()
        print("✨ 제안된 행동:")
        for i, suggestion in enumerate(suggestions['suggestions'], 1):
            print(f"\n{i}. {suggestion['action']}")
            print(f"   ⏱️  {suggestion['duration']}")
            print(f"   📊 {suggestion['difficulty']}")
            print(f"   💰 {suggestion['estimated_points']}pt")
    else:
        print(f"❌ 오류: {suggest_response.text}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "suggest":
        test_suggest_only()
    else:
        test_full_ai_flow()


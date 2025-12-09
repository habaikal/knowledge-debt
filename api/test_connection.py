"""
Connection Agent 통합 테스트
전혀 다른 분야의 책들을 연결해서 새로운 아이디어 생성
"""
import os
import requests
import time

API_BASE_URL = "http://localhost:8000"

def print_separator():
    print("\n" + "="*80 + "\n")


def test_connection_flow():
    """전체 연결 플로우 테스트"""
    
    print("🧪 Connection Agent 테스트 시작\n")
    
    # 0. API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY가 설정되지 않았습니다.")
        print("   export GOOGLE_API_KEY='your-api-key'")
        return
    
    # 1. 책 2권 등록 (완전히 다른 분야)
    print_separator()
    print("📚 Step 1: 책 등록\n")
    
    book1 = {
        "title": "아주 작은 습관의 힘",
        "author": "제임스 클리어",
        "genre": "자기계발",
        "purchase_date": "2024-01-15",
        "page_count": 350
    }
    
    book2 = {
        "title": "클린 코드",
        "author": "로버트 C. 마틴",
        "genre": "프로그래밍",
        "purchase_date": "2024-01-20",
        "page_count": 450
    }
    
    # 책1 등록
    response1 = requests.post(f"{API_BASE_URL}/books", json=book1)
    book1_data = response1.json()
    book1_id = book1_data["id"]
    print(f"✅ 책1 등록: {book1['title']} (ID: {book1_id})")
    
    # 책2 등록
    response2 = requests.post(f"{API_BASE_URL}/books", json=book2)
    book2_data = response2.json()
    book2_id = book2_data["id"]
    print(f"✅ 책2 등록: {book2['title']} (ID: {book2_id})")
    
    # 2. 하이라이트 추가 (벡터 DB에 자동 저장됨)
    print_separator()
    print("💡 Step 2: 하이라이트 추가\n")
    
    highlights = [
        {
            "book_id": book1_id,
            "original_text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
            "page_number": 15,
            "my_thoughts": "복리의 힘"
        },
        {
            "book_id": book1_id,
            "original_text": "습관은 자아 정체성의 구체화다.",
            "page_number": 45,
            "my_thoughts": "정체성 기반 습관"
        },
        {
            "book_id": book2_id,
            "original_text": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
            "page_number": 23,
            "my_thoughts": "기술 부채"
        },
        {
            "book_id": book2_id,
            "original_text": "깨끗한 코드는 단순하고 직접적이다.",
            "page_number": 67,
            "my_thoughts": "단순함의 미학"
        }
    ]
    
    highlight_ids = []
    
    for h in highlights:
        response = requests.post(f"{API_BASE_URL}/highlights", json=h)
        h_data = response.json()
        highlight_ids.append(h_data["id"])
        print(f"✅ 하이라이트 추가: \"{h['original_text'][:40]}...\" (ID: {h_data['id']})")
    
    # 잠시 대기 (벡터 저장 완료)
    time.sleep(1)
    
    # 3. 벡터 DB 통계 확인
    print_separator()
    print("📊 Step 3: 벡터 DB 통계\n")
    
    response = requests.get(f"{API_BASE_URL}/vector/stats")
    stats = response.json()
    print(f"   총 벡터 수: {stats['total_vectors']}")
    print(f"   임베딩 타입: {stats['embedding_type']}")
    print(f"   저장 경로: {stats['persist_directory']}")
    
    # 4. Random Mix 테스트
    print_separator()
    print("🎲 Step 4: Random Mix - 전혀 다른 하이라이트 매칭\n")
    
    response = requests.get(f"{API_BASE_URL}/vector/random-mix?n=2&min_distance=0.3")
    random_mix = response.json()
    
    print(f"   매칭된 하이라이트 수: {random_mix['count']}")
    print(f"   최소 거리: {random_mix['min_distance']}\n")
    
    for i, item in enumerate(random_mix['results'], 1):
        print(f"   {i}. \"{item['text'][:50]}...\"")
        print(f"      📚 {item['metadata']['book_title']}")
        print(f"      🎯 장르: {item['metadata']['genre']}")
        if item.get('distance'):
            print(f"      📏 Distance: {item['distance']:.4f}")
        print()
    
    # 5. 아이디어 연결 - 수동 선택
    print_separator()
    print("🔗 Step 5: 아이디어 연결 (수동 선택)\n")
    
    connect_request = {
        "highlight_id_a": highlight_ids[0],  # 습관의 힘
        "highlight_id_b": highlight_ids[2],  # 클린 코드
        "user_context": "개발자로서 생산성을 높이고 싶습니다"
    }
    
    print(f"   하이라이트 A: ID {highlight_ids[0]}")
    print(f"   하이라이트 B: ID {highlight_ids[2]}")
    print(f"   사용자 상황: {connect_request['user_context']}")
    print("\n   AI 에이전트 생성 중...\n")
    
    response = requests.post(
        f"{API_BASE_URL}/ai/connect-ideas",
        json=connect_request
    )
    
    if response.status_code != 200:
        print(f"❌ 에러: {response.text}")
        return
    
    connection = response.json()
    
    print("✨ 연결 결과:\n")
    print(f"📚 책 A: {connection['highlight_a']['metadata']['book_title']}")
    print(f"   \"{connection['highlight_a']['text']}\"\n")
    
    print(f"📚 책 B: {connection['highlight_b']['metadata']['book_title']}")
    print(f"   \"{connection['highlight_b']['text']}\"\n")
    
    if connection.get('distance'):
        print(f"📏 의미적 거리: {connection['distance']:.4f} (높을수록 다름)\n")
    
    result = connection['result']
    
    print("🔗 연결점:")
    print(f"   {result['connection_point']}\n")
    
    print("💡 새로운 아이디어:")
    print(f"   {result['new_idea']}\n")
    
    print("✅ 이 아이디어가 작동하는 이유:")
    for i, reason in enumerate(result['why_it_works'], 1):
        print(f"   {i}. {reason}")
    
    if result.get('example'):
        print(f"\n📌 예시:")
        print(f"   {result['example']}")
    
    # 6. 아이디어 연결 - 자동 매칭 (Random Mix)
    print_separator()
    print("🎲 Step 6: 아이디어 연결 (Random Mix 자동 매칭)\n")
    
    random_request = {
        "use_random_mix": True,
        "user_context": "스타트업 창업을 준비하고 있습니다"
    }
    
    print(f"   사용자 상황: {random_request['user_context']}")
    print("   Random Mix로 자동 매칭 중...\n")
    
    response = requests.post(
        f"{API_BASE_URL}/ai/connect-ideas",
        json=random_request
    )
    
    if response.status_code != 200:
        print(f"❌ 에러: {response.text}")
        return
    
    connection = response.json()
    
    print("✨ 자동 매칭 결과:\n")
    print(f"📚 책 A: {connection['highlight_a']['metadata']['book_title']} ({connection['highlight_a']['metadata']['genre']})")
    print(f"   \"{connection['highlight_a']['text']}\"\n")
    
    print(f"📚 책 B: {connection['highlight_b']['metadata']['book_title']} ({connection['highlight_b']['metadata']['genre']})")
    print(f"   \"{connection['highlight_b']['text']}\"\n")
    
    if connection.get('distance'):
        print(f"📏 의미적 거리: {connection['distance']:.4f}\n")
    
    result = connection['result']
    
    print("🔗 연결점:")
    print(f"   {result['connection_point']}\n")
    
    print("💡 새로운 아이디어:")
    print(f"   {result['new_idea']}\n")
    
    print("✅ 이 아이디어가 작동하는 이유:")
    for i, reason in enumerate(result['why_it_works'], 1):
        print(f"   {i}. {reason}")
    
    if result.get('example'):
        print(f"\n📌 예시:")
        print(f"   {result['example']}")
    
    print_separator()
    print("🎉 테스트 완료!")
    print("\n💡 Tip: Swagger UI (http://localhost:8000/docs)에서")
    print("   'AI Agent' 섹션의 /ai/connect-ideas를 직접 테스트해보세요!")


if __name__ == "__main__":
    test_connection_flow()


"""
POST /ai/mix-ideas 엔드포인트 테스트
두 책을 연결하여 아이디어 생성 및 저장, 부채 탕감
"""
import os
import requests
import time

API_BASE_URL = "http://localhost:8000"

def print_separator():
    print("\n" + "="*80 + "\n")


def test_mix_ideas():
    """mix-ideas 엔드포인트 테스트"""
    
    print("🧪 Mix Ideas 테스트 시작\n")
    
    # API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY가 설정되지 않았습니다.")
        print("   export GOOGLE_API_KEY='your-api-key'")
        return
    
    # 1. 기존 책 확인
    print_separator()
    print("📚 Step 1: 기존 책 확인\n")
    
    response = requests.get(f"{API_BASE_URL}/books")
    books = response.json()
    
    if len(books) < 2:
        print("⚠️  최소 2권의 책이 필요합니다. 책을 먼저 등록해주세요.")
        
        # 테스트용 책 등록
        print("\n테스트용 책 2권 등록 중...\n")
        
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
        
        r1 = requests.post(f"{API_BASE_URL}/books", json=book1)
        book1_data = r1.json()
        print(f"✅ {book1['title']} 등록 (ID: {book1_data['id']})")
        
        r2 = requests.post(f"{API_BASE_URL}/books", json=book2)
        book2_data = r2.json()
        print(f"✅ {book2['title']} 등록 (ID: {book2_data['id']})")
        
        # 하이라이트 추가
        print("\n하이라이트 추가 중...\n")
        
        h1 = {
            "book_id": book1_data['id'],
            "original_text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
            "page_number": 15
        }
        
        h2 = {
            "book_id": book2_data['id'],
            "original_text": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
            "page_number": 23
        }
        
        requests.post(f"{API_BASE_URL}/highlights", json=h1)
        print(f"✅ 하이라이트 추가: 책 {book1_data['id']}")
        
        requests.post(f"{API_BASE_URL}/highlights", json=h2)
        print(f"✅ 하이라이트 추가: 책 {book2_data['id']}")
        
        time.sleep(2)  # 벡터 저장 대기
        
        books = [book1_data, book2_data]
    
    print(f"📚 총 {len(books)}권의 책 발견")
    for book in books[:5]:
        print(f"   - {book['title']} (ID: {book['id']})")
    
    # 2. Manual Mode 테스트
    print_separator()
    print("🎯 Step 2: Manual Mode - 직접 두 책 선택\n")
    
    if len(books) >= 2:
        book_a_id = books[0]['id']
        book_b_id = books[1]['id']
        
        manual_request = {
            "mode": "manual",
            "book_id_a": book_a_id,
            "book_id_b": book_b_id,
            "user_context": "개발자로서 생산성과 습관 개선에 관심이 있습니다"
        }
        
        print(f"   책 A: {books[0]['title']} (ID: {book_a_id})")
        print(f"   책 B: {books[1]['title']} (ID: {book_b_id})")
        print(f"   사용자 상황: {manual_request['user_context']}")
        print("\n   AI 아이디어 생성 중...\n")
        
        response = requests.post(
            f"{API_BASE_URL}/ai/mix-ideas",
            json=manual_request
        )
        
        if response.status_code != 200:
            print(f"❌ 에러: {response.status_code}")
            print(response.text)
        else:
            data = response.json()
            
            print("✨ 아이디어 생성 및 저장 완료!\n")
            
            idea = data['idea']
            print(f"💡 Idea ID: {idea['id']}")
            print(f"   생성 시간: {idea['created_at']}")
            if idea.get('distance'):
                print(f"   의미적 거리: {idea['distance']:.4f}\n")
            
            print(f"🔗 연결점:")
            print(f"   {idea['connection_point']}\n")
            
            print(f"💡 새로운 아이디어:")
            print(f"   {idea['new_idea']}\n")
            
            import json
            why_it_works = json.loads(idea['why_it_works'])
            print(f"✅ 작동 이유:")
            for i, reason in enumerate(why_it_works, 1):
                print(f"   {i}. {reason}")
            
            if idea.get('example'):
                print(f"\n📌 예시:")
                print(f"   {idea['example']}")
            
            print(f"\n📊 부채 탕감:")
            print(f"   책 A: {data['book_a']['title']}")
            print(f"   책 B: {data['book_b']['title']}")
            print(f"   총 탕감: {data['total_reduction']}pt (-40pt × 2)")
            
            print(f"\n🎯 생성된 활동:")
            for act in data['activities_created']:
                print(f"   - {act['activity_type']}: {act['content'][:60]}... ({act['reduction_points']}pt)")
    
    # 3. Random Mode 테스트
    print_separator()
    print("🎲 Step 3: Random Mode - 시스템이 랜덤 조합 제안\n")
    
    random_request = {
        "mode": "random",
        "user_context": "혁신적인 스타트업 아이디어를 찾고 있습니다"
    }
    
    print(f"   사용자 상황: {random_request['user_context']}")
    print("   시스템이 랜덤으로 두 책을 선택합니다...\n")
    
    response = requests.post(
        f"{API_BASE_URL}/ai/mix-ideas",
        json=random_request
    )
    
    if response.status_code != 200:
        print(f"❌ 에러: {response.status_code}")
        print(response.text)
    else:
        data = response.json()
        
        print(f"✨ 랜덤 조합 선택:\n")
        print(f"   책 A: {data['book_a']['title']} ({data['book_a']['genre']})")
        print(f"   책 B: {data['book_b']['title']} ({data['book_b']['genre']})\n")
        
        idea = data['idea']
        print(f"💡 Idea ID: {idea['id']}\n")
        
        print(f"🔗 연결점:")
        print(f"   {idea['connection_point']}\n")
        
        print(f"💡 새로운 아이디어:")
        print(f"   {idea['new_idea']}\n")
        
        import json
        why_it_works = json.loads(idea['why_it_works'])
        print(f"✅ 작동 이유:")
        for i, reason in enumerate(why_it_works, 1):
            print(f"   {i}. {reason}")
        
        if idea.get('example'):
            print(f"\n📌 예시:")
            print(f"   {idea['example']}")
        
        print(f"\n📊 총 탕감: {data['total_reduction']}pt")
    
    # 4. 생성된 아이디어 목록 조회
    print_separator()
    print("📋 Step 4: 생성된 아이디어 목록\n")
    
    response = requests.get(f"{API_BASE_URL}/ideas")
    ideas = response.json()
    
    print(f"💡 총 {len(ideas)}개의 아이디어\n")
    
    for i, idea in enumerate(ideas[:5], 1):
        print(f"{i}. ID {idea['id']} - {idea['created_at']}")
        print(f"   🔗 {idea['connection_point'][:60]}...")
        print(f"   💡 {idea['new_idea'][:80]}...")
        print()
    
    # 5. 특정 책의 아이디어 조회
    if books:
        print_separator()
        print(f"📚 Step 5: 특정 책의 아이디어\n")
        
        book_id = books[0]['id']
        response = requests.get(f"{API_BASE_URL}/books/{book_id}/ideas")
        data = response.json()
        
        print(f"📚 {data['book_title']}")
        print(f"💡 연결된 아이디어: {data['total_ideas']}개\n")
        
        for i, idea in enumerate(data['ideas'][:3], 1):
            print(f"{i}. {idea['connection_point'][:60]}...")
    
    print_separator()
    print("🎉 테스트 완료!")
    print("\n💡 Swagger UI에서 더 많은 기능을 테스트해보세요:")
    print("   http://localhost:8000/docs")


if __name__ == "__main__":
    test_mix_ideas()


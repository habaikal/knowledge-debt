"""
알림 시스템 테스트
"""
import requests
import time

API_BASE_URL = "http://localhost:8000"

def print_separator():
    print("\n" + "="*80 + "\n")


def test_notifications():
    """알림 시스템 테스트"""
    
    print("🧪 알림 시스템 테스트 시작\n")
    
    # 1. 알림 체크 수동 실행
    print_separator()
    print("🔧 Step 1: 알림 체크 수동 실행\n")
    
    response = requests.post(f"{API_BASE_URL}/notifications/run-checks")
    
    if response.status_code == 200:
        print("✅ 알림 체크 실행 완료")
        print(f"   응답: {response.json()}")
    else:
        print(f"❌ 에러: {response.status_code}")
        print(response.text)
    
    time.sleep(2)  # 알림 생성 대기
    
    # 2. 알림 목록 조회
    print_separator()
    print("📬 Step 2: 알림 목록 조회\n")
    
    response = requests.get(f"{API_BASE_URL}/notifications")
    notifications = response.json()
    
    print(f"📬 총 {len(notifications)}개의 알림\n")
    
    for i, notif in enumerate(notifications[:10], 1):
        icon = {
            'normal': '📢',
            'warning': '⚠️',
            'critical': '🚨'
        }.get(notif['priority'], '📢')
        
        read_status = '✓' if notif['is_read'] else '●'
        
        print(f"{read_status} {icon} {notif['title']}")
        print(f"   {notif['message']}")
        print(f"   타입: {notif['notification_type']} | 우선순위: {notif['priority']}")
        print(f"   생성: {notif['created_at']}")
        print()
    
    # 3. 읽지 않은 알림 수
    print_separator()
    print("🔔 Step 3: 읽지 않은 알림 수\n")
    
    response = requests.get(f"{API_BASE_URL}/notifications/unread-count")
    data = response.json()
    
    print(f"🔔 읽지 않은 알림: {data['unread_count']}개")
    
    # 4. 읽지 않은 알림만 조회
    print_separator()
    print("📭 Step 4: 읽지 않은 알림만 조회\n")
    
    response = requests.get(f"{API_BASE_URL}/notifications?is_read=false")
    unread_notifications = response.json()
    
    print(f"📭 읽지 않은 알림: {len(unread_notifications)}개\n")
    
    for i, notif in enumerate(unread_notifications[:5], 1):
        print(f"{i}. {notif['title']}")
        print(f"   {notif['message']}")
        print()
    
    # 5. 개별 알림 읽음 처리
    if notifications:
        print_separator()
        print("✅ Step 5: 개별 알림 읽음 처리\n")
        
        notif_id = notifications[0]['id']
        
        response = requests.patch(
            f"{API_BASE_URL}/notifications/{notif_id}",
            json={"is_read": True}
        )
        
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ 알림 {notif_id} 읽음 처리 완료")
            print(f"   제목: {updated['title']}")
            print(f"   읽음 상태: {updated['is_read']}")
    
    # 6. 모든 알림 읽음 처리
    print_separator()
    print("✅ Step 6: 모든 알림 읽음 처리\n")
    
    response = requests.post(f"{API_BASE_URL}/notifications/mark-all-read")
    
    if response.status_code == 200:
        print("✅ 모든 알림 읽음 처리 완료")
        print(f"   응답: {response.json()}")
    
    # 읽지 않은 알림 수 재확인
    response = requests.get(f"{API_BASE_URL}/notifications/unread-count")
    data = response.json()
    print(f"\n🔔 현재 읽지 않은 알림: {data['unread_count']}개")
    
    # 7. 우선순위별 알림 통계
    print_separator()
    print("📊 Step 7: 알림 통계\n")
    
    response = requests.get(f"{API_BASE_URL}/notifications?limit=1000")
    all_notifications = response.json()
    
    # 타입별 카운트
    type_counts = {}
    priority_counts = {}
    
    for notif in all_notifications:
        notif_type = notif['notification_type']
        priority = notif['priority']
        
        type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print("📊 알림 타입별 통계:")
    for notif_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {notif_type}: {count}개")
    
    print("\n📊 우선순위별 통계:")
    for priority, count in sorted(priority_counts.items(), key=lambda x: x[1], reverse=True):
        icon = {'normal': '📢', 'warning': '⚠️', 'critical': '🚨'}.get(priority, '📢')
        print(f"   {icon} {priority}: {count}개")
    
    print_separator()
    print("🎉 테스트 완료!")
    print("\n💡 Swagger UI에서 더 많은 기능을 테스트해보세요:")
    print("   http://localhost:8000/docs")
    print("\n📅 스케줄러는 다음 시간에 자동으로 실행됩니다:")
    print("   - 매일 오전 9시, 오후 6시: 고부채 경고")
    print("   - 매일 오전 10시: 일일 부채 리마인더")
    print("   - 매일 오전 11시: 책 완료 축하")
    print("   - 매일 오후 8시: 비활성 책 경고")


if __name__ == "__main__":
    test_notifications()


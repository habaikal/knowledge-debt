# 📬 알림 시스템 (APScheduler)

APScheduler를 사용한 자동 알림 시스템입니다. 정해진 시간에 자동으로 체크하고 알림을 생성합니다.

## 🎯 핵심 기능

### 1. 자동 스케줄 알림

#### ① 매일 오전 10시: 일일 부채 리마인더 📚
```
"📚 현재 지적 부채: {총포인트}pt ({책수}권)입니다."
```
- 총 부채가 0pt 이상일 때만 알림 생성
- 우선순위: normal

#### ② 매일 오후 8시: 비활성 책 경고 ⚠️
```
"⚠️ {책제목}이 3일째 방치 중입니다. 부채이자가 늘어나고 있어요!"
```
- 3일 이상 활동이 없는 책 체크
- 부채가 있는 책만 경고
- 우선순위: warning

#### ③ 매일 오전 9시, 오후 6시: 고부채 경고 🚨
```
"🚨 경고! 지적 부채가 위험 수준입니다 ({총포인트}pt). 
지금 바로 탕감 활동을 시작하세요."
```
- 총 부채가 500pt 초과 시 알림
- 하루 2회 체크
- 우선순위: critical

#### ④ 매일 오전 11시: 책 완료 축하 🎉
```
"🎉 축하합니다! {책제목}를 완전히 자산화했습니다! 
마일리지 {포인트}pt 획득!"
```
- 최근 자산으로 전환된 책 발견
- 중복 방지 (이미 축하 알림이 있으면 스킵)
- 우선순위: normal

### 2. 알림 저장 및 조회

모든 알림은 `notifications` 테이블에 저장되며, REST API로 조회/관리 가능합니다.

## 📊 Database Schema

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_type TEXT NOT NULL,    -- 알림 타입
    title TEXT NOT NULL,                -- 제목
    message TEXT NOT NULL,              -- 메시지 내용
    book_id INTEGER,                    -- 연관된 책 (선택)
    priority TEXT DEFAULT 'normal',     -- normal, warning, critical
    is_read BOOLEAN DEFAULT 0,          -- 읽음 여부
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

## 🚀 API 엔드포인트

### GET /notifications

알림 목록 조회

```bash
# 전체 알림
curl "http://localhost:8000/notifications"

# 읽지 않은 알림만
curl "http://localhost:8000/notifications?is_read=false"

# 읽은 알림만
curl "http://localhost:8000/notifications?is_read=true"

# 페이지네이션
curl "http://localhost:8000/notifications?skip=0&limit=20"
```

**Response:**
```json
[
  {
    "id": 1,
    "notification_type": "daily_reminder",
    "title": "📚 일일 부채 현황",
    "message": "현재 지적 부채: 450pt (3권)입니다.",
    "book_id": null,
    "priority": "normal",
    "is_read": false,
    "created_at": "2024-12-09T10:00:00"
  },
  {
    "id": 2,
    "notification_type": "inactive_warning",
    "title": "⚠️ 방치된 책 경고",
    "message": "클린 코드이 3일째 방치 중입니다. 부채이자가 늘어나고 있어요!",
    "book_id": 5,
    "priority": "warning",
    "is_read": false,
    "created_at": "2024-12-09T20:00:00"
  }
]
```

### GET /notifications/unread-count

읽지 않은 알림 수

```bash
curl "http://localhost:8000/notifications/unread-count"
```

**Response:**
```json
{
  "unread_count": 5
}
```

### PATCH /notifications/{notification_id}

개별 알림 읽음 처리

```bash
curl -X PATCH "http://localhost:8000/notifications/1" \
  -H "Content-Type: application/json" \
  -d '{"is_read": true}'
```

**Response:**
```json
{
  "id": 1,
  "notification_type": "daily_reminder",
  "title": "📚 일일 부채 현황",
  "message": "...",
  "is_read": true,
  "created_at": "2024-12-09T10:00:00"
}
```

### POST /notifications/mark-all-read

모든 알림 읽음 처리

```bash
curl -X POST "http://localhost:8000/notifications/mark-all-read"
```

**Response:**
```json
{
  "message": "모든 알림을 읽음 처리했습니다"
}
```

### POST /notifications/run-checks

알림 체크 수동 실행 (테스트용)

```bash
curl -X POST "http://localhost:8000/notifications/run-checks"
```

**Response:**
```json
{
  "message": "모든 알림 체크가 실행되었습니다"
}
```

## 📅 스케줄 설정

### Cron 표현식

| 시간 | 작업 | Cron |
|------|------|------|
| 매일 오전 9시 | 고부채 경고 | `0 9 * * *` |
| 매일 오전 10시 | 일일 리마인더 | `0 10 * * *` |
| 매일 오전 11시 | 책 완료 축하 | `0 11 * * *` |
| 매일 오후 6시 | 고부채 경고 | `0 18 * * *` |
| 매일 오후 8시 | 비활성 책 경고 | `0 20 * * *` |

### 시간대 설정

```python
# scheduler.py
scheduler = BackgroundScheduler(timezone="Asia/Seoul")
```

## 🧪 테스트

### 자동 테스트 실행

```bash
cd api

# 테스트 실행
python3 test_notifications.py
```

**테스트 시나리오:**
1. 알림 체크 수동 실행
2. 알림 목록 조회
3. 읽지 않은 알림 수
4. 읽지 않은 알림만 조회
5. 개별 알림 읽음 처리
6. 모든 알림 읽음 처리
7. 알림 통계

### 수동 테스트

```bash
# 서버 로그 확인 (스케줄러 시작 확인)
tail -f api/logs.txt

# 알림 체크 즉시 실행
curl -X POST "http://localhost:8000/notifications/run-checks"

# 알림 확인
curl "http://localhost:8000/notifications"
```

## 💡 활용 시나리오

### 1. 실시간 배지 표시

```typescript
const NotificationBadge = () => {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    // 5초마다 체크
    const interval = setInterval(async () => {
      const response = await fetch('/api/notifications/unread-count');
      const data = await response.json();
      setUnreadCount(data.unread_count);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative">
      <BellIcon />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 text-xs flex items-center justify-center">
          {unreadCount}
        </span>
      )}
    </div>
  );
};
```

### 2. 알림 센터

```typescript
const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState<'all' | 'unread'>('unread');

  const fetchNotifications = async () => {
    const url = filter === 'unread' 
      ? '/api/notifications?is_read=false' 
      : '/api/notifications';
    
    const response = await fetch(url);
    const data = await response.json();
    setNotifications(data);
  };

  const markAsRead = async (id: number) => {
    await fetch(`/api/notifications/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_read: true })
    });
    fetchNotifications();
  };

  return (
    <div className="notification-center">
      <div className="flex gap-2 mb-4">
        <button onClick={() => setFilter('all')}>전체</button>
        <button onClick={() => setFilter('unread')}>읽지 않음</button>
      </div>

      {notifications.map(notif => (
        <div 
          key={notif.id}
          className={`p-4 border rounded ${notif.is_read ? 'opacity-50' : ''}`}
        >
          <div className="flex justify-between">
            <h3 className="font-bold">{notif.title}</h3>
            <span className="text-xs text-gray-500">
              {new Date(notif.created_at).toLocaleString()}
            </span>
          </div>
          <p className="mt-2">{notif.message}</p>
          {!notif.is_read && (
            <button 
              onClick={() => markAsRead(notif.id)}
              className="mt-2 text-blue-600 text-sm"
            >
              읽음 처리
            </button>
          )}
        </div>
      ))}
    </div>
  );
};
```

### 3. 우선순위별 스타일링

```typescript
const getPriorityStyle = (priority: string) => {
  switch (priority) {
    case 'critical':
      return 'border-red-500 bg-red-50';
    case 'warning':
      return 'border-yellow-500 bg-yellow-50';
    default:
      return 'border-gray-300 bg-white';
  }
};

const getPriorityIcon = (priority: string) => {
  switch (priority) {
    case 'critical': return '🚨';
    case 'warning': return '⚠️';
    default: return '📢';
  }
};
```

### 4. 푸시 알림 연동

```typescript
// 서버에서 새 알림 생성 시 WebSocket으로 전송
// 또는 주기적으로 폴링

const useNotifications = () => {
  const [lastCount, setLastCount] = useState(0);

  useEffect(() => {
    const checkNewNotifications = async () => {
      const response = await fetch('/api/notifications/unread-count');
      const data = await response.json();
      
      if (data.unread_count > lastCount) {
        // 브라우저 푸시 알림
        if (Notification.permission === 'granted') {
          new Notification('새로운 알림', {
            body: '읽지 않은 알림이 있습니다.',
            icon: '/notification-icon.png'
          });
        }
      }
      
      setLastCount(data.unread_count);
    };

    const interval = setInterval(checkNewNotifications, 30000); // 30초마다
    return () => clearInterval(interval);
  }, [lastCount]);
};
```

## 🔧 커스터마이징

### 스케줄 변경

```python
# scheduler.py

# 일일 리마인더를 오전 8시로 변경
scheduler.add_job(
    daily_debt_reminder,
    trigger=CronTrigger(hour=8, minute=0),  # 10 → 8
    id='daily_debt_reminder',
    name='일일 부채 현황 리마인더',
    replace_existing=True
)

# 비활성 책 체크를 5일로 변경
def check_inactive_books():
    inactive_books = crud.get_books_without_recent_activity(db, days=5)  # 3 → 5
    ...
```

### 새로운 알림 추가

```python
# scheduler.py

def weekly_summary():
    """매주 일요일 오후 8시: 주간 요약"""
    db = get_db()
    try:
        # 이번 주 활동 통계
        stats = get_weekly_stats(db)
        
        notification_data = {
            'notification_type': 'weekly_summary',
            'title': '📊 주간 활동 요약',
            'message': f'이번 주 {stats["activities"]}개 활동으로 {stats["reduction"]}pt 탕감했습니다!',
            'priority': 'normal'
        }
        
        crud.create_notification(db, notification_data)
    finally:
        db.close()

# 스케줄 등록
scheduler.add_job(
    weekly_summary,
    trigger=CronTrigger(day_of_week='sun', hour=20, minute=0),
    id='weekly_summary',
    name='주간 요약'
)
```

### 알림 타입 추가

```python
# crud.py

NOTIFICATION_TYPES = {
    'daily_reminder': '일일 리마인더',
    'inactive_warning': '비활성 경고',
    'high_debt_alert': '고부채 경고',
    'completion_celebration': '완료 축하',
    'weekly_summary': '주간 요약',  # 새로 추가
    'milestone': '마일스톤 달성',    # 새로 추가
}
```

## 📊 모니터링

### 스케줄러 상태 확인

```python
# scheduler.py

def get_scheduler_status():
    """스케줄러 상태 조회"""
    jobs = scheduler.get_jobs()
    
    return {
        "running": scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time),
                "trigger": str(job.trigger)
            }
            for job in jobs
        ]
    }
```

### 로그 분석

```bash
# 스케줄러 로그 확인
grep "📚" api/logs.txt  # 일일 리마인더
grep "⚠️" api/logs.txt   # 비활성 경고
grep "🚨" api/logs.txt   # 고부채 경고
grep "🎉" api/logs.txt   # 완료 축하
```

## ⚠️ 주의사항

1. **시간대 설정**: `timezone="Asia/Seoul"` 확인
2. **DB 세션 관리**: 각 작업에서 명시적으로 `db.close()` 호출
3. **중복 방지**: 같은 알림이 여러 번 생성되지 않도록 체크
4. **성능**: 대량의 책이 있을 경우 쿼리 최적화 필요
5. **서버 재시작**: 서버 재시작 시 스케줄러 자동 시작

## 🔮 향후 확장 아이디어

1. **이메일 알림**: SMTP 연동하여 이메일 발송
2. **슬랙/디스코드 알림**: 웹훅 연동
3. **개인화된 시간**: 사용자별 선호 시간 설정
4. **알림 끄기**: 특정 알림 타입 비활성화
5. **스마트 알림**: AI가 적절한 시간 추천
6. **요약 기능**: 여러 알림을 하나로 묶어서 표시
7. **알림 히스토리**: 삭제된 알림 보관
8. **통계 대시보드**: 알림 타입별 통계 시각화

## 🎉 실행 확인

서버 시작 시 다음 로그가 표시되면 정상:

```
🚀 FastAPI 시작
✅ APScheduler 시작됨
📅 등록된 작업:
   - 일일 부채 현황 리마인더 (ID: daily_debt_reminder)
   - 비활성 책 경고 (ID: check_inactive_books)
   - 고부채 경고 (ID: check_high_debt)
   - 책 완료 축하 (ID: check_book_completion)
```

---

Made with 📬 using APScheduler

정해진 시간에 자동으로 알림을 받으세요! ⏰


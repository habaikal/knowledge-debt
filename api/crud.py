from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models
import schemas

# 활동 유형별 포인트 매핑
ACTIVITY_POINTS = {
    'read': 10, 'highlight': 20, 'feeling': 20, 'diary': 25,
    'writing': 30, 'quiz': 30, 'recommend': 30,
    'visual': 35, 'blog': 35,
    'connect': 40, 'discussion': 40, 'letter': 40,
    'study': 45, 'action': 50, 'video': 50, 'presentation': 50,
    'project': 60,
}


def calculate_initial_debt(page_count: int) -> int:
    """초기 부채 계산: 300 + (페이지수 × 0.5)"""
    return 300 + int(page_count * 0.5)


def calculate_status(current_debt: int, initial_debt: int) -> str:
    """부채 상태 계산"""
    if current_debt <= 0:
        return "asset"
    elif current_debt <= initial_debt * 0.5:
        return "partial"
    else:
        return "debt"


# ============================================
# Book CRUD
# ============================================

def create_book(db: Session, book: schemas.BookCreate):
    """책 등록 + 부채 원장 생성"""
    # 책 생성
    db_book = models.Book(
        title=book.title,
        author=book.author,
        genre=book.genre,
        purchase_date=book.purchase_date or str(date.today()),
        cover_image_url=book.cover_image_url,
        page_count=book.page_count,
    )
    db.add(db_book)
    db.flush()  # ID 생성을 위해 flush

    # 부채 원장 생성 (기본 300pt + 페이지당 0.5pt)
    initial_debt = calculate_initial_debt(book.page_count)
    db_debt = models.DebtLedger(
        book_id=db_book.id,
        initial_debt_points=initial_debt,
        current_remaining_points=initial_debt,
        status="debt",
        accumulated_mileage=0,
    )
    db.add(db_debt)
    db.commit()
    db.refresh(db_book)

    return db_book


def get_books(db: Session, status: str = None, skip: int = 0, limit: int = 100):
    """책 목록 조회 (상태별 필터링)"""
    query = db.query(models.Book).join(models.DebtLedger)
    
    if status:
        if status == "debt":
            # debt + partial 포함
            query = query.filter(models.DebtLedger.status.in_(["debt", "partial"]))
        else:
            query = query.filter(models.DebtLedger.status == status)
    
    return query.offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int):
    """특정 책 조회"""
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def delete_book(db: Session, book_id: int):
    """책 삭제 (연관된 모든 데이터 삭제)"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        db.delete(book)
        db.commit()
        return True
    return False


def update_book(db: Session, book_id: int, update_data: schemas.BookUpdate):
    """책 정보 수정"""
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None

    # None이 아닌 필드만 업데이트
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        if value is not None:
            setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def get_book_with_debt(db: Session, book_id: int):
    """책 + 부채 정보 조회"""
    book = get_book(db, book_id)
    if not book:
        return None
    
    # 진행률 계산
    progress = 0
    if book.debt_ledger.initial_debt_points > 0:
        progress = ((book.debt_ledger.initial_debt_points - book.debt_ledger.current_remaining_points) 
                   / book.debt_ledger.initial_debt_points * 100)
    
    return {
        **book.__dict__,
        "initial_debt_points": book.debt_ledger.initial_debt_points,
        "current_remaining_points": book.debt_ledger.current_remaining_points,
        "status": book.debt_ledger.status,
        "accumulated_mileage": book.debt_ledger.accumulated_mileage,
        "progress_percentage": min(progress, 100),
        "total_activities": len(book.activities),
        "total_highlights": len(book.highlights),
        "activities": book.activities,
        "highlights": book.highlights,
    }


# ============================================
# Activity CRUD
# ============================================

def create_activity(db: Session, activity: schemas.ActivityCreate):
    """활동 기록 + 자동 포인트 차감"""
    # 포인트 계산
    reduction_points = -ACTIVITY_POINTS.get(activity.activity_type, 20)
    
    # 활동 생성
    db_activity = models.Activity(
        book_id=activity.book_id,
        activity_type=activity.activity_type,
        reduction_points=reduction_points,
        content=activity.content,
        activity_date=activity.activity_date or str(date.today()),
    )
    db.add(db_activity)
    
    # 부채 업데이트
    debt = db.query(models.DebtLedger).filter(
        models.DebtLedger.book_id == activity.book_id
    ).first()
    
    if debt:
        debt.current_remaining_points += reduction_points
        
        # 0 미만일 경우 마일리지로 전환
        if debt.current_remaining_points < 0:
            debt.accumulated_mileage += abs(debt.current_remaining_points)
            debt.current_remaining_points = 0
        
        # 상태 업데이트
        debt.status = calculate_status(debt.current_remaining_points, debt.initial_debt_points)
    
    db.commit()
    db.refresh(db_activity)
    
    return db_activity


def get_activities(db: Session, book_id: int):
    """특정 책의 활동 목록 (최신순)"""
    return db.query(models.Activity).filter(
        models.Activity.book_id == book_id
    ).order_by(models.Activity.created_at.desc()).all()


def update_activity_completion(db: Session, activity_id: int, is_completed: bool):
    """활동 완료 상태 업데이트"""
    from datetime import datetime

    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id
    ).first()

    if not activity:
        return None

    activity.is_completed = is_completed
    activity.completed_at = datetime.now() if is_completed else None

    db.commit()
    db.refresh(activity)

    return activity


# ============================================
# Highlight CRUD
# ============================================

def create_highlight(db: Session, highlight: schemas.HighlightCreate):
    """하이라이트 추가 + 자동 20pt 탕감"""
    # 하이라이트 생성
    db_highlight = models.Highlight(
        book_id=highlight.book_id,
        original_text=highlight.original_text,
        page_number=highlight.page_number,
        my_thoughts=highlight.my_thoughts,
    )
    db.add(db_highlight)
    
    # 자동으로 activity 생성 (highlight 타입)
    db_activity = models.Activity(
        book_id=highlight.book_id,
        activity_type="highlight",
        reduction_points=-20,
        content=f"하이라이트 추가: {highlight.original_text[:50]}",
        activity_date=str(date.today()),
    )
    db.add(db_activity)
    
    # 부채 차감
    debt = db.query(models.DebtLedger).filter(
        models.DebtLedger.book_id == highlight.book_id
    ).first()
    
    if debt:
        debt.current_remaining_points -= 20
        
        if debt.current_remaining_points < 0:
            debt.accumulated_mileage += abs(debt.current_remaining_points)
            debt.current_remaining_points = 0
        
        debt.status = calculate_status(debt.current_remaining_points, debt.initial_debt_points)
    
    db.commit()
    db.refresh(db_highlight)
    
    return db_highlight


def get_highlights(db: Session, book_id: int):
    """특정 책의 하이라이트 목록"""
    return db.query(models.Highlight).filter(
        models.Highlight.book_id == book_id
    ).order_by(models.Highlight.page_number, models.Highlight.created_at).all()


def get_highlight(db: Session, highlight_id: int):
    """하이라이트 단일 조회"""
    return db.query(models.Highlight).filter(
        models.Highlight.id == highlight_id
    ).first()


# ============================================
# Idea CRUD
# ============================================

def create_idea(db: Session, idea_data: dict):
    """아이디어 저장"""
    import json
    
    # why_it_works를 JSON 문자열로 변환
    why_it_works = idea_data.get('why_it_works', [])
    if isinstance(why_it_works, list):
        why_it_works = json.dumps(why_it_works, ensure_ascii=False)
    
    db_idea = models.Idea(
        book_id_a=idea_data['book_id_a'],
        book_id_b=idea_data['book_id_b'],
        connection_point=idea_data['connection_point'],
        new_idea=idea_data['new_idea'],
        why_it_works=why_it_works,
        example=idea_data.get('example'),
        user_context=idea_data.get('user_context'),
        distance=idea_data.get('distance'),
    )
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    
    return db_idea


def get_ideas(db: Session, skip: int = 0, limit: int = 50):
    """아이디어 목록 조회"""
    return db.query(models.Idea).order_by(
        models.Idea.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_ideas_by_book(db: Session, book_id: int):
    """특정 책과 연결된 아이디어들"""
    return db.query(models.Idea).filter(
        (models.Idea.book_id_a == book_id) | (models.Idea.book_id_b == book_id)
    ).order_by(models.Idea.created_at.desc()).all()


def get_idea(db: Session, idea_id: int):
    """아이디어 단일 조회"""
    return db.query(models.Idea).filter(
        models.Idea.id == idea_id
    ).first()


# ============================================
# Notification CRUD
# ============================================

def create_notification(db: Session, notification_data: dict):
    """알림 생성"""
    db_notification = models.Notification(
        notification_type=notification_data['notification_type'],
        title=notification_data['title'],
        message=notification_data['message'],
        book_id=notification_data.get('book_id'),
        priority=notification_data.get('priority', 'normal'),
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_notifications(db: Session, is_read: bool = None, skip: int = 0, limit: int = 50):
    """알림 목록 조회"""
    query = db.query(models.Notification)
    
    if is_read is not None:
        query = query.filter(models.Notification.is_read == is_read)
    
    return query.order_by(
        models.Notification.created_at.desc()
    ).offset(skip).limit(limit).all()


def update_notification(db: Session, notification_id: int, is_read: bool):
    """알림 읽음 처리"""
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id
    ).first()
    
    if notification:
        notification.is_read = is_read
        db.commit()
        db.refresh(notification)
    
    return notification


def mark_all_as_read(db: Session):
    """모든 알림 읽음 처리"""
    db.query(models.Notification).update({"is_read": True})
    db.commit()
    return True


def get_unread_count(db: Session) -> int:
    """읽지 않은 알림 수"""
    return db.query(func.count(models.Notification.id)).filter(
        models.Notification.is_read == False
    ).scalar()


def get_books_without_recent_activity(db: Session, days: int = 3):
    """최근 활동이 없는 책 목록"""
    from datetime import datetime, timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 모든 책 가져오기
    all_books = db.query(models.Book).all()
    inactive_books = []
    
    for book in all_books:
        # 해당 책의 가장 최근 활동
        recent_activity = db.query(models.Activity).filter(
            models.Activity.book_id == book.id
        ).order_by(models.Activity.created_at.desc()).first()
        
        if not recent_activity:
            # 활동이 아예 없는 책
            inactive_books.append(book)
        elif recent_activity.activity_date < cutoff_date:
            # 3일 이상 활동 없음
            inactive_books.append(book)
    
    return inactive_books


# ============================================
# Dashboard CRUD
# ============================================

def get_dashboard_stats(db: Session):
    """대시보드 통계"""
    total_books = db.query(func.count(models.Book.id)).scalar()
    
    # 각 상태별 책 수 계산
    debt_books = db.query(func.count(models.DebtLedger.id)).filter(
        models.DebtLedger.status == "debt"
    ).scalar() or 0
    
    partial_books = db.query(func.count(models.DebtLedger.id)).filter(
        models.DebtLedger.status == "partial"
    ).scalar() or 0
    
    asset_books = db.query(func.count(models.DebtLedger.id)).filter(
        models.DebtLedger.status == "asset"
    ).scalar() or 0
    
    # 포인트 합계
    stats = db.query(
        func.sum(models.DebtLedger.initial_debt_points).label("total_initial"),
        func.sum(models.DebtLedger.current_remaining_points).label("total_remaining"),
        func.sum(models.DebtLedger.accumulated_mileage).label("total_mileage"),
    ).first()
    
    # 전체 진행률
    overall_progress = 0
    if stats.total_initial and stats.total_initial > 0:
        overall_progress = ((stats.total_initial - stats.total_remaining) / stats.total_initial * 100)
    
    # 자산 전환율
    asset_rate = 0
    if total_books > 0:
        asset_rate = (asset_books / total_books * 100) if asset_books else 0
    
    return {
        "total_books": total_books or 0,
        "debt_books": int(debt_books),
        "partial_books": int(partial_books),
        "asset_books": int(asset_books),
        "total_initial_debt": int(stats.total_initial or 0),
        "total_remaining_debt": int(stats.total_remaining or 0),
        "total_mileage": int(stats.total_mileage or 0),
        "overall_progress": round(overall_progress, 2),
        "asset_conversion_rate": round(asset_rate, 2),
    }


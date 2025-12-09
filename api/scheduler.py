"""
APScheduler를 사용한 알림 시스템
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import logging

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    """DB 세션"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # 각 작업에서 명시적으로 close


def daily_debt_reminder():
    """
    매일 오전 10시: 현재 총 부채 현황 리마인드
    """
    db = get_db()
    try:
        logger.info("📚 일일 부채 리마인더 실행")
        
        # 대시보드 통계 조회
        stats = crud.get_dashboard_stats(db)
        
        total_debt = stats['total_remaining_debt']
        total_books = stats['debt_books'] + stats['partial_books']
        
        if total_debt > 0:
            notification_data = {
                'notification_type': 'daily_reminder',
                'title': '📚 일일 부채 현황',
                'message': f'현재 지적 부채: {total_debt}pt ({total_books}권)입니다.',
                'priority': 'normal'
            }
            
            crud.create_notification(db, notification_data)
            logger.info(f"✅ 일일 리마인더 생성: {total_debt}pt ({total_books}권)")
        else:
            logger.info("ℹ️  현재 부채가 없습니다. 알림 생성 스킵.")
    
    except Exception as e:
        logger.error(f"❌ 일일 리마인더 오류: {e}")
    finally:
        db.close()


def check_inactive_books():
    """
    3일 이상 활동 없는 책 경고
    매일 오후 8시 체크
    """
    db = get_db()
    try:
        logger.info("⚠️  비활성 책 체크 실행")
        
        # 3일 이상 활동 없는 책들
        inactive_books = crud.get_books_without_recent_activity(db, days=3)
        
        for book in inactive_books:
            # 부채가 있는 책만 경고
            if book.debt_ledger and book.debt_ledger.current_remaining_points > 0:
                notification_data = {
                    'notification_type': 'inactive_warning',
                    'title': '⚠️ 방치된 책 경고',
                    'message': f'{book.title}이 3일째 방치 중입니다. 부채이자가 늘어나고 있어요!',
                    'book_id': book.id,
                    'priority': 'warning'
                }
                
                crud.create_notification(db, notification_data)
                logger.info(f"⚠️  비활성 경고 생성: {book.title}")
        
        if not inactive_books:
            logger.info("ℹ️  모든 책이 활발합니다.")
        else:
            logger.info(f"✅ {len(inactive_books)}권의 비활성 책 경고 생성")
    
    except Exception as e:
        logger.error(f"❌ 비활성 책 체크 오류: {e}")
    finally:
        db.close()


def check_high_debt():
    """
    부채가 500pt 초과 시 강력 경고
    매일 오전 9시, 오후 6시 체크
    """
    db = get_db()
    try:
        logger.info("🚨 고부채 체크 실행")
        
        # 대시보드 통계
        stats = crud.get_dashboard_stats(db)
        total_debt = stats['total_remaining_debt']
        
        if total_debt > 500:
            notification_data = {
                'notification_type': 'high_debt_alert',
                'title': '🚨 긴급 경고!',
                'message': f'경고! 지적 부채가 위험 수준입니다 ({total_debt}pt). 지금 바로 탕감 활동을 시작하세요.',
                'priority': 'critical'
            }
            
            crud.create_notification(db, notification_data)
            logger.info(f"🚨 고부채 경고 생성: {total_debt}pt")
        else:
            logger.info(f"ℹ️  부채 수준 양호: {total_debt}pt")
    
    except Exception as e:
        logger.error(f"❌ 고부채 체크 오류: {e}")
    finally:
        db.close()


def check_book_completion():
    """
    책이 자산으로 전환되었을 때 축하 알림
    매일 오전 11시 체크
    """
    db = get_db()
    try:
        logger.info("🎉 책 완료 체크 실행")
        
        # 최근 자산으로 전환된 책 찾기
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 자산 상태인 책들 중 최근 업데이트된 책
        import models
        asset_books = db.query(models.Book).join(models.DebtLedger).filter(
            models.DebtLedger.status == "asset",
            models.DebtLedger.updated_at >= yesterday
        ).all()
        
        for book in asset_books:
            # 이미 축하 알림이 있는지 체크
            existing = db.query(models.Notification).filter(
                models.Notification.book_id == book.id,
                models.Notification.notification_type == "completion_celebration"
            ).first()
            
            if not existing:
                notification_data = {
                    'notification_type': 'completion_celebration',
                    'title': '🎉 축하합니다!',
                    'message': f'"{book.title}"를 완전히 자산화했습니다! 마일리지 {book.debt_ledger.accumulated_mileage}pt 획득!',
                    'book_id': book.id,
                    'priority': 'normal'
                }
                
                crud.create_notification(db, notification_data)
                logger.info(f"🎉 완료 축하 생성: {book.title}")
    
    except Exception as e:
        logger.error(f"❌ 책 완료 체크 오류: {e}")
    finally:
        db.close()


# ============================================
# Scheduler 설정
# ============================================

scheduler = BackgroundScheduler(timezone="Asia/Seoul")


def init_scheduler():
    """스케줄러 초기화 및 작업 등록"""
    
    # 1. 매일 오전 10시: 일일 부채 리마인더
    scheduler.add_job(
        daily_debt_reminder,
        trigger=CronTrigger(hour=10, minute=0),
        id='daily_debt_reminder',
        name='일일 부채 현황 리마인더',
        replace_existing=True
    )
    
    # 2. 매일 오후 8시: 비활성 책 경고
    scheduler.add_job(
        check_inactive_books,
        trigger=CronTrigger(hour=20, minute=0),
        id='check_inactive_books',
        name='비활성 책 경고',
        replace_existing=True
    )
    
    # 3. 매일 오전 9시, 오후 6시: 고부채 경고
    scheduler.add_job(
        check_high_debt,
        trigger=CronTrigger(hour='9,18', minute=0),
        id='check_high_debt',
        name='고부채 경고',
        replace_existing=True
    )
    
    # 4. 매일 오전 11시: 책 완료 축하
    scheduler.add_job(
        check_book_completion,
        trigger=CronTrigger(hour=11, minute=0),
        id='check_book_completion',
        name='책 완료 축하',
        replace_existing=True
    )
    
    # 스케줄러 시작
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ APScheduler 시작됨")
        logger.info("📅 등록된 작업:")
        for job in scheduler.get_jobs():
            logger.info(f"   - {job.name} (ID: {job.id})")


def shutdown_scheduler():
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 APScheduler 종료됨")


def get_scheduler():
    """스케줄러 인스턴스 반환"""
    return scheduler


# ============================================
# 수동 실행 함수 (테스트용)
# ============================================

def run_all_checks_now():
    """모든 체크를 즉시 실행 (테스트용)"""
    logger.info("🔧 모든 체크 수동 실행")
    daily_debt_reminder()
    check_inactive_books()
    check_high_debt()
    check_book_completion()
    logger.info("✅ 모든 체크 완료")


if __name__ == "__main__":
    # 테스트 실행
    logger.info("🧪 Scheduler 테스트 시작\n")
    
    # 즉시 실행
    run_all_checks_now()
    
    logger.info("\n✅ 테스트 완료")


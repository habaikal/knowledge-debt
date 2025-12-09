from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    purchase_date = Column(String, nullable=False)
    genre = Column(String)
    cover_image_url = Column(String)
    page_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 관계
    debt_ledger = relationship("DebtLedger", back_populates="book", uselist=False, cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="book", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="book", cascade="all, delete-orphan")


class DebtLedger(Base):
    __tablename__ = "debt_ledger"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), unique=True, nullable=False)
    initial_debt_points = Column(Integer, nullable=False)
    current_remaining_points = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="debt")
    accumulated_mileage = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 관계
    book = relationship("Book", back_populates="debt_ledger")

    __table_args__ = (
        CheckConstraint("status IN ('debt', 'partial', 'asset')", name="check_status"),
    )


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    reduction_points = Column(Integer, nullable=False, default=0)
    content = Column(String)
    activity_date = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)  # AI 제안 실행 여부
    completed_at = Column(DateTime, nullable=True)  # 실행 완료 시간
    created_at = Column(DateTime, server_default=func.now())

    # 관계
    book = relationship("Book", back_populates="activities")


class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    original_text = Column(String, nullable=False)
    page_number = Column(Integer)
    my_thoughts = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 관계
    book = relationship("Book", back_populates="highlights")


class Idea(Base):
    """두 책을 연결한 아이디어"""
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, index=True)
    book_id_a = Column(Integer, ForeignKey("books.id"), nullable=False)
    book_id_b = Column(Integer, ForeignKey("books.id"), nullable=False)
    connection_point = Column(String, nullable=False)
    new_idea = Column(String, nullable=False)
    why_it_works = Column(String)  # JSON string
    example = Column(String)
    user_context = Column(String)
    distance = Column(Float)  # 두 책 간 의미적 거리
    created_at = Column(DateTime, server_default=func.now())

    # 관계
    book_a = relationship("Book", foreign_keys=[book_id_a])
    book_b = relationship("Book", foreign_keys=[book_id_b])


class Notification(Base):
    """알림"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    notification_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"))
    priority = Column(String, default="normal")  # normal, warning, critical
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # 관계
    book = relationship("Book", foreign_keys=[book_id])


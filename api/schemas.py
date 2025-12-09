from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# ============================================
# Book Schemas
# ============================================

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, description="책 제목")
    author: str = Field(..., min_length=1, description="저자")
    genre: Optional[str] = Field(None, description="장르")
    purchase_date: Optional[str] = Field(None, description="구매일 (YYYY-MM-DD)")
    cover_image_url: Optional[str] = Field(None, description="표지 이미지 URL")
    page_count: int = Field(300, ge=1, description="페이지 수")


class BookUpdate(BaseModel):
    """책 정보 수정"""
    title: Optional[str] = Field(None, min_length=1, description="책 제목")
    author: Optional[str] = Field(None, min_length=1, description="저자")
    genre: Optional[str] = Field(None, description="장르")
    cover_image_url: Optional[str] = Field(None, description="표지 이미지 URL")


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: Optional[str]
    purchase_date: str
    cover_image_url: Optional[str]
    page_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class BookWithDebt(BookResponse):
    initial_debt_points: int
    current_remaining_points: int
    status: str
    accumulated_mileage: int
    progress_percentage: float
    total_activities: int
    total_highlights: int


# ============================================
# Activity Schemas
# ============================================

class ActivityCreate(BaseModel):
    book_id: int = Field(..., description="책 ID")
    activity_type: str = Field(..., description="활동 유형 (read, highlight, etc.)")
    content: Optional[str] = Field(None, description="활동 내용")
    activity_date: Optional[str] = Field(None, description="활동 날짜")


class ActivityResponse(BaseModel):
    id: int
    book_id: int
    activity_type: str
    reduction_points: int
    content: Optional[str]
    activity_date: str
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityCompletionUpdate(BaseModel):
    """활동 완료 상태 업데이트"""
    is_completed: bool = Field(..., description="완료 여부")


# ============================================
# Highlight Schemas
# ============================================

class HighlightCreate(BaseModel):
    book_id: int = Field(..., description="책 ID")
    original_text: str = Field(..., min_length=1, description="원문")
    page_number: Optional[int] = Field(None, description="페이지 번호")
    my_thoughts: Optional[str] = Field(None, description="나의 생각")


class HighlightResponse(BaseModel):
    id: int
    book_id: int
    original_text: str
    page_number: Optional[int]
    my_thoughts: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Dashboard Schemas
# ============================================

class DashboardStats(BaseModel):
    total_books: int
    debt_books: int
    partial_books: int
    asset_books: int
    total_initial_debt: int
    total_remaining_debt: int
    total_mileage: int
    overall_progress: float
    asset_conversion_rate: float  # 자산 전환율


# ============================================
# Book Detail Schema
# ============================================

class BookDetail(BookWithDebt):
    activities: List[ActivityResponse]
    highlights: List[HighlightResponse]


# ============================================
# AI Agent Schemas
# ============================================

class AISuggestRequest(BaseModel):
    book_id: int = Field(..., description="책 ID")
    highlight_id: int = Field(..., description="하이라이트 ID")
    user_context: Optional[str] = Field(None, description="사용자 상황/직업")


class AIActionSuggestion(BaseModel):
    action: str = Field(..., description="행동 설명")
    duration: str = Field(..., description="예상 소요시간")
    difficulty: str = Field(..., description="난이도")
    activity_type: str = Field(..., description="활동 유형")
    estimated_points: int = Field(..., description="예상 탕감 포인트")


class AISuggestResponse(BaseModel):
    book_id: int
    book_title: str
    highlight_id: int
    highlight_text: str
    user_context: Optional[str]
    suggestions: List[AIActionSuggestion]


class AIExecuteRequest(BaseModel):
    book_id: int = Field(..., description="책 ID")
    suggestion: AIActionSuggestion = Field(..., description="선택한 제안")
    content: Optional[str] = Field(None, description="추가 내용 (선택)")


# ============================================
# Connection Agent Schemas
# ============================================

from typing import Dict

class ConnectIdeasRequest(BaseModel):
    """두 하이라이트 연결 요청"""
    highlight_id_a: Optional[int] = None
    highlight_id_b: Optional[int] = None
    use_random_mix: bool = False  # True면 자동으로 전혀 다른 하이라이트 매칭
    user_context: Optional[str] = None


class ConnectionResult(BaseModel):
    """연결 결과"""
    connection_point: str
    new_idea: str
    why_it_works: List[str]
    example: Optional[str] = None


class ConnectIdeasResponse(BaseModel):
    """두 하이라이트 연결 응답"""
    highlight_a: Dict
    highlight_b: Dict
    result: ConnectionResult
    distance: Optional[float] = None  # 두 하이라이트 간 거리 (다를수록 높음)


# ============================================
# Mix Ideas Schemas (책 단위 연결)
# ============================================

class MixIdeasRequest(BaseModel):
    """두 책 연결 아이디어 생성 요청"""
    mode: str = Field(..., description="모드: 'manual' 또는 'random'")
    book_id_a: Optional[int] = Field(None, description="책 A ID (manual 모드)")
    book_id_b: Optional[int] = Field(None, description="책 B ID (manual 모드)")
    user_context: Optional[str] = Field(None, description="사용자 상황")


class IdeaResponse(BaseModel):
    """저장된 아이디어 응답"""
    id: int
    book_id_a: int
    book_id_b: int
    connection_point: str
    new_idea: str
    why_it_works: str
    example: Optional[str]
    user_context: Optional[str]
    distance: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MixIdeasResponse(BaseModel):
    """두 책 연결 응답"""
    idea: IdeaResponse
    book_a: BookResponse
    book_b: BookResponse
    activities_created: List[ActivityResponse]
    total_reduction: int  # -80pt (각 -40pt)


# ============================================
# Notification Schemas
# ============================================

class NotificationResponse(BaseModel):
    """알림 응답"""
    id: int
    notification_type: str
    title: str
    message: str
    book_id: Optional[int]
    priority: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """알림 업데이트 (읽음 처리)"""
    is_read: bool


# ============================================
# Semantic Mix Schemas (의미적 브릿지)
# ============================================

class SemanticMixRequest(BaseModel):
    """의미적 Mix 요청"""
    book_id: Optional[int] = Field(None, description="특정 책 기준 (None이면 전체)")
    cross_genre: bool = Field(True, description="다른 장르 우선")
    min_similarity: float = Field(0.5, ge=0.0, le=1.0, description="최소 유사도")


class HighlightPairInfo(BaseModel):
    """하이라이트 쌍 정보"""
    highlight_id: int
    text: str
    book_id: int
    book_title: str
    author: str
    genre: str
    page: int


class SemanticPairResponse(BaseModel):
    """의미적 쌍 응답"""
    highlight_a: HighlightPairInfo
    highlight_b: HighlightPairInfo
    similarity_score: float
    is_cross_genre: bool


class SemanticMixResult(BaseModel):
    """의미적 Mix AI 결과"""
    connection_point: str
    new_idea: str
    why_it_works: str
    action_suggestion: str


class SemanticMixResponse(BaseModel):
    """의미적 Mix 전체 응답"""
    pair: SemanticPairResponse
    insight: SemanticMixResult


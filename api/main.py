from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# .env 파일 로드 (가장 먼저 실행)
load_dotenv()

import models
import schemas
import crud
from database import engine, get_db
from ai_agent import DebtReductionAgent, AgentRequest, create_agent
from lance_vector_store import get_vector_store  # LanceDB 기반 (락 문제 없음)
from connection_agent import get_connection_agent
from mix_agent import get_mix_agent, MixRequest, HighlightInfo
from scheduler import init_scheduler, shutdown_scheduler, run_all_checks_now
import os

# 테이블 생성
models.Base.metadata.create_all(bind=engine)

# Lifespan 이벤트 (스케줄러 시작/종료)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI 시작")
    init_scheduler()
    yield
    # Shutdown
    print("🛑 FastAPI 종료")
    shutdown_scheduler()

# FastAPI 앱 생성
app = FastAPI(
    title="지식 부채 관리 시스템 API",
    description="책을 읽고 활동하면서 지식 부채를 갚아나가는 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# 엔드포인트
# ============================================

@app.get("/", tags=["Root"])
def read_root():
    """API 루트"""
    return {
        "message": "지식 부채 관리 시스템 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# 1. POST /books - 새 책 등록
@app.post("/books", response_model=schemas.BookResponse, tags=["Books"])
def register_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 책을 등록합니다.
    
    - 자동으로 부채가 생성됩니다 (300 + 페이지수 × 0.5)
    - 초기 상태는 'debt'입니다
    """
    return crud.create_book(db, book)


# 2. GET /books - 책 목록 조회
@app.get("/books", response_model=List[schemas.BookWithDebt], tags=["Books"])
def get_books(
    status: Optional[str] = Query(None, description="상태 필터 (debt, partial, asset)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    책 목록을 조회합니다.
    
    - status: 상태별 필터링 (debt, partial, asset)
    - debt 필터는 debt + partial 모두 포함
    """
    books = crud.get_books(db, status, skip, limit)
    
    result = []
    for book in books:
        progress = 0
        if book.debt_ledger.initial_debt_points > 0:
            progress = ((book.debt_ledger.initial_debt_points - book.debt_ledger.current_remaining_points) 
                       / book.debt_ledger.initial_debt_points * 100)
        
        result.append({
            **book.__dict__,
            "initial_debt_points": book.debt_ledger.initial_debt_points,
            "current_remaining_points": book.debt_ledger.current_remaining_points,
            "status": book.debt_ledger.status,
            "accumulated_mileage": book.debt_ledger.accumulated_mileage,
            "progress_percentage": min(progress, 100),
            "total_activities": len(book.activities),
            "total_highlights": len(book.highlights),
        })
    
    return result


# 3. GET /books/{id} - 책 상세 정보
@app.get("/books/{book_id}", response_model=schemas.BookDetail, tags=["Books"])
def get_book_detail(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 책의 상세 정보를 조회합니다.
    
    - 책 정보
    - 부채 정보
    - 활동 이력
    - 하이라이트 목록
    """
    book_data = crud.get_book_with_debt(db, book_id)
    if not book_data:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    return book_data


@app.patch("/books/{book_id}", response_model=schemas.BookResponse, tags=["Books"])
def update_book(
    book_id: int,
    update_data: schemas.BookUpdate,
    db: Session = Depends(get_db)
):
    """
    ✏️ 책 정보 수정

    - 제목, 저자, 장르, 표지 이미지 URL 수정 가능
    - 변경하고 싶은 필드만 전달하면 됩니다
    """
    book = crud.update_book(db, book_id, update_data)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    return book


@app.delete("/books/{book_id}", tags=["Books"])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    🗑️ 책 삭제

    - 책과 연관된 모든 데이터를 삭제합니다
    - 부채 장부, 활동, 하이라이트가 모두 삭제됩니다
    - ⚠️ 이 작업은 되돌릴 수 없습니다
    """
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")

    book_title = book.title
    success = crud.delete_book(db, book_id)

    if success:
        return {
            "message": f"'{book_title}'이(가) 삭제되었습니다",
            "deleted_book_id": book_id
        }
    else:
        raise HTTPException(status_code=500, detail="책 삭제에 실패했습니다")


# 4. POST /activities - 탕감 활동 기록
@app.post("/activities", response_model=schemas.ActivityResponse, tags=["Activities"])
def record_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db)
):
    """
    탕감 활동을 기록합니다.
    
    - 자동으로 활동 유형에 따른 포인트가 차감됩니다
    - 부채 상태가 자동으로 업데이트됩니다
    - 0pt 이하로 내려가면 마일리지로 전환됩니다
    
    활동 유형: read(10pt), highlight(20pt), feeling(20pt), diary(25pt),
              writing(30pt), quiz(30pt), recommend(30pt), visual(35pt), blog(35pt),
              connect(40pt), discussion(40pt), letter(40pt), study(45pt),
              action(50pt), video(50pt), presentation(50pt), project(60pt)
    """
    # 책 존재 확인
    book = crud.get_book(db, activity.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    return crud.create_activity(db, activity)


# 4-2. GET /activities/{book_id} - 특정 책의 활동 이력 조회
@app.get("/activities/{book_id}", response_model=List[schemas.ActivityResponse], tags=["Activities"])
def get_book_activities(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 책의 활동 이력을 조회합니다.

    - 최신순으로 정렬
    - AI 제안 행동 포함
    """
    # 책 존재 확인
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")

    return crud.get_activities(db, book_id)


# 4-3. PATCH /activities/{activity_id}/complete - 활동 완료 상태 업데이트
@app.patch("/activities/{activity_id}/complete", response_model=schemas.ActivityResponse, tags=["Activities"])
def update_activity_completion(
    activity_id: int,
    update_data: schemas.ActivityCompletionUpdate,
    db: Session = Depends(get_db)
):
    """
    활동의 완료 상태를 업데이트합니다.

    - AI 제안 행동의 실제 실행 여부를 기록
    - 완료 시 completed_at에 현재 시간 기록
    """
    activity = crud.update_activity_completion(db, activity_id, update_data.is_completed)
    if not activity:
        raise HTTPException(status_code=404, detail="활동을 찾을 수 없습니다")
    return activity


# 5. GET /dashboard - 대시보드 통계
@app.get("/dashboard", response_model=schemas.DashboardStats, tags=["Dashboard"])
def get_dashboard(db: Session = Depends(get_db)):
    """
    대시보드 통계를 조회합니다.
    
    - 총 책 수
    - 상태별 책 수 (debt, partial, asset)
    - 총 부채/잔여 부채/마일리지
    - 전체 진행률
    - 자산 전환율
    """
    return crud.get_dashboard_stats(db)


# 6. GET /highlights/{book_id} - 하이라이트 목록
@app.get("/highlights/{book_id}", response_model=List[schemas.HighlightResponse], tags=["Highlights"])
def get_book_highlights(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 책의 하이라이트 목록을 조회합니다.
    
    - 페이지 순, 생성일 순으로 정렬
    """
    # 책 존재 확인
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    return crud.get_highlights(db, book_id)


# 벡터 저장 백그라운드 작업 (SQLite + numpy 기반)
def save_to_vector_store(highlight_id: int, text: str, metadata: dict):
    """백그라운드에서 벡터 DB에 저장"""
    try:
        vector_store = get_vector_store()
        vector_store.add_highlight(
            highlight_id=highlight_id,
            text=text,
            metadata=metadata
        )
    except Exception as e:
        print(f"⚠️ 벡터 저장 실패: {e}")


# 7. POST /highlights - 하이라이트 추가 (벡터 저장 포함)
@app.post("/highlights", response_model=schemas.HighlightResponse, tags=["Highlights"])
def add_highlight(
    highlight: schemas.HighlightCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    하이라이트를 추가합니다.

    - 자동으로 20pt 탕감됩니다
    - 자동으로 'highlight' 활동이 기록됩니다
    - ✨ 벡터 DB에 자동 저장됩니다 (유사도 검색 가능)
    """
    # 책 존재 확인
    book = crud.get_book(db, highlight.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")

    # DB에 저장
    db_highlight = crud.create_highlight(db, highlight)

    # 벡터 DB 저장을 백그라운드로 처리 (블로킹 방지)
    background_tasks.add_task(
        save_to_vector_store,
        highlight_id=db_highlight.id,
        text=highlight.original_text,
        metadata={
            "book_id": book.id,
            "book_title": book.title,
            "author": book.author,
            "genre": book.genre or "",
            "page": highlight.page_number or 0
        }
    )

    return db_highlight


@app.delete("/highlights/{highlight_id}", tags=["Highlights"])
def delete_highlight(
    highlight_id: int,
    db: Session = Depends(get_db)
):
    """하이라이트를 삭제합니다"""
    highlight = db.query(models.Highlight).filter(models.Highlight.id == highlight_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="하이라이트를 찾을 수 없습니다")
    
    db.delete(highlight)
    db.commit()
    
    return {"message": "하이라이트가 삭제되었습니다", "id": highlight_id}


# ============================================
# AI 에이전트 엔드포인트
# ============================================

@app.post("/ai/suggest-actions", response_model=schemas.AISuggestResponse, tags=["AI Agent"])
def suggest_actions(
    request: schemas.AISuggestRequest,
    db: Session = Depends(get_db)
):
    """
    하이라이트를 분석하여 탕감 행동을 제안합니다.
    
    - 데이터베이스에서 책과 하이라이트 정보 자동 조회
    - Google Gemini API로 개인화된 행동 3가지 제안
    - 각 행동에 활동 유형, 소요시간, 난이도, 예상 포인트 포함
    
    ⚠️ 사용하려면 GOOGLE_API_KEY 환경변수 설정 필요
    """
    # API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY 환경변수가 설정되지 않았습니다. Google AI Studio(aistudio.google.com)에서 API 키를 발급받아 설정해주세요."
        )
    
    # 책 확인
    book = crud.get_book(db, request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    # 하이라이트 확인
    highlight = db.query(models.Highlight).filter(
        models.Highlight.id == request.highlight_id,
        models.Highlight.book_id == request.book_id
    ).first()
    
    if not highlight:
        raise HTTPException(status_code=404, detail="하이라이트를 찾을 수 없습니다")
    
    try:
        # AI 에이전트 실행
        agent = create_agent()
        result = agent.suggest_and_format(
            book_title=book.title,
            highlight_text=highlight.original_text,
            user_context=request.user_context
        )
        
        # 응답 포맷팅
        return {
            "book_id": book.id,
            "book_title": book.title,
            "highlight_id": highlight.id,
            "highlight_text": highlight.original_text,
            "user_context": request.user_context,
            "suggestions": result["suggestions"]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 에이전트 오류: {str(e)}")


@app.post("/ai/execute-action", response_model=schemas.ActivityResponse, tags=["AI Agent"])
def execute_suggested_action(
    request: schemas.AIExecuteRequest,
    db: Session = Depends(get_db)
):
    """
    AI가 제안한 행동을 선택하여 실행합니다.
    
    - 자동으로 activities 테이블에 기록
    - 제안된 활동 유형에 따른 포인트 자동 차감
    - 부채 상태 자동 업데이트
    
    이 엔드포인트를 호출하면:
    1. 활동이 기록되고
    2. 포인트가 차감되며
    3. 상태가 업데이트됩니다
    """
    # 책 확인
    book = crud.get_book(db, request.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    # 활동 내용 구성
    content = request.content or request.suggestion.action
    
    # 활동 생성 (자동으로 포인트 차감됨)
    activity_data = schemas.ActivityCreate(
        book_id=request.book_id,
        activity_type=request.suggestion.activity_type,
        content=f"[AI 제안] {content}"
    )
    
    activity = crud.create_activity(db, activity_data)
    
    return activity


# ============================================
# Vector Search 엔드포인트
# ============================================

@app.get("/vector/similar", tags=["Vector Search"])
def find_similar_highlights(
    text: str = Query(..., description="검색할 텍스트"),
    n: int = Query(5, ge=1, le=20, description="반환할 결과 수"),
    book_id: Optional[int] = Query(None, description="특정 책으로 필터링")
):
    """
    유사한 하이라이트를 검색합니다.
    
    - 벡터 유사도 기반 검색
    - 책 ID로 필터링 가능
    """
    try:
        vector_store = get_vector_store()
        results = vector_store.find_similar(text, n, book_id)
        return {
            "query": text,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search error: {str(e)}")


@app.get("/vector/connections/{book_id}", tags=["Vector Search"])
def find_book_connections(
    book_id: int,
    n: int = Query(3, ge=1, le=10, description="반환할 책 수"),
    db: Session = Depends(get_db)
):
    """
    특정 책과 연결 가능한 다른 책들을 찾습니다.
    
    - 하이라이트 내용 유사도 기반
    - 책 간 지식 연결고리 발견
    """
    # 책 존재 확인
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    try:
        vector_store = get_vector_store()
        connections = vector_store.find_connections(book_id, n)
        return {
            "book_id": book_id,
            "book_title": book.title,
            "connections": connections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search error: {str(e)}")


@app.get("/vector/stats", tags=["Vector Search"])
def get_vector_stats():
    """벡터 DB 통계"""
    try:
        vector_store = get_vector_store()
        return {
            "total_vectors": vector_store.count(),
            "embedding_type": os.getenv("EMBEDDING_TYPE", "local"),
            "persist_directory": vector_store.persist_directory
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {str(e)}")


@app.get("/vector/random-mix", tags=["Vector Search"])
def get_random_mix(
    n: int = Query(2, ge=2, le=5, description="매칭할 하이라이트 수"),
    min_distance: float = Query(0.7, ge=0.0, le=2.0, description="최소 거리 (높을수록 더 다름)")
):
    """
    🎲 Random Mix: 유사도가 낮은 하이라이트 무작위 매칭
    
    - 전혀 다른 분야의 개념을 강제 연결
    - 세렌디피티(우연한 발견)를 위한 기능
    - 창의적 아이디어 생성에 활용
    """
    try:
        vector_store = get_vector_store()
        results = vector_store.find_random_mix(n, min_distance)
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="충분한 하이라이트가 없습니다"
            )
        
        return {
            "count": len(results),
            "min_distance": min_distance,
            "results": results,
            "tip": "이 하이라이트들을 연결해서 새로운 아이디어를 만들어보세요!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Random mix error: {str(e)}")


# ============================================
# Connection Agent 엔드포인트
# ============================================

@app.post("/ai/connect-ideas", response_model=schemas.ConnectIdeasResponse, tags=["AI Agent"])
def connect_ideas(
    request: schemas.ConnectIdeasRequest,
    db: Session = Depends(get_db)
):
    """
    ✨ 두 책의 하이라이트를 연결해서 새로운 아이디어 생성
    
    - 전혀 다른 분야의 개념을 강제 연결
    - 세렌디피티를 통한 창의적 사고 촉진
    - use_random_mix=true로 자동 매칭 가능
    
    ## 사용 방법
    
    ### 1. 수동 선택
    ```json
    {
      "highlight_id_a": 1,
      "highlight_id_b": 5,
      "user_context": "스타트업 창업 준비 중"
    }
    ```
    
    ### 2. 자동 매칭 (Random Mix)
    ```json
    {
      "use_random_mix": true,
      "user_context": "새로운 비즈니스 아이디어 필요"
    }
    ```
    """
    vector_store = get_vector_store()
    connection_agent = get_connection_agent()
    
    try:
        # 1. 하이라이트 선택
        if request.use_random_mix:
            # Random Mix: 자동으로 전혀 다른 하이라이트 매칭
            print("🎲 Random Mix 모드")
            random_highlights = vector_store.find_random_mix(n=2, min_distance=0.7)
            
            if len(random_highlights) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Random Mix를 위한 하이라이트가 부족합니다 (최소 2개 필요)"
                )
            
            highlight_a = random_highlights[0]
            highlight_b = random_highlights[1]
            distance = highlight_b.get('distance')
        
        else:
            # 수동 선택
            if not request.highlight_id_a or not request.highlight_id_b:
                raise HTTPException(
                    status_code=400,
                    detail="highlight_id_a와 highlight_id_b가 필요합니다"
                )
            
            # DB에서 하이라이트 조회
            db_highlight_a = crud.get_highlight(db, request.highlight_id_a)
            db_highlight_b = crud.get_highlight(db, request.highlight_id_b)
            
            if not db_highlight_a or not db_highlight_b:
                raise HTTPException(
                    status_code=404,
                    detail="하이라이트를 찾을 수 없습니다"
                )
            
            # 책 정보 조회
            book_a = crud.get_book(db, db_highlight_a.book_id)
            book_b = crud.get_book(db, db_highlight_b.book_id)
            
            highlight_a = {
                "id": f"highlight_{db_highlight_a.id}",
                "text": db_highlight_a.original_text,
                "metadata": {
                    "book_id": str(book_a.id),
                    "book_title": book_a.title,
                    "author": book_a.author,
                    "genre": book_a.genre or "",
                    "page": str(db_highlight_a.page_number or 0)
                }
            }
            
            highlight_b = {
                "id": f"highlight_{db_highlight_b.id}",
                "text": db_highlight_b.original_text,
                "metadata": {
                    "book_id": str(book_b.id),
                    "book_title": book_b.title,
                    "author": book_b.author,
                    "genre": book_b.genre or "",
                    "page": str(db_highlight_b.page_number or 0)
                }
            }
            
            # 두 하이라이트 간 거리 계산
            similar = vector_store.find_similar(
                highlight_a['text'],
                n=20,
                book_id=int(highlight_b['metadata']['book_id'])
            )
            
            distance = None
            for item in similar:
                if item['text'] == highlight_b['text']:
                    distance = item.get('distance')
                    break
        
        # 2. AI 에이전트로 아이디어 연결
        print(f"🔗 연결 중: {highlight_a['metadata']['book_title']} ↔ {highlight_b['metadata']['book_title']}")
        
        result = connection_agent.connect_ideas(
            highlight_a={
                "text": highlight_a['text'],
                "book_title": highlight_a['metadata']['book_title'],
                "author": highlight_a['metadata']['author'],
                "genre": highlight_a['metadata']['genre']
            },
            highlight_b={
                "text": highlight_b['text'],
                "book_title": highlight_b['metadata']['book_title'],
                "author": highlight_b['metadata']['author'],
                "genre": highlight_b['metadata']['genre']
            },
            user_context=request.user_context
        )
        
        return {
            "highlight_a": highlight_a,
            "highlight_b": highlight_b,
            "result": result,
            "distance": distance
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Connection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"아이디어 연결 실패: {str(e)}"
        )


@app.post("/ai/mix-ideas", response_model=schemas.MixIdeasResponse, tags=["AI Agent"])
def mix_ideas(
    request: schemas.MixIdeasRequest,
    db: Session = Depends(get_db)
):
    """
    🎨 두 책을 연결해서 새로운 아이디어 생성 및 저장
    
    - 아이디어를 ideas 테이블에 저장
    - 두 책 모두에 'connect' 활동 기록 (-40pt씩)
    - 총 -80pt 탕감
    
    ## 모드
    
    ### 1. Manual Mode
    사용자가 직접 두 책을 선택
    
    ```json
    {
      "mode": "manual",
      "book_id_a": 1,
      "book_id_b": 5,
      "user_context": "새로운 비즈니스 아이디어"
    }
    ```
    
    ### 2. Semantic Mode (권장)
    Vector DB에서 의미적으로 연결된 하이라이트 쌍을 자동 매칭

    ```json
    {
      "mode": "semantic",
      "user_context": "창의적 사고 필요"
    }
    ```

    ### 3. Random Mode (레거시)
    완전 랜덤 선택 (의미적 연결 없음)

    ```json
    {
      "mode": "random"
    }
    ```
    """
    vector_store = get_vector_store()
    connection_agent = get_connection_agent()
    
    try:
        # 1. 책 선택
        if request.mode == "manual":
            # Manual: 사용자가 두 책 직접 선택
            if not request.book_id_a or not request.book_id_b:
                raise HTTPException(
                    status_code=400,
                    detail="Manual 모드에서는 book_id_a와 book_id_b가 필요합니다"
                )
            
            book_a = crud.get_book(db, request.book_id_a)
            book_b = crud.get_book(db, request.book_id_b)
            
            if not book_a or not book_b:
                raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
            
            # 각 책의 하이라이트 가져오기
            highlights_a = crud.get_highlights(db, request.book_id_a)
            highlights_b = crud.get_highlights(db, request.book_id_b)
            
            if not highlights_a or not highlights_b:
                raise HTTPException(
                    status_code=400,
                    detail="두 책 모두 하이라이트가 있어야 합니다"
                )
            
            # 대표 하이라이트 선택 (첫 번째)
            highlight_a_text = highlights_a[0].original_text
            highlight_b_text = highlights_b[0].original_text
            
            # 거리 계산 (벡터 DB 사용)
            try:
                similar = vector_store.find_similar(highlight_a_text, n=20)
                distance = None
                for item in similar:
                    if str(item['metadata'].get('book_id')) == str(request.book_id_b):
                        distance = item.get('distance')
                        break
            except:
                distance = None
        
        elif request.mode == "semantic":
            # Semantic: Vector DB에서 의미적으로 연결된 쌍 찾기
            pairs = vector_store.find_semantic_pairs(
                source_book_id=None,  # 전체에서 찾기
                cross_genre=True,     # 다른 장르 우선
                min_similarity=0.5,
                top_k=1
            )

            if not pairs:
                raise HTTPException(
                    status_code=404,
                    detail="의미적으로 연결 가능한 하이라이트 쌍을 찾을 수 없습니다. 더 많은 하이라이트를 추가해주세요."
                )

            best_pair = pairs[0]

            # 책 정보 가져오기
            book_a = crud.get_book(db, best_pair["highlight_a"]["book_id"])
            book_b = crud.get_book(db, best_pair["highlight_b"]["book_id"])

            if not book_a or not book_b:
                raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")

            highlight_a_text = best_pair["highlight_a"]["text"]
            highlight_b_text = best_pair["highlight_b"]["text"]
            distance = 1 - best_pair["similarity_score"]  # 유사도를 거리로 변환

        elif request.mode == "random":
            # Random: 완전 랜덤 선택 (레거시)
            all_books = crud.get_books(db, limit=100)

            if len(all_books) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Random Mix를 위한 책이 부족합니다 (최소 2권 필요)"
                )

            # 하이라이트가 있는 책만 필터링
            books_with_highlights = []
            for book in all_books:
                highlights = crud.get_highlights(db, book.id)
                if highlights:
                    books_with_highlights.append(book)

            if len(books_with_highlights) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="하이라이트가 있는 책이 최소 2권 필요합니다"
                )

            # Random Mix로 서로 다른 책 선택
            import random
            random.shuffle(books_with_highlights)
            book_a = books_with_highlights[0]
            book_b = books_with_highlights[1]

            # 각 책의 하이라이트 가져오기
            highlights_a = crud.get_highlights(db, book_a.id)
            highlights_b = crud.get_highlights(db, book_b.id)

            highlight_a_text = highlights_a[0].original_text
            highlight_b_text = highlights_b[0].original_text

            # 거리 계산
            try:
                similar = vector_store.search(highlight_a_text, top_k=50)
                distance = None
                for item in similar:
                    if str(item['metadata'].get('book_id')) == str(book_b.id):
                        distance = 1 - item.get('score', 0)
                        break
            except:
                distance = None

        else:
            raise HTTPException(
                status_code=400,
                detail="mode는 'manual', 'semantic', 또는 'random'이어야 합니다"
            )
        
        # 2. AI 에이전트로 아이디어 연결
        print(f"🔗 Mix Ideas: {book_a.title} ↔ {book_b.title}")
        
        result = connection_agent.connect_ideas(
            highlight_a={
                "text": highlight_a_text,
                "book_title": book_a.title,
                "author": book_a.author,
                "genre": book_a.genre or ""
            },
            highlight_b={
                "text": highlight_b_text,
                "book_title": book_b.title,
                "author": book_b.author,
                "genre": book_b.genre or ""
            },
            user_context=request.user_context
        )
        
        # 3. ideas 테이블에 저장
        idea_data = {
            "book_id_a": book_a.id,
            "book_id_b": book_b.id,
            "connection_point": result['connection_point'],
            "new_idea": result['new_idea'],
            "why_it_works": result['why_it_works'],
            "example": result.get('example'),
            "user_context": request.user_context,
            "distance": distance
        }
        
        saved_idea = crud.create_idea(db, idea_data)
        
        # 4. 두 책 모두에 'connect' 활동 기록 (-40pt씩)
        activities = []
        
        # 책 A에 connect 활동
        activity_a = crud.create_activity(db, schemas.ActivityCreate(
            book_id=book_a.id,
            activity_type="connect",
            content=f"'{book_b.title}'와 연결: {result['connection_point'][:50]}..."
        ))
        activities.append(activity_a)
        
        # 책 B에 connect 활동
        activity_b = crud.create_activity(db, schemas.ActivityCreate(
            book_id=book_b.id,
            activity_type="connect",
            content=f"'{book_a.title}'와 연결: {result['connection_point'][:50]}..."
        ))
        activities.append(activity_b)
        
        # 5. 책 정보 다시 조회 (업데이트된 부채 포함)
        book_a_updated = crud.get_book(db, book_a.id)
        book_b_updated = crud.get_book(db, book_b.id)
        
        return {
            "idea": saved_idea,
            "book_a": book_a_updated,
            "book_b": book_b_updated,
            "activities_created": activities,
            "total_reduction": -80  # -40pt × 2
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Mix Ideas error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"아이디어 생성 실패: {str(e)}"
        )


@app.get("/ideas", response_model=List[schemas.IdeaResponse], tags=["Ideas"])
def get_ideas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    💡 저장된 아이디어 목록 조회
    
    - 최신순 정렬
    - 페이지네이션 지원
    """
    return crud.get_ideas(db, skip=skip, limit=limit)


@app.get("/ideas/{idea_id}", tags=["Ideas"])
def get_idea_detail(
    idea_id: int,
    db: Session = Depends(get_db)
):
    """
    💡 아이디어 상세 조회
    
    - 연결된 두 책 정보 포함
    """
    idea = crud.get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없습니다")
    
    book_a = crud.get_book(db, idea.book_id_a)
    book_b = crud.get_book(db, idea.book_id_b)
    
    import json
    why_it_works = json.loads(idea.why_it_works) if idea.why_it_works else []
    
    return {
        "idea": {
            **idea.__dict__,
            "why_it_works": why_it_works
        },
        "book_a": book_a,
        "book_b": book_b
    }


@app.get("/books/{book_id}/ideas", tags=["Ideas"])
def get_book_ideas(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    📚 특정 책과 연결된 아이디어들
    
    - 해당 책이 book_a 또는 book_b로 포함된 모든 아이디어
    """
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="책을 찾을 수 없습니다")
    
    ideas = crud.get_ideas_by_book(db, book_id)
    
    return {
        "book_id": book_id,
        "book_title": book.title,
        "total_ideas": len(ideas),
        "ideas": ideas
    }


# ============================================
# Notification 엔드포인트
# ============================================

@app.get("/notifications", response_model=List[schemas.NotificationResponse], tags=["Notifications"])
def get_notifications(
    is_read: Optional[bool] = Query(None, description="읽음 상태 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    📬 알림 목록 조회
    
    - 최신순 정렬
    - 읽음/안읽음 필터링 가능
    - 페이지네이션 지원
    """
    return crud.get_notifications(db, is_read=is_read, skip=skip, limit=limit)


@app.get("/notifications/unread-count", tags=["Notifications"])
def get_unread_count(db: Session = Depends(get_db)):
    """
    🔔 읽지 않은 알림 수
    
    - 배지 표시용
    """
    count = crud.get_unread_count(db)
    return {"unread_count": count}


@app.patch("/notifications/{notification_id}", response_model=schemas.NotificationResponse, tags=["Notifications"])
def update_notification(
    notification_id: int,
    update: schemas.NotificationUpdate,
    db: Session = Depends(get_db)
):
    """
    ✅ 알림 읽음 처리
    
    - 개별 알림 읽음 상태 변경
    """
    notification = crud.update_notification(db, notification_id, update.is_read)
    if not notification:
        raise HTTPException(status_code=404, detail="알림을 찾을 수 없습니다")
    
    return notification


@app.post("/notifications/mark-all-read", tags=["Notifications"])
def mark_all_as_read(db: Session = Depends(get_db)):
    """
    ✅ 모든 알림 읽음 처리
    
    - 한 번에 모든 알림을 읽음으로 표시
    """
    crud.mark_all_as_read(db)
    return {"message": "모든 알림을 읽음 처리했습니다"}


@app.post("/notifications/run-checks", tags=["Notifications"])
def run_notification_checks():
    """
    🔧 알림 체크 수동 실행 (테스트용)
    
    - 모든 스케줄된 체크를 즉시 실행
    - 개발/테스트 목적
    """
    try:
        run_all_checks_now()
        return {"message": "모든 알림 체크가 실행되었습니다"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"알림 체크 실행 실패: {str(e)}"
        )


# ============================================
# Semantic Mix (의미적 브릿지) 엔드포인트
# ============================================

@app.post("/ai/mix-highlights", response_model=schemas.SemanticMixResponse, tags=["AI Agent"])
def mix_highlights(
    request: schemas.SemanticMixRequest,
    db: Session = Depends(get_db)
):
    """
    의미적으로 연결된 하이라이트를 찾고 인사이트를 생성합니다.

    - Vector DB에서 다른 책의 유사한 하이라이트 쌍을 찾음
    - AI가 두 개념의 교차점에서 새로운 인사이트 생성
    - cross_genre=True면 다른 장르 우선

    ⚠️ GOOGLE_API_KEY 환경변수 필요
    """
    # API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY 환경변수가 설정되지 않았습니다"
        )

    try:
        # 1. Vector DB에서 의미적 쌍 찾기
        vector_store = get_vector_store()
        pairs = vector_store.find_semantic_pairs(
            source_book_id=request.book_id,
            cross_genre=request.cross_genre,
            min_similarity=request.min_similarity,
            top_k=1  # 가장 좋은 쌍 1개만
        )

        if not pairs:
            raise HTTPException(
                status_code=404,
                detail="연결 가능한 하이라이트 쌍을 찾을 수 없습니다. 더 많은 하이라이트를 추가해주세요."
            )

        best_pair = pairs[0]

        # 2. Mix Agent로 인사이트 생성
        mix_agent = get_mix_agent()
        mix_request = MixRequest(
            highlight_a=HighlightInfo(
                text=best_pair["highlight_a"]["text"],
                book_title=best_pair["highlight_a"]["book_title"],
                author=best_pair["highlight_a"]["author"],
                genre=best_pair["highlight_a"]["genre"]
            ),
            highlight_b=HighlightInfo(
                text=best_pair["highlight_b"]["text"],
                book_title=best_pair["highlight_b"]["book_title"],
                author=best_pair["highlight_b"]["author"],
                genre=best_pair["highlight_b"]["genre"]
            ),
            similarity_score=best_pair["similarity_score"]
        )

        result = mix_agent.generate_connection(mix_request)

        # 3. 응답 구성
        return schemas.SemanticMixResponse(
            pair=schemas.SemanticPairResponse(
                highlight_a=schemas.HighlightPairInfo(**best_pair["highlight_a"]),
                highlight_b=schemas.HighlightPairInfo(**best_pair["highlight_b"]),
                similarity_score=best_pair["similarity_score"],
                is_cross_genre=best_pair["is_cross_genre"]
            ),
            insight=schemas.SemanticMixResult(
                connection_point=result.connection_point,
                new_idea=result.new_idea,
                why_it_works=result.why_it_works,
                action_suggestion=result.action_suggestion
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mix 생성 실패: {str(e)}"
        )


@app.get("/ai/semantic-pairs", tags=["AI Agent"])
def get_semantic_pairs(
    book_id: Optional[int] = Query(None, description="특정 책 기준"),
    cross_genre: bool = Query(True, description="다른 장르 우선"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="최소 유사도"),
    top_k: int = Query(5, ge=1, le=20, description="반환할 쌍 수")
):
    """
    의미적으로 연결된 하이라이트 쌍 목록을 반환합니다 (AI 생성 없이).

    - 프론트엔드에서 미리보기용
    - 사용자가 원하는 쌍 선택 가능
    """
    try:
        vector_store = get_vector_store()
        pairs = vector_store.find_semantic_pairs(
            source_book_id=book_id,
            cross_genre=cross_genre,
            min_similarity=min_similarity,
            top_k=top_k
        )
        return {"pairs": pairs, "count": len(pairs)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"검색 실패: {str(e)}"
        )


# ============================================
# 서버 실행 (개발용)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


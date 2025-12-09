"""
LanceDB 기반 벡터 저장소
- Serverless & Embedded
- Disk-based Indexing (메모리 효율적)
- 락 문제 없음
"""
import os
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import lancedb
from lancedb.pydantic import LanceModel, Vector
import google.generativeai as genai

# .env 파일 로드
load_dotenv()

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Gemini API 설정됨")
else:
    print("⚠️ GOOGLE_API_KEY not set")

# 임베딩 차원 (Gemini text-embedding-004)
EMBEDDING_DIM = 768


class HighlightSchema(LanceModel):
    """하이라이트 벡터 스키마"""
    highlight_id: int
    text: str
    book_id: int
    book_title: str
    author: str
    genre: str
    page: int
    vector: Vector(EMBEDDING_DIM)


class LanceVectorStore:
    """LanceDB 기반 벡터 저장소"""

    def __init__(self, db_path: str = None):
        # 외부 볼륨에서는 rename 작업이 실패할 수 있어서 로컬 경로 사용
        if db_path is None:
            import tempfile
            db_path = os.path.join(tempfile.gettempdir(), "knowledge_debt_lancedb")
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self.table_name = "highlights"
        self._init_table()
        print(f"✅ LanceVectorStore 초기화: {db_path}")
        print(f"   📊 저장된 벡터 수: {self.count()}")

    def _init_table(self):
        """테이블 생성/로드"""
        try:
            if self.table_name in self.db.table_names():
                self.table = self.db.open_table(self.table_name)
            else:
                # 빈 테이블 생성
                self.table = self.db.create_table(
                    self.table_name,
                    schema=HighlightSchema,
                    mode="overwrite"
                )
        except Exception as e:
            print(f"⚠️ 테이블 열기 실패, 새로 생성: {e}")
            # 기존 테이블 삭제 후 재생성
            try:
                self.db.drop_table(self.table_name)
            except Exception:
                pass
            self.table = self.db.create_table(
                self.table_name,
                schema=HighlightSchema,
                mode="overwrite"
            )

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Gemini API로 임베딩 생성"""
        if not GOOGLE_API_KEY:
            print("⚠️ GOOGLE_API_KEY 없음 - 임베딩 생성 불가")
            return None

        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            return result['embedding']
        except Exception as e:
            print(f"⚠️ 임베딩 생성 실패: {e}")
            return None

    def add_highlight(
        self,
        highlight_id: int,
        text: str,
        metadata: Dict
    ) -> bool:
        """하이라이트 벡터 저장"""
        # 이미 존재하는지 확인
        try:
            existing = self.table.search().where(
                f"highlight_id = {highlight_id}"
            ).limit(1).to_list()
            if existing:
                print(f"⏭️ 이미 존재: highlight #{highlight_id}")
                return False
        except Exception:
            pass  # 테이블이 비어있으면 에러 발생 가능

        # 임베딩 생성
        embedding = self._get_embedding(text)
        if embedding is None:
            return False

        # 저장
        data = {
            "highlight_id": highlight_id,
            "text": text,
            "book_id": metadata.get("book_id", 0),
            "book_title": metadata.get("book_title", ""),
            "author": metadata.get("author", ""),
            "genre": metadata.get("genre", ""),
            "page": metadata.get("page", 0),
            "vector": embedding
        }

        self.table.add([data])
        print(f"✅ 벡터 저장: highlight #{highlight_id}")
        return True

    def search(
        self,
        query_text: str,
        top_k: int = 5,
        exclude_book_id: Optional[int] = None
    ) -> List[Dict]:
        """유사한 하이라이트 검색"""
        query_embedding = self._get_embedding(query_text)
        if query_embedding is None:
            return []

        try:
            # 벡터 검색
            results = self.table.search(query_embedding).limit(top_k * 2).to_list()

            # 필터링 및 변환
            output = []
            for row in results:
                if exclude_book_id and row.get("book_id") == exclude_book_id:
                    continue
                output.append({
                    "highlight_id": row["highlight_id"],
                    "text": row["text"],
                    "metadata": {
                        "book_id": row["book_id"],
                        "book_title": row["book_title"],
                        "author": row["author"],
                        "genre": row["genre"],
                        "page": row["page"]
                    },
                    "score": 1 - row.get("_distance", 0)  # 거리를 유사도로 변환
                })

            return output[:top_k]
        except Exception as e:
            print(f"⚠️ 검색 실패: {e}")
            return []

    def find_connections(
        self,
        book_id: int,
        top_k: int = 3
    ) -> List[Dict]:
        """특정 책과 연결 가능한 다른 책들의 하이라이트 찾기"""
        try:
            # 해당 책의 하이라이트들 가져오기
            book_highlights = self.table.search().where(
                f"book_id = {book_id}"
            ).limit(100).to_list()

            if not book_highlights:
                return []

            # 각 하이라이트에 대해 다른 책에서 유사한 것 찾기
            all_connections = []
            for row in book_highlights:
                similar = self.search(row["text"], top_k=top_k, exclude_book_id=book_id)
                all_connections.extend(similar)

            # 중복 제거 및 점수순 정렬
            seen = set()
            unique_connections = []
            for conn in sorted(all_connections, key=lambda x: x["score"], reverse=True):
                if conn["highlight_id"] not in seen:
                    seen.add(conn["highlight_id"])
                    unique_connections.append(conn)

            return unique_connections[:top_k]
        except Exception as e:
            print(f"⚠️ 연결 찾기 실패: {e}")
            return []

    def get_random_pair(
        self,
        different_genre: bool = True
    ) -> Optional[Tuple[Dict, Dict]]:
        """랜덤 하이라이트 쌍 (세렌디피티용)"""
        import random

        try:
            all_highlights = self.table.search().limit(1000).to_list()

            if len(all_highlights) < 2:
                return None

            # 첫 번째 랜덤 선택
            first = random.choice(all_highlights)

            # 두 번째 선택 (다른 장르 우선)
            candidates = []
            for row in all_highlights:
                if row["highlight_id"] == first["highlight_id"]:
                    continue
                if different_genre:
                    if row["genre"] != first["genre"]:
                        candidates.append(row)
                else:
                    candidates.append(row)

            if not candidates:
                candidates = [r for r in all_highlights if r["highlight_id"] != first["highlight_id"]]

            if not candidates:
                return None

            second = random.choice(candidates)

            def to_dict(row):
                return {
                    "highlight_id": row["highlight_id"],
                    "text": row["text"],
                    "metadata": {
                        "book_id": row["book_id"],
                        "book_title": row["book_title"],
                        "author": row["author"],
                        "genre": row["genre"],
                        "page": row["page"]
                    }
                }

            return (to_dict(first), to_dict(second))
        except Exception as e:
            print(f"⚠️ 랜덤 쌍 생성 실패: {e}")
            return None

    def find_semantic_pairs(
        self,
        source_book_id: Optional[int] = None,
        cross_genre: bool = True,
        min_similarity: float = 0.7,
        top_k: int = 5
    ) -> List[Dict]:
        """
        의미적으로 연결된 하이라이트 쌍 찾기 (다른 책에서)

        Args:
            source_book_id: 특정 책 기준 (None이면 전체)
            cross_genre: True면 다른 장르 우선
            min_similarity: 최소 유사도 임계값 (0~1)
            top_k: 반환할 쌍의 수
        """
        try:
            # 소스 하이라이트 가져오기
            if source_book_id:
                source_highlights = self.table.search().where(
                    f"book_id = {source_book_id}"
                ).limit(100).to_list()
            else:
                source_highlights = self.table.search().limit(500).to_list()

            if len(source_highlights) < 1:
                return []

            # 모든 쌍의 유사도 계산
            pairs = []
            for source in source_highlights:
                # 해당 하이라이트의 벡터로 유사한 것 검색
                results = self.table.search(source["vector"]).limit(20).to_list()

                for target in results:
                    # 같은 책 제외
                    if target["book_id"] == source["book_id"]:
                        continue

                    # 이미 추가된 쌍인지 확인 (양방향)
                    pair_key = tuple(sorted([source["highlight_id"], target["highlight_id"]]))
                    if any(p.get("pair_key") == pair_key for p in pairs):
                        continue

                    # 유사도 계산 (거리를 유사도로 변환)
                    similarity = 1 - target.get("_distance", 0)

                    # 최소 유사도 필터
                    if similarity < min_similarity:
                        continue

                    # cross_genre 필터
                    is_cross_genre = source["genre"] != target["genre"]
                    if cross_genre and not is_cross_genre:
                        continue

                    pairs.append({
                        "pair_key": pair_key,
                        "similarity_score": similarity,
                        "is_cross_genre": is_cross_genre,
                        "highlight_a": {
                            "highlight_id": source["highlight_id"],
                            "text": source["text"],
                            "book_id": source["book_id"],
                            "book_title": source["book_title"],
                            "author": source["author"],
                            "genre": source["genre"],
                            "page": source["page"]
                        },
                        "highlight_b": {
                            "highlight_id": target["highlight_id"],
                            "text": target["text"],
                            "book_id": target["book_id"],
                            "book_title": target["book_title"],
                            "author": target["author"],
                            "genre": target["genre"],
                            "page": target["page"]
                        }
                    })

            # 유사도순 정렬 후 상위 반환
            pairs.sort(key=lambda x: x["similarity_score"], reverse=True)

            # pair_key 제거 후 반환
            for p in pairs:
                del p["pair_key"]

            return pairs[:top_k]

        except Exception as e:
            print(f"⚠️ 의미적 쌍 찾기 실패: {e}")
            return []

    def count(self) -> int:
        """저장된 벡터 수"""
        try:
            return self.table.count_rows()
        except Exception:
            return 0

    def delete(self, highlight_id: int) -> bool:
        """벡터 삭제"""
        try:
            self.table.delete(f"highlight_id = {highlight_id}")
            return True
        except Exception as e:
            print(f"⚠️ 삭제 실패: {e}")
            return False


# 싱글톤 인스턴스
_vector_store: Optional[LanceVectorStore] = None


def get_vector_store() -> LanceVectorStore:
    """벡터 저장소 인스턴스 반환"""
    global _vector_store
    if _vector_store is None:
        _vector_store = LanceVectorStore()
    return _vector_store

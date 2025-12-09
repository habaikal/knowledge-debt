"""
SQLite + numpy 기반 간단한 벡터 저장소
ChromaDB 대체 - 더 가볍고 안정적
"""
import sqlite3
import json
import numpy as np
import os
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()

# Gemini API 설정
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(f"✅ Gemini API 설정됨")


class SimpleVectorStore:
    """SQLite 기반 벡터 저장소"""

    def __init__(self, db_path: str = "./highlight_vectors.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_table()
        print(f"✅ SimpleVectorStore 초기화: {db_path}")
        print(f"   📊 저장된 벡터 수: {self.count()}")

    def _init_table(self):
        """테이블 생성"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                highlight_id INTEGER UNIQUE,
                embedding BLOB,
                text TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_highlight_id ON vectors(highlight_id)
        """)
        self.conn.commit()

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Gemini API로 임베딩 생성"""
        if not GOOGLE_API_KEY:
            print("⚠️ GOOGLE_API_KEY 없음 - 임베딩 생성 불가")
            return None

        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text
            )
            return np.array(result['embedding'], dtype=np.float32)
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
        existing = self.conn.execute(
            "SELECT id FROM vectors WHERE highlight_id = ?",
            (highlight_id,)
        ).fetchone()

        if existing:
            print(f"⏭️ 이미 존재: highlight #{highlight_id}")
            return False

        # 임베딩 생성
        embedding = self._get_embedding(text)
        if embedding is None:
            return False

        # 저장
        self.conn.execute(
            """INSERT INTO vectors (highlight_id, embedding, text, metadata)
               VALUES (?, ?, ?, ?)""",
            (highlight_id, embedding.tobytes(), text, json.dumps(metadata, ensure_ascii=False))
        )
        self.conn.commit()
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

        # 모든 벡터 로드
        rows = self.conn.execute(
            "SELECT highlight_id, embedding, text, metadata FROM vectors"
        ).fetchall()

        if not rows:
            return []

        # 코사인 유사도 계산
        scores = []
        for row in rows:
            highlight_id, emb_bytes, text, metadata_json = row
            metadata = json.loads(metadata_json)

            # 특정 책 제외 (같은 책 내 검색 방지)
            if exclude_book_id and metadata.get("book_id") == exclude_book_id:
                continue

            emb = np.frombuffer(emb_bytes, dtype=np.float32)

            # 코사인 유사도
            score = np.dot(query_embedding, emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb) + 1e-8
            )

            scores.append({
                "highlight_id": highlight_id,
                "text": text,
                "metadata": metadata,
                "score": float(score)
            })

        # 점수순 정렬
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

    def find_connections(
        self,
        book_id: int,
        top_k: int = 3
    ) -> List[Dict]:
        """특정 책과 연결 가능한 다른 책들의 하이라이트 찾기"""
        # 해당 책의 하이라이트들 가져오기
        rows = self.conn.execute(
            """SELECT text, metadata FROM vectors
               WHERE json_extract(metadata, '$.book_id') = ?""",
            (book_id,)
        ).fetchall()

        if not rows:
            return []

        # 각 하이라이트에 대해 다른 책에서 유사한 것 찾기
        all_connections = []
        for text, _ in rows:
            similar = self.search(text, top_k=top_k, exclude_book_id=book_id)
            all_connections.extend(similar)

        # 중복 제거 및 점수순 정렬
        seen = set()
        unique_connections = []
        for conn in sorted(all_connections, key=lambda x: x["score"], reverse=True):
            if conn["highlight_id"] not in seen:
                seen.add(conn["highlight_id"])
                unique_connections.append(conn)

        return unique_connections[:top_k]

    def get_random_pair(
        self,
        different_genre: bool = True
    ) -> Optional[Tuple[Dict, Dict]]:
        """랜덤 하이라이트 쌍 (세렌디피티용)"""
        rows = self.conn.execute(
            "SELECT highlight_id, text, metadata FROM vectors"
        ).fetchall()

        if len(rows) < 2:
            return None

        import random

        # 첫 번째 랜덤 선택
        first = random.choice(rows)
        first_metadata = json.loads(first[2])

        # 두 번째 선택 (다른 장르 우선)
        candidates = []
        for row in rows:
            if row[0] == first[0]:  # 같은 것 제외
                continue
            metadata = json.loads(row[2])
            if different_genre:
                if metadata.get("genre") != first_metadata.get("genre"):
                    candidates.append(row)
            else:
                candidates.append(row)

        if not candidates:
            candidates = [r for r in rows if r[0] != first[0]]

        if not candidates:
            return None

        second = random.choice(candidates)

        return (
            {"highlight_id": first[0], "text": first[1], "metadata": json.loads(first[2])},
            {"highlight_id": second[0], "text": second[1], "metadata": json.loads(second[2])}
        )

    def count(self) -> int:
        """저장된 벡터 수"""
        result = self.conn.execute("SELECT COUNT(*) FROM vectors").fetchone()
        return result[0] if result else 0

    def delete(self, highlight_id: int) -> bool:
        """벡터 삭제"""
        self.conn.execute(
            "DELETE FROM vectors WHERE highlight_id = ?",
            (highlight_id,)
        )
        self.conn.commit()
        return True

    def close(self):
        """연결 종료"""
        self.conn.close()


# 싱글톤 인스턴스
_vector_store: Optional[SimpleVectorStore] = None


def get_vector_store() -> SimpleVectorStore:
    """벡터 저장소 인스턴스 반환"""
    global _vector_store
    if _vector_store is None:
        _vector_store = SimpleVectorStore()
    return _vector_store

"""
ChromaDB를 사용한 하이라이트 벡터 저장 시스템
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
import google.generativeai as genai

# 임베딩 타입
EMBEDDING_TYPE = os.getenv("EMBEDDING_TYPE", "local")  # "local" or "gemini"

# Gemini API 설정 (선택적)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class VectorStore:
    """하이라이트 벡터 저장소"""
    
    def __init__(
        self, 
        collection_name: str = "highlights",
        persist_directory: str = "./chroma_db"
    ):
        """
        Args:
            collection_name: 컬렉션 이름
            persist_directory: 로컬 저장 경로
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # ChromaDB 클라이언트 생성 (persistent 모드)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 임베딩 함수 설정
        self.embedding_function = self._get_embedding_function()
        
        # 컬렉션 생성 또는 가져오기
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Book highlights vector store"}
        )
        
        print(f"✅ VectorStore initialized: {collection_name}")
        print(f"   📁 Directory: {persist_directory}")
        print(f"   🔢 Count: {self.collection.count()} vectors")
        print(f"   🤖 Embedding: {EMBEDDING_TYPE}")
    
    def _get_embedding_function(self):
        """임베딩 함수 선택"""
        if EMBEDDING_TYPE == "gemini" and GOOGLE_API_KEY:
            print("   Using Gemini Embedding (text-embedding-004)")
            from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
            return GoogleGenerativeAiEmbeddingFunction(
                api_key=GOOGLE_API_KEY,
                model_name="models/text-embedding-004"
            )
        else:
            print("   Using Local Embedding (all-MiniLM-L6-v2)")
            from chromadb.utils import embedding_functions
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
    
    def add_highlight(
        self,
        highlight_id: int,
        text: str,
        metadata: Dict
    ) -> bool:
        """
        하이라이트 추가
        
        Args:
            highlight_id: 하이라이트 ID
            text: 하이라이트 텍스트
            metadata: {
                "book_id": int,
                "book_title": str,
                "author": str,
                "genre": str,
                "page": int
            }
        
        Returns:
            bool: 성공 여부
        """
        try:
            # 메타데이터 타입 변환 (ChromaDB는 str, int, float, bool만 지원)
            clean_metadata = {
                "book_id": str(metadata.get("book_id", "")),
                "book_title": str(metadata.get("book_title", "")),
                "author": str(metadata.get("author", "")),
                "genre": str(metadata.get("genre", "")),
                "page": str(metadata.get("page", ""))
            }
            
            self.collection.add(
                ids=[f"highlight_{highlight_id}"],
                documents=[text],
                metadatas=[clean_metadata]
            )
            
            return True
        
        except Exception as e:
            print(f"❌ Error adding highlight: {e}")
            return False
    
    def find_similar(
        self,
        text: str,
        n: int = 5,
        book_id: Optional[int] = None
    ) -> List[Dict]:
        """
        유사한 하이라이트 검색
        
        Args:
            text: 검색할 텍스트
            n: 반환할 결과 수
            book_id: 특정 책으로 필터링 (선택)
        
        Returns:
            List[Dict]: 유사한 하이라이트 목록
        """
        try:
            # where 조건 설정
            where_clause = None
            if book_id:
                where_clause = {"book_id": str(book_id)}
            
            results = self.collection.query(
                query_texts=[text],
                n_results=n,
                where=where_clause
            )
            
            # 결과 포맷팅
            similar_highlights = []
            
            if results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    similar_highlights.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            
            return similar_highlights
        
        except Exception as e:
            print(f"❌ Error searching similar highlights: {e}")
            return []
    
    def find_connections(
        self,
        book_id: int,
        n: int = 3,
        exclude_same_book: bool = True
    ) -> List[Dict]:
        """
        특정 책과 연결 가능한 다른 책들 찾기
        
        Args:
            book_id: 기준 책 ID
            n: 반환할 책 수
            exclude_same_book: 같은 책 제외 여부
        
        Returns:
            List[Dict]: 연결된 책 정보
        """
        try:
            # 해당 책의 모든 하이라이트 가져오기
            book_highlights = self.collection.get(
                where={"book_id": str(book_id)}
            )
            
            if not book_highlights['documents']:
                return []
            
            # 모든 하이라이트에 대해 유사한 하이라이트 검색
            connections = {}
            
            for doc in book_highlights['documents'][:5]:  # 최대 5개 하이라이트만 검색
                similar = self.find_similar(doc, n=10)
                
                for item in similar:
                    other_book_id = item['metadata'].get('book_id')
                    
                    # 같은 책 제외
                    if exclude_same_book and other_book_id == str(book_id):
                        continue
                    
                    if other_book_id not in connections:
                        connections[other_book_id] = {
                            "book_id": other_book_id,
                            "book_title": item['metadata'].get('book_title'),
                            "author": item['metadata'].get('author'),
                            "genre": item['metadata'].get('genre'),
                            "connection_count": 0,
                            "similar_highlights": []
                        }
                    
                    connections[other_book_id]['connection_count'] += 1
                    connections[other_book_id]['similar_highlights'].append({
                        "text": item['text'],
                        "page": item['metadata'].get('page')
                    })
            
            # 연결 수로 정렬
            sorted_connections = sorted(
                connections.values(),
                key=lambda x: x['connection_count'],
                reverse=True
            )
            
            return sorted_connections[:n]
        
        except Exception as e:
            print(f"❌ Error finding connections: {e}")
            return []
    
    def get_by_book(self, book_id: int) -> List[Dict]:
        """특정 책의 모든 하이라이트 가져오기"""
        try:
            results = self.collection.get(
                where={"book_id": str(book_id)}
            )
            
            highlights = []
            for i in range(len(results['ids'])):
                highlights.append({
                    "id": results['ids'][i],
                    "text": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })
            
            return highlights
        
        except Exception as e:
            print(f"❌ Error getting highlights: {e}")
            return []
    
    def delete_highlight(self, highlight_id: int) -> bool:
        """하이라이트 삭제"""
        try:
            self.collection.delete(
                ids=[f"highlight_{highlight_id}"]
            )
            return True
        
        except Exception as e:
            print(f"❌ Error deleting highlight: {e}")
            return False
    
    def find_random_mix(
        self,
        n: int = 2,
        min_distance: float = 0.7
    ) -> List[Dict]:
        """
        유사도가 낮은 하이라이트 무작위 매칭
        세렌디피티를 위한 '전혀 다른' 개념 연결
        
        Args:
            n: 반환할 하이라이트 수
            min_distance: 최소 거리 (높을수록 더 다름)
        
        Returns:
            List[Dict]: 서로 다른 하이라이트들
        """
        try:
            # 전체 벡터 수 확인
            total = self.collection.count()
            
            if total < n:
                print(f"⚠️ Not enough vectors: {total} < {n}")
                return []
            
            # 랜덤하게 하나 선택
            import random
            all_data = self.collection.get()
            
            if not all_data['documents']:
                return []
            
            # 첫 번째 하이라이트 선택
            random_idx = random.randint(0, len(all_data['documents']) - 1)
            seed_text = all_data['documents'][random_idx]
            
            # 유사도 검색으로 가장 다른 것들 찾기
            # (거리가 먼 순으로 정렬하기 위해 많이 조회)
            results = self.collection.query(
                query_texts=[seed_text],
                n_results=min(total, 50)
            )
            
            # 거리 기준으로 필터링 (거리가 큰 것 = 다른 것)
            mixed_highlights = []
            
            if results['ids'][0]:
                # 첫 번째는 seed 자체
                mixed_highlights.append({
                    "id": results['ids'][0][0],
                    "text": results['documents'][0][0],
                    "metadata": results['metadatas'][0][0],
                    "distance": 0
                })
                
                # 나머지는 거리가 먼 순으로
                for i in range(len(results['ids'][0]) - 1, 0, -1):
                    if len(mixed_highlights) >= n:
                        break
                    
                    distance = results['distances'][0][i] if 'distances' in results else 1.0
                    
                    # 최소 거리 조건 확인
                    if distance >= min_distance:
                        mixed_highlights.append({
                            "id": results['ids'][0][i],
                            "text": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i],
                            "distance": distance
                        })
            
            # 부족하면 랜덤으로 채우기
            if len(mixed_highlights) < n:
                remaining = n - len(mixed_highlights)
                existing_ids = {h['id'] for h in mixed_highlights}
                
                for _ in range(remaining):
                    candidates = [
                        i for i in range(len(all_data['documents']))
                        if f"highlight_{all_data['ids'][i]}" not in existing_ids
                    ]
                    
                    if candidates:
                        idx = random.choice(candidates)
                        mixed_highlights.append({
                            "id": all_data['ids'][idx],
                            "text": all_data['documents'][idx],
                            "metadata": all_data['metadatas'][idx],
                            "distance": None
                        })
            
            return mixed_highlights[:n]
        
        except Exception as e:
            print(f"❌ Error finding random mix: {e}")
            return []
    
    def count(self) -> int:
        """전체 벡터 수"""
        return self.collection.count()
    
    def reset(self):
        """컬렉션 초기화 (주의!)"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        print(f"⚠️  Collection reset: {self.collection_name}")


# 싱글톤 인스턴스
_vector_store = None

def get_vector_store() -> VectorStore:
    """VectorStore 싱글톤 인스턴스 반환"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


# ============================================
# 테스트 코드
# ============================================

if __name__ == "__main__":
    print("🧪 VectorStore 테스트\n")
    
    # VectorStore 생성
    store = VectorStore(persist_directory="./test_chroma_db")
    
    # 테스트 데이터
    test_highlights = [
        {
            "id": 1,
            "text": "1%의 개선이 매일 쌓이면 1년 후 37배 나아진다.",
            "metadata": {
                "book_id": 1,
                "book_title": "아주 작은 습관의 힘",
                "author": "제임스 클리어",
                "genre": "자기계발",
                "page": 15
            }
        },
        {
            "id": 2,
            "text": "습관은 자아 정체성의 구체화다.",
            "metadata": {
                "book_id": 1,
                "book_title": "아주 작은 습관의 힘",
                "author": "제임스 클리어",
                "genre": "자기계발",
                "page": 45
            }
        },
        {
            "id": 3,
            "text": "나쁜 코드는 나중에 치워도 괜찮다는 거짓말을 하지 마라.",
            "metadata": {
                "book_id": 2,
                "book_title": "클린 코드",
                "author": "로버트 C. 마틴",
                "genre": "프로그래밍",
                "page": 23
            }
        },
        {
            "id": 4,
            "text": "작은 변화가 큰 차이를 만든다.",
            "metadata": {
                "book_id": 3,
                "book_title": "티핑 포인트",
                "author": "말콤 글래드웰",
                "genre": "사회학",
                "page": 100
            }
        },
    ]
    
    # 1. 하이라이트 추가
    print("📝 1. 하이라이트 추가")
    for highlight in test_highlights:
        store.add_highlight(
            highlight['id'],
            highlight['text'],
            highlight['metadata']
        )
        print(f"   ✅ Added: {highlight['text'][:50]}...")
    
    print(f"\n   총 {store.count()}개 벡터 저장됨\n")
    
    # 2. 유사한 하이라이트 검색
    print("🔍 2. 유사한 하이라이트 검색")
    query = "점진적으로 개선하는 것이 중요하다"
    print(f"   Query: {query}\n")
    
    similar = store.find_similar(query, n=3)
    for i, item in enumerate(similar, 1):
        print(f"   {i}. {item['text']}")
        print(f"      📚 {item['metadata']['book_title']}")
        print(f"      📄 Page {item['metadata']['page']}")
        if item['distance']:
            print(f"      🎯 Distance: {item['distance']:.4f}")
        print()
    
    # 3. 책 간 연결 찾기
    print("🔗 3. 책 간 연결 찾기")
    book_id = 1
    print(f"   Book ID: {book_id} (아주 작은 습관의 힘)\n")
    
    connections = store.find_connections(book_id, n=2)
    for i, conn in enumerate(connections, 1):
        print(f"   {i}. 📚 {conn['book_title']}")
        print(f"      👤 {conn['author']}")
        print(f"      🔗 {conn['connection_count']}개 연결점")
        print(f"      💡 유사 하이라이트:")
        for highlight in conn['similar_highlights'][:2]:
            print(f"         - {highlight['text'][:50]}... (p.{highlight['page']})")
        print()
    
    # 4. Random Mix - 전혀 다른 개념 매칭
    print("🎲 4. Random Mix - 세렌디피티 매칭")
    print("   (유사도가 낮은 하이라이트끼리 매칭)\n")
    
    random_mix = store.find_random_mix(n=2, min_distance=0.5)
    for i, item in enumerate(random_mix, 1):
        print(f"   {i}. {item['text']}")
        print(f"      📚 {item['metadata']['book_title']}")
        if item['distance']:
            print(f"      📏 Distance: {item['distance']:.4f}")
        print()
    
    print("✅ 테스트 완료!")


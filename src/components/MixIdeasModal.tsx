import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

interface Book {
  id: number;
  title: string;
  author: string;
}

interface HighlightInfo {
  highlight_id: number;
  text: string;
  book_id: number;
  book_title: string;
  author: string;
  genre: string;
  page: number;
}

interface MixResult {
  idea: {
    id: number;
    connection_point: string;
    new_idea: string;
    why_it_works: string;
    example: string | null;
  };
  book_a: Book;
  book_b: Book;
  total_reduction: number;
}

interface MixIdeasModalProps {
  isOpen: boolean;
  onClose: () => void;
  books: Book[];
  onMixComplete: () => void;
}

export function MixIdeasModal({
  isOpen,
  onClose,
  books,
  onMixComplete,
}: MixIdeasModalProps) {
  const [mode, setMode] = useState<'semantic' | 'manual'>('semantic');
  const [bookAId, setBookAId] = useState<number | null>(null);
  const [bookBId, setBookBId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MixResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 모달 닫힐 때 상태 초기화
  useEffect(() => {
    if (!isOpen) {
      setResult(null);
      setError(null);
      setMode('semantic');
      setBookAId(null);
      setBookBId(null);
    }
  }, [isOpen]);

  // Mix 실행
  const handleMix = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload: any = { mode };

      if (mode === 'manual') {
        if (!bookAId || !bookBId) {
          throw new Error('두 권의 책을 선택해주세요');
        }
        if (bookAId === bookBId) {
          throw new Error('서로 다른 책을 선택해주세요');
        }
        payload.book_id_a = bookAId;
        payload.book_id_b = bookBId;
      }

      const response = await fetch('http://localhost:8000/ai/mix-ideas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Mix 생성에 실패했습니다');
      }

      const data = await response.json();
      setResult(data);

      toast.success(
        <div className="flex flex-col gap-1">
          <div className="font-bold">💡 새로운 인사이트 발견!</div>
          <div className="text-green-600 font-semibold">{data.total_reduction}pt 탕감</div>
        </div>,
        { duration: 4000 }
      );

      onMixComplete();
    } catch (err: any) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* 배경 오버레이 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* 모달 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-slate-900 rounded-2xl shadow-2xl border border-slate-700"
          >
            {/* 헤더 */}
            <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 z-10">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                    🔗 아이디어 Mix
                  </h2>
                  <p className="text-sm text-gray-400">
                    서로 다른 책의 하이라이트를 연결해 새로운 인사이트를 발견하세요
                  </p>
                </div>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-white transition-colors text-2xl"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* 본문 */}
            <div className="p-6 space-y-6">
              {/* 결과가 없을 때: 모드 선택 */}
              {!result && (
                <>
                  {/* 모드 선택 */}
                  <div>
                    <label className="block text-sm font-medium text-purple-200 mb-3">
                      Mix 모드 선택
                    </label>
                    <div className="flex gap-4">
                      <button
                        onClick={() => setMode('semantic')}
                        style={{
                          backgroundColor: mode === 'semantic' ? 'rgba(139, 92, 246, 0.3)' : '#1e293b',
                          borderColor: mode === 'semantic' ? '#a855f7' : '#475569',
                        }}
                        className="flex-1 p-4 rounded-xl border-2 transition-all"
                      >
                        <div className="text-2xl mb-2">🧠</div>
                        <div className="text-white font-bold mb-1">Semantic Mix</div>
                        <div className="text-xs text-gray-300">
                          AI가 의미적으로 연결된 하이라이트를 자동 발견
                        </div>
                      </button>
                      <button
                        onClick={() => setMode('manual')}
                        style={{
                          backgroundColor: mode === 'manual' ? 'rgba(139, 92, 246, 0.3)' : '#1e293b',
                          borderColor: mode === 'manual' ? '#a855f7' : '#475569',
                        }}
                        className="flex-1 p-4 rounded-xl border-2 transition-all"
                      >
                        <div className="text-2xl mb-2">✋</div>
                        <div className="text-white font-bold mb-1">Manual Mix</div>
                        <div className="text-xs text-gray-300">
                          직접 두 권의 책을 선택해 연결
                        </div>
                      </button>
                    </div>
                  </div>

                  {/* Manual 모드: 책 선택 */}
                  {mode === 'manual' && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-purple-200 mb-2">
                          📖 책 A
                        </label>
                        <select
                          value={bookAId || ''}
                          onChange={(e) => setBookAId(Number(e.target.value) || null)}
                          className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="">책을 선택하세요</option>
                          {books.map((book) => (
                            <option key={book.id} value={book.id}>
                              {book.title} - {book.author}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-purple-200 mb-2">
                          📖 책 B
                        </label>
                        <select
                          value={bookBId || ''}
                          onChange={(e) => setBookBId(Number(e.target.value) || null)}
                          className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="">책을 선택하세요</option>
                          {books.map((book) => (
                            <option key={book.id} value={book.id}>
                              {book.title} - {book.author}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  )}

                  {/* 오류 메시지 */}
                  {error && (
                    <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
                      ⚠️ {error}
                    </div>
                  )}

                  {/* Mix 버튼 */}
                  <button
                    onClick={handleMix}
                    disabled={loading || (mode === 'manual' && (!bookAId || !bookBId))}
                    className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <span className="flex items-center justify-center gap-2">
                        <motion.span
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="inline-block"
                        >
                          🔄
                        </motion.span>
                        AI가 연결점을 찾고 있습니다...
                      </span>
                    ) : (
                      '🔗 아이디어 Mix 실행'
                    )}
                  </button>
                </>
              )}

              {/* 결과 표시 */}
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* 연결된 두 책 */}
                  <div className="flex items-center gap-4">
                    <div className="flex-1 p-4 bg-slate-800 rounded-xl border border-slate-600">
                      <div className="text-sm text-purple-400 mb-1">📖 책 A</div>
                      <div className="text-white font-bold">{result.book_a.title}</div>
                      <div className="text-sm text-gray-400">{result.book_a.author}</div>
                    </div>
                    <div className="text-3xl">🔗</div>
                    <div className="flex-1 p-4 bg-slate-800 rounded-xl border border-slate-600">
                      <div className="text-sm text-pink-400 mb-1">📖 책 B</div>
                      <div className="text-white font-bold">{result.book_b.title}</div>
                      <div className="text-sm text-gray-400">{result.book_b.author}</div>
                    </div>
                  </div>

                  {/* AI 인사이트 */}
                  <div className="p-6 bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500/50">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      💡 발견된 인사이트
                    </h3>

                    <div className="space-y-4">
                      <div>
                        <div className="text-sm text-purple-300 mb-1">🔗 연결점</div>
                        <div className="text-white">{result.idea.connection_point}</div>
                      </div>

                      <div>
                        <div className="text-sm text-purple-300 mb-1">💡 새로운 아이디어</div>
                        <div className="text-white font-medium">{result.idea.new_idea}</div>
                      </div>

                      <div>
                        <div className="text-sm text-purple-300 mb-1">🤔 왜 이게 의미있나?</div>
                        <div className="text-gray-300 text-sm">{result.idea.why_it_works}</div>
                      </div>

                      {result.idea.example && (
                        <div>
                          <div className="text-sm text-purple-300 mb-1">📌 예시</div>
                          <div className="text-gray-300 text-sm italic">{result.idea.example}</div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 포인트 탕감 표시 */}
                  <div className="p-4 bg-green-900/30 border border-green-500/50 rounded-xl text-center">
                    <div className="text-2xl font-bold text-green-400">
                      {result.total_reduction}pt 탕감 완료!
                    </div>
                    <div className="text-sm text-green-300 mt-1">
                      각 책에서 -40pt씩 차감되었습니다
                    </div>
                  </div>

                  {/* 다시 시도 버튼 */}
                  <div className="flex gap-4">
                    <button
                      onClick={() => setResult(null)}
                      className="flex-1 py-3 bg-slate-700 text-white font-bold rounded-lg hover:bg-slate-600 transition-all"
                    >
                      🔄 다시 Mix하기
                    </button>
                    <button
                      onClick={onClose}
                      className="flex-1 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-lg hover:shadow-lg hover:shadow-green-500/30 transition-all"
                    >
                      ✅ 완료
                    </button>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

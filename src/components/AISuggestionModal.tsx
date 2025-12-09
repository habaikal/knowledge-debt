import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

interface ActionSuggestion {
  action: string;
  duration: string;
  difficulty: string;
  activity_type: string;
  estimated_points: number;
}

interface AISuggestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  bookId: number;
  bookTitle: string;
  highlight: {
    id: number;
    text: string;
  };
  onActionSelected: () => void;
}

export function AISuggestionModal({
  isOpen,
  onClose,
  bookId,
  bookTitle,
  highlight,
  onActionSelected,
}: AISuggestionModalProps) {
  const [suggestions, setSuggestions] = useState<ActionSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userContext, setUserContext] = useState('');
  const [executing, setExecuting] = useState<number | null>(null);

  // AI 제안 요청
  const fetchSuggestions = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/ai/suggest-actions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: bookId,
          highlight_id: highlight.id,
          user_context: userContext || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '제안 생성에 실패했습니다');
      }

      const data = await response.json();
      setSuggestions(data.suggestions);
    } catch (err: any) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 제안 실행 (활동 기록)
  const executeAction = async (suggestion: ActionSuggestion, index: number) => {
    setExecuting(index);

    try {
      const response = await fetch('http://localhost:8000/ai/execute-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: bookId,
          suggestion: {
            action: suggestion.action,
            duration: suggestion.duration,
            difficulty: suggestion.difficulty,
            activity_type: suggestion.activity_type,
            estimated_points: suggestion.estimated_points,
          },
          content: suggestion.action,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '활동 기록에 실패했습니다');
      }

      const data = await response.json();

      toast.success(
        <div className="flex flex-col gap-1">
          <div className="font-bold">🎉 활동이 기록되었습니다!</div>
          <div className="text-green-600 font-semibold">-{data.points_reduced}pt 탕감</div>
        </div>,
        { duration: 3000 }
      );

      onActionSelected();
      onClose();
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setExecuting(null);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '쉬움':
        return 'text-green-400';
      case '보통':
        return 'text-yellow-400';
      case '어려움':
        return 'text-red-400';
      default:
        return 'text-gray-400';
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
            className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-slate-900 rounded-2xl shadow-2xl border border-slate-700"
          >
            {/* 헤더 */}
            <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 z-10">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                    💡 AI 행동 제안
                  </h2>
                  <p className="text-sm text-gray-400 mb-2">📖 {bookTitle}</p>
                  <p className="text-sm text-purple-300 italic">"{highlight.text}"</p>
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
              {/* 사용자 컨텍스트 입력 */}
              {suggestions.length === 0 && (
                <div>
                  <label className="block text-sm font-medium text-purple-200 mb-2">
                    나의 상황 (선택)
                  </label>
                  <input
                    type="text"
                    value={userContext}
                    onChange={(e) => setUserContext(e.target.value)}
                    placeholder="예: 소프트웨어 엔지니어, 스타트업 재직"
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                  <p className="text-xs text-gray-400 mt-2">
                    당신의 직업이나 상황을 입력하면 더 개인화된 제안을 받을 수 있습니다.
                  </p>
                </div>
              )}

              {/* AI 제안 요청 버튼 */}
              {suggestions.length === 0 && (
                <button
                  onClick={fetchSuggestions}
                  disabled={loading}
                  className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-lg shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? '🤔 AI가 생각 중...' : '✨ AI 제안 받기'}
                </button>
              )}

              {/* 오류 메시지 */}
              {error && (
                <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
                  ⚠️ {error}
                </div>
              )}

              {/* 제안 목록 */}
              {suggestions.length > 0 && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white">💡 제안된 행동</h3>
                    <button
                      onClick={() => {
                        setSuggestions([]);
                        setUserContext('');
                      }}
                      className="text-sm text-purple-400 hover:text-purple-300"
                    >
                      🔄 다시 생성
                    </button>
                  </div>

                  {suggestions.map((suggestion, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-5 bg-slate-800 border border-slate-600 rounded-lg hover:border-purple-500 transition-all"
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1">
                          <p className="text-white font-medium mb-2">{suggestion.action}</p>
                          <div className="flex flex-wrap gap-3 text-sm">
                            <span className="flex items-center gap-1 text-gray-400">
                              ⏱️ {suggestion.duration}
                            </span>
                            <span className={`flex items-center gap-1 ${getDifficultyColor(suggestion.difficulty)}`}>
                              📊 {suggestion.difficulty}
                            </span>
                            <span className="flex items-center gap-1 text-green-400">
                              🎯 -{suggestion.estimated_points}pt
                            </span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => executeAction(suggestion, index)}
                        disabled={executing !== null}
                        className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-lg hover:shadow-lg hover:shadow-green-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {executing === index ? '⏳ 기록 중...' : '✅ 이 행동 실천하기'}
                      </button>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}


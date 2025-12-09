import { useState, useEffect, FormEvent } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { ACTIVITY_TYPES } from '../constants/activities';
import { AISuggestionModal } from './AISuggestionModal';

interface ActivityFormData {
  bookId: number;
  activityType: string;
  content: string;
}

interface ActivityFormProps {
  books: Array<{ id: number; title: string }>;
  onSubmit: (activity: ActivityFormData) => void;
}

export function ActivityForm({ books, onSubmit }: ActivityFormProps) {
  const [formData, setFormData] = useState<ActivityFormData>({
    bookId: 0,
    activityType: '',
    content: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof ActivityFormData, string>>>({});
  const [highlights, setHighlights] = useState<any[]>([]);
  const [selectedHighlight, setSelectedHighlight] = useState<any>(null);
  const [showAIModal, setShowAIModal] = useState(false);
  const [loadingHighlights, setLoadingHighlights] = useState(false);

  // 책 선택 시 해당 책의 하이라이트 불러오기
  useEffect(() => {
    if (formData.bookId && formData.bookId !== 0) {
      fetchHighlights(formData.bookId);
    } else {
      setHighlights([]);
    }
  }, [formData.bookId]);

  const fetchHighlights = async (bookId: number) => {
    setLoadingHighlights(true);
    try {
      const response = await fetch(`http://localhost:8000/highlights/${bookId}`);
      if (response.ok) {
        const data = await response.json();
        setHighlights(data);
      }
    } catch (error) {
      console.error('하이라이트 조회 실패:', error);
    } finally {
      setLoadingHighlights(false);
    }
  };

  const openAISuggestion = (highlight: any) => {
    setSelectedHighlight(highlight);
    setShowAIModal(true);
  };

  // 유효성 검사
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof ActivityFormData, string>> = {};

    if (!formData.bookId || formData.bookId === 0) {
      newErrors.bookId = '책을 선택해주세요';
    }

    if (!formData.activityType) {
      newErrors.activityType = '활동 유형을 선택해주세요';
    }

    if (!formData.content.trim()) {
      newErrors.content = '활동 내용을 입력해주세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      toast.error('입력 내용을 확인해주세요', {
        icon: '⚠️',
      });
      return;
    }

    const activity = ACTIVITY_TYPES.find((a) => a.type === formData.activityType);
    const reductionPoints = activity?.points || 0;
    const selectedBook = books.find((b) => b.id === formData.bookId);

    // 성공 토스트 (애니메이션 포함)
    const IconComponent = activity?.icon;
    toast.success(
      (t) => (
        <div className="flex flex-col gap-1">
          <div className="font-bold text-lg">탕감 완료!</div>
          <div className="text-green-600 font-semibold text-2xl">-{reductionPoints}pt</div>
          <div className="text-sm text-gray-600 flex items-center gap-1">
            {IconComponent && <IconComponent size={16} />}
            {activity?.label}
          </div>
          <div className="text-xs text-gray-500">{selectedBook?.title}</div>
        </div>
      ),
      {
        duration: 4000,
        style: {
          background: '#f0fdf4',
          border: '2px solid #22c55e',
        },
      }
    );

    onSubmit(formData);

    // 폼 초기화
    setFormData({
      bookId: 0,
      activityType: '',
      content: '',
    });
    setErrors({});
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20"
    >
      <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
        ✨ 활동 기록하기
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 책 선택 */}
        <div>
          <label htmlFor="bookId" className="block text-sm font-medium text-purple-200 mb-2">
            책 선택 *
          </label>
          <select
            id="bookId"
            value={formData.bookId}
            onChange={(e) => setFormData({ ...formData, bookId: Number(e.target.value) })}
            className={`w-full px-4 py-3 bg-white/5 border ${
              errors.bookId ? 'border-red-500' : 'border-white/20'
            } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all cursor-pointer`}
          >
            <option value="0" className="bg-gray-800">
              책을 선택하세요
            </option>
            {books.map((book) => (
              <option key={book.id} value={book.id} className="bg-gray-800">
                {book.title}
              </option>
            ))}
          </select>
          {errors.bookId && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-400 text-sm mt-1"
            >
              {errors.bookId}
            </motion.p>
          )}
        </div>

        {/* 활동 유형 선택 (아이콘 버튼들) */}
        <div>
          <label className="block text-sm font-medium text-purple-200 mb-3">
            활동 유형 * {formData.activityType && (
              <span className="text-green-400 ml-2">
                (-{ACTIVITY_TYPES.find(a => a.type === formData.activityType)?.points}pt)
              </span>
            )}
          </label>
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {ACTIVITY_TYPES.map((activity) => {
              const IconComponent = activity.icon;
              return (
                <motion.button
                  key={activity.type}
                  type="button"
                  onClick={() => setFormData({ ...formData, activityType: activity.type })}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`flex flex-col items-center justify-center p-3 rounded-lg border-2 transition-all ${
                    formData.activityType === activity.type
                      ? 'border-green-400 shadow-lg shadow-green-500/20'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                  style={{
                    backgroundColor: formData.activityType === activity.type ? '#22c55e40' : '#1e293b',
                  }}
                >
                  <IconComponent 
                    size={32} 
                    className="mb-1"
                    style={{
                      color: formData.activityType === activity.type ? '#86efac' : '#a78bfa',
                    }}
                  />
                  <span style={{
                    color: formData.activityType === activity.type ? '#bbf7d0' : '#ffffff',
                    fontSize: '0.75rem',
                    fontWeight: 'bold'
                  }}>
                    {activity.label}
                  </span>
                  <span style={{
                    color: formData.activityType === activity.type ? '#86efac' : '#c084fc',
                    fontSize: '0.75rem',
                    fontWeight: '600'
                  }}>
                    -{activity.points}pt
                  </span>
                </motion.button>
              );
            })}
          </div>
          {errors.activityType && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-400 text-sm mt-2"
            >
              {errors.activityType}
            </motion.p>
          )}
        </div>

        {/* 활동 내용 */}
        <div>
          <label htmlFor="content" className="block text-sm font-medium text-purple-200 mb-2">
            활동 내용 *
          </label>
          <textarea
            id="content"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            rows={4}
            className={`w-full px-4 py-3 bg-white/5 border ${
              errors.content ? 'border-red-500' : 'border-white/20'
            } rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all resize-none`}
            placeholder="활동 내용을 자세히 적어주세요..."
          />
          {errors.content && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-400 text-sm mt-1"
            >
              {errors.content}
            </motion.p>
          )}
        </div>

        {/* AI 제안 섹션 */}
        {formData.bookId !== 0 && highlights.length > 0 && (
          <div className="p-5 bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-xl border border-purple-500/30">
            <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              💡 AI 행동 제안받기
            </h3>
            <p className="text-sm text-purple-200 mb-4">
              이 책의 하이라이트를 선택하면 AI가 구체적인 행동을 제안해드립니다
            </p>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {highlights.map((highlight) => (
                <button
                  key={highlight.id}
                  type="button"
                  onClick={() => openAISuggestion(highlight)}
                  className="w-full text-left p-3 rounded-lg transition-all group"
                  style={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#334155';
                    e.currentTarget.style.borderColor = '#a855f7';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#1e293b';
                    e.currentTarget.style.borderColor = '#475569';
                  }}
                >
                  <p className="text-sm text-white italic line-clamp-2">
                    "{highlight.original_text}"
                  </p>
                  {highlight.page_number && (
                    <span className="text-xs text-purple-200 mt-1 inline-block">
                      p.{highlight.page_number}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {formData.bookId !== 0 && highlights.length === 0 && !loadingHighlights && (
          <div className="p-5 bg-slate-800/50 rounded-xl border border-slate-600 text-center">
            <p className="text-gray-400 text-sm">
              📝 이 책에는 아직 하이라이트가 없습니다
            </p>
            <p className="text-gray-500 text-xs mt-1">
              하이라이트를 추가하면 AI 제안을 받을 수 있습니다
            </p>
          </div>
        )}

        {/* 제출 버튼 */}
        <motion.button
          type="submit"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-lg shadow-lg hover:shadow-green-500/50 transition-all"
        >
          ✨ 활동 기록하기
        </motion.button>
      </form>

      {/* AI 제안 모달 */}
      {selectedHighlight && (
        <AISuggestionModal
          isOpen={showAIModal}
          onClose={() => {
            setShowAIModal(false);
            setSelectedHighlight(null);
          }}
          bookId={formData.bookId}
          bookTitle={books.find(b => b.id === formData.bookId)?.title || ''}
          highlight={{
            id: selectedHighlight.id,
            text: selectedHighlight.original_text,
          }}
          onActionSelected={() => {
            setShowAIModal(false);
            setSelectedHighlight(null);
            toast.success('활동이 자동으로 기록되었습니다!');
          }}
        />
      )}
    </motion.div>
  );
}


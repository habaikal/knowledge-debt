import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Pencil,
  X,
  Trash2,
  BookOpen,
  Highlighter,
  Plus,
  Lightbulb,
  FileText,
  BookMarked,
  Link2,
  PenTool,
  Target,
  CheckCircle2,
  Bot,
  Check,
  Circle,
  MessageCircle
} from 'lucide-react';
import { AISuggestionModal } from './AISuggestionModal';

interface Highlight {
  id: number;
  book_id: number;
  original_text: string;
  page_number: number | null;
  my_thoughts: string | null;
  created_at: string;
}

interface Activity {
  id: number;
  book_id: number;
  activity_type: string;
  reduction_points: number;
  content: string | null;
  activity_date: string;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
}

interface BookDetailProps {
  book: {
    id: number;
    title: string;
    author: string;
    genre?: string;
    pageCount?: number;
    purchaseDate?: string;
    coverImageUrl?: string;
    initialDebt: number;
    currentDebt: number;
    status: 'debt' | 'partial' | 'asset';
    progressPercentage: number;
    totalActivities?: number;
    totalHighlights?: number;
    accumulatedMileage?: number;
  };
  onBack: () => void;
}

export function BookDetail({ book, onBack }: BookDetailProps) {
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loadingHighlights, setLoadingHighlights] = useState(false);
  const [loadingActivities, setLoadingActivities] = useState(false);
  const [selectedHighlight, setSelectedHighlight] = useState<Highlight | null>(null);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showAddHighlight, setShowAddHighlight] = useState(false);
  const [newHighlight, setNewHighlight] = useState({
    text: '',
    page: '',
    thought: '',
  });
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    title: book.title,
    author: book.author,
    genre: book.genre || '',
    coverImageUrl: book.coverImageUrl || '',
  });
  const [isSaving, setIsSaving] = useState(false);

  // 하이라이트 목록 조회
  const fetchHighlights = async () => {
    setLoadingHighlights(true);
    try {
      const response = await fetch(`http://localhost:8000/highlights/${book.id}`);
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

  // 활동 이력 조회
  const fetchActivities = async () => {
    setLoadingActivities(true);
    try {
      const response = await fetch(`http://localhost:8000/activities/${book.id}`);
      if (response.ok) {
        const data = await response.json();
        setActivities(data);
      }
    } catch (error) {
      console.error('활동 이력 조회 실패:', error);
    } finally {
      setLoadingActivities(false);
    }
  };

  useEffect(() => {
    fetchHighlights();
    fetchActivities();
  }, [book.id]);

  // 활동 완료 상태 토글
  const handleActivityCompletion = async (activityId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`http://localhost:8000/activities/${activityId}/complete`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_completed: !currentStatus }),
      });

      if (response.ok) {
        fetchActivities(); // 목록 갱신
      }
    } catch (error) {
      console.error('활동 완료 상태 업데이트 실패:', error);
    }
  };

  const openAISuggestion = (highlight: Highlight) => {
    setSelectedHighlight(highlight);
    setShowAIModal(true);
  };

  // 책 정보 수정
  const handleUpdateBook = async () => {
    setIsSaving(true);
    try {
      // 변경된 필드만 전송 (빈 문자열은 제외)
      const updatePayload: Record<string, string> = {};

      if (editData.title && editData.title.trim()) {
        updatePayload.title = editData.title.trim();
      }
      if (editData.author && editData.author.trim()) {
        updatePayload.author = editData.author.trim();
      }
      if (editData.genre && editData.genre.trim()) {
        updatePayload.genre = editData.genre.trim();
      }
      if (editData.coverImageUrl && editData.coverImageUrl.trim()) {
        updatePayload.cover_image_url = editData.coverImageUrl.trim();
      }

      // 변경된 내용이 없으면 종료
      if (Object.keys(updatePayload).length === 0) {
        alert('변경된 내용이 없습니다');
        setIsSaving(false);
        return;
      }

      const response = await fetch(`http://localhost:8000/books/${book.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatePayload),
      });

      if (response.ok) {
        alert('책 정보가 수정되었습니다');
        setIsEditing(false);
        onBack(); // 서재로 돌아가서 갱신된 데이터 반영
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`책 정보 수정에 실패했습니다: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('책 정보 수정 실패:', error);
      alert('네트워크 오류가 발생했습니다');
    } finally {
      setIsSaving(false);
    }
  };

  const cancelEdit = () => {
    setEditData({
      title: book.title,
      author: book.author,
      genre: book.genre || '',
      coverImageUrl: book.coverImageUrl || '',
    });
    setIsEditing(false);
  };

  // 하이라이트 추가
  const handleAddHighlight = async () => {
    if (!newHighlight.text.trim()) {
      alert('하이라이트 내용을 입력해주세요');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/highlights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: book.id,
          original_text: newHighlight.text,
          page_number: newHighlight.page ? parseInt(newHighlight.page) : null,
          my_thoughts: newHighlight.thought || null,
        }),
      });

      if (response.ok) {
        setNewHighlight({ text: '', page: '', thought: '' });
        setShowAddHighlight(false);
        fetchHighlights();
        alert('✅ 하이라이트가 추가되었습니다! (-20pt 탕감)');
      } else {
        alert('하이라이트 추가에 실패했습니다');
      }
    } catch (error) {
      console.error('하이라이트 추가 실패:', error);
      alert('오류가 발생했습니다');
    }
  };

  // 하이라이트 삭제
  const handleDeleteHighlight = async (highlightId: number) => {
    if (!confirm('이 하이라이트를 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`http://localhost:8000/highlights/${highlightId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchHighlights();
        alert('✅ 하이라이트가 삭제되었습니다');
      } else {
        alert('하이라이트 삭제에 실패했습니다');
      }
    } catch (error) {
      console.error('하이라이트 삭제 실패:', error);
      alert('오류가 발생했습니다');
    }
  };
  const getStatusConfig = () => {
    switch (book.status) {
      case 'asset':
        return {
          badge: '🟢 자산',
          color: 'text-green-400',
          bgColor: 'from-green-500/20 to-emerald-500/20',
        };
      case 'partial':
        return {
          badge: '🟡 상환중',
          color: 'text-yellow-400',
          bgColor: 'from-yellow-500/20 to-orange-500/20',
        };
      default:
        return {
          badge: '🔴 부채',
          color: 'text-red-400',
          bgColor: 'from-red-500/20 to-pink-500/20',
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* 상단 버튼 */}
      <div className="flex justify-between items-center">
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all border"
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            borderColor: 'rgba(71, 85, 105, 0.5)',
            color: '#cbd5e1'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(51, 65, 85, 0.5)';
            e.currentTarget.style.color = '#ffffff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(30, 41, 59, 0.8)';
            e.currentTarget.style.color = '#cbd5e1';
          }}
        >
          <ArrowLeft size={20} />
          <span className="font-semibold">서재로 돌아가기</span>
        </button>

        <div className="flex gap-2">
          <button
            onClick={() => isEditing ? cancelEdit() : setIsEditing(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all border"
            style={{
              backgroundColor: isEditing ? 'rgba(59, 130, 246, 0.5)' : 'rgba(30, 41, 59, 0.8)',
              borderColor: isEditing ? 'rgba(96, 165, 250, 0.5)' : 'rgba(71, 85, 105, 0.5)',
              color: isEditing ? '#93c5fd' : '#cbd5e1'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.5)';
              e.currentTarget.style.color = '#ffffff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = isEditing ? 'rgba(59, 130, 246, 0.5)' : 'rgba(30, 41, 59, 0.8)';
              e.currentTarget.style.color = isEditing ? '#93c5fd' : '#cbd5e1';
            }}
          >
            {isEditing ? <X size={18} /> : <Pencil size={18} />}
            <span className="font-semibold">{isEditing ? '취소' : '수정'}</span>
          </button>

        <button
          onClick={async () => {
            if (confirm(`"${book.title}"을(를) 정말 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) {
              try {
                const response = await fetch(`http://localhost:8000/books/${book.id}`, {
                  method: 'DELETE',
                });
                
                if (response.ok) {
                  const data = await response.json();
                  alert(data.message);
                  onBack();
                } else {
                  alert('책 삭제에 실패했습니다.');
                }
              } catch (error) {
                console.error('삭제 오류:', error);
                alert('삭제 중 오류가 발생했습니다.');
              }
            }
          }}
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all border"
          style={{
            backgroundColor: 'rgba(127, 29, 29, 0.5)',
            borderColor: 'rgba(185, 28, 28, 0.5)',
            color: '#fca5a5'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(153, 27, 27, 0.5)';
            e.currentTarget.style.color = '#ffffff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(127, 29, 29, 0.5)';
            e.currentTarget.style.color = '#fca5a5';
          }}
        >
          <Trash2 size={18} />
          <span className="font-semibold">삭제</span>
        </button>
        </div>
      </div>

      {/* 책 상세 정보 */}
      <div className={`bg-gradient-to-br ${statusConfig.bgColor} backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20`}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 왼쪽: 표지 */}
          <div className="lg:col-span-1">
            <div className="aspect-[2/3] bg-gradient-to-br from-purple-900 to-indigo-900 rounded-xl overflow-hidden shadow-2xl">
              {(isEditing ? editData.coverImageUrl : book.coverImageUrl) ? (
                <img
                  src={isEditing ? editData.coverImageUrl : book.coverImageUrl}
                  alt={book.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <span className="text-9xl">📚</span>
                </div>
              )}
            </div>
          </div>

          {/* 오른쪽: 정보 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 제목 & 상태 */}
            <div>
              <div className="flex items-start justify-between mb-2">
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.title}
                    onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                    className="text-3xl font-bold text-white bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 flex-1 mr-4"
                    placeholder="책 제목"
                  />
                ) : (
                  <h1 className="text-4xl font-bold text-white">{book.title}</h1>
                )}
                <span className={`px-4 py-2 bg-black/30 rounded-full text-sm font-bold ${statusConfig.color}`}>
                  {statusConfig.badge}
                </span>
              </div>
              {isEditing ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editData.author}
                    onChange={(e) => setEditData({ ...editData, author: e.target.value })}
                    className="text-lg text-purple-200 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 w-full"
                    placeholder="저자"
                  />
                  <input
                    type="text"
                    value={editData.genre}
                    onChange={(e) => setEditData({ ...editData, genre: e.target.value })}
                    className="text-sm text-gray-300 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 w-full"
                    placeholder="장르"
                  />
                  <div>
                    <label className="block text-xs text-purple-200 mb-1">표지 이미지 URL</label>
                    <input
                      type="url"
                      value={editData.coverImageUrl}
                      onChange={(e) => setEditData({ ...editData, coverImageUrl: e.target.value })}
                      className="text-sm text-gray-300 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 w-full"
                      placeholder="https://example.com/cover.jpg"
                    />
                  </div>
                  <button
                    onClick={handleUpdateBook}
                    disabled={isSaving}
                    className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
                  >
                    {isSaving ? '저장 중...' : '변경사항 저장'}
                  </button>
                </div>
              ) : (
                <>
                  <p className="text-xl text-purple-200">{book.author}</p>
                  {book.genre && (
                    <p className="text-sm text-gray-400 mt-2">장르: {book.genre}</p>
                  )}
                </>
              )}
            </div>

            {/* 통계 그리드 */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">초기 부채</p>
                <p className="text-2xl font-bold text-white">{Math.round(book.initialDebt)}pt</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">남은 부채</p>
                <p className="text-2xl font-bold text-red-400">{Math.round(book.currentDebt)}pt</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">진행률</p>
                <p className="text-2xl font-bold text-green-400">{Math.round(book.progressPercentage || 0)}%</p>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">마일리지</p>
                <p className="text-2xl font-bold text-yellow-400">{book.accumulatedMileage || 0}pt</p>
              </div>
            </div>

            {/* 진행률 바 */}
            <div>
              <div className="flex justify-between text-sm text-gray-300 mb-2">
                <span>전체 진행률</span>
                <span className="font-bold">{(book.progressPercentage || 0).toFixed(1)}%</span>
              </div>
              <div className="h-4 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${book.progressPercentage || 0}%` }}
                  transition={{ duration: 1.5, ease: 'easeOut' }}
                  className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-red-500"
                />
              </div>
            </div>

            {/* 활동 요약 */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="flex justify-center mb-2">
                  <FileText size={32} className="text-purple-400" />
                </div>
                <p className="text-2xl font-bold text-white">{book.totalActivities || 0}</p>
                <p className="text-xs text-gray-400">총 활동</p>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="flex justify-center mb-2">
                  <Highlighter size={32} className="text-yellow-400" />
                </div>
                <p className="text-2xl font-bold text-white">{book.totalHighlights || 0}</p>
                <p className="text-xs text-gray-400">하이라이트</p>
              </div>
              <div className="text-center p-4 bg-white/5 rounded-lg">
                <div className="flex justify-center mb-2">
                  <BookOpen size={32} className="text-blue-400" />
                </div>
                <p className="text-2xl font-bold text-white">{book.pageCount || 0}</p>
                <p className="text-xs text-gray-400">페이지</p>
              </div>
            </div>

            {/* 추가 정보 */}
            {book.purchaseDate && (
              <div className="text-sm text-gray-400">
                구매일: {new Date(book.purchaseDate).toLocaleDateString('ko-KR')}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 하이라이트 목록 */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Highlighter size={24} className="text-yellow-400" />
            하이라이트
          </h2>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">
              {highlights.length}개
            </span>
            <button
              onClick={() => setShowAddHighlight(!showAddHighlight)}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all text-sm"
            >
              {showAddHighlight ? (
                <span className="flex items-center gap-1"><X size={14} /> 취소</span>
              ) : (
                <span className="flex items-center gap-1"><Plus size={14} /> 하이라이트 추가</span>
              )}
            </button>
          </div>
        </div>

        {/* 하이라이트 추가 폼 */}
        {showAddHighlight && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6 p-6 bg-slate-800/80 rounded-xl border border-purple-500/30"
          >
            <h3 className="text-lg font-bold text-white mb-4">새 하이라이트 추가</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-purple-200 mb-2">하이라이트 내용 *</label>
                <textarea
                  value={newHighlight.text}
                  onChange={(e) => setNewHighlight({ ...newHighlight, text: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="책에서 인상 깊었던 문장을 입력하세요..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-purple-200 mb-2">페이지 (선택)</label>
                  <input
                    type="number"
                    value={newHighlight.page}
                    onChange={(e) => setNewHighlight({ ...newHighlight, page: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="42"
                  />
                </div>
                <div>
                  <label className="block text-sm text-purple-200 mb-2">나의 생각 (선택)</label>
                  <input
                    type="text"
                    value={newHighlight.thought}
                    onChange={(e) => setNewHighlight({ ...newHighlight, thought: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    placeholder="내 생각..."
                  />
                </div>
              </div>
              <button
                onClick={handleAddHighlight}
                className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-lg hover:shadow-lg transition-all"
              >
                <span className="flex items-center justify-center gap-2">
                  <Check size={18} /> 추가하기 (-20pt 탕감)
                </span>
              </button>
            </div>
          </motion.div>
        )}

        {loadingHighlights ? (
          <div className="text-center py-8 text-gray-400">
            로딩 중...
          </div>
        ) : highlights.length === 0 ? (
          <div className="text-center py-12">
            <div className="flex justify-center mb-4">
              <FileText size={64} className="text-purple-400" />
            </div>
            <p className="text-gray-400">아직 하이라이트가 없습니다</p>
            <p className="text-sm text-gray-500 mt-2">
              책을 읽으면서 중요한 문장을 하이라이트해보세요
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {highlights.map((highlight, index) => (
              <motion.div
                key={highlight.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-5 bg-slate-800/80 border border-slate-600 rounded-lg hover:border-purple-500 transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <blockquote className="text-white italic border-l-4 border-purple-400 pl-4 flex-1">
                        "{highlight.original_text}"
                      </blockquote>
                      {highlight.page_number && (
                        <span className="text-xs text-gray-400 whitespace-nowrap">
                          p.{highlight.page_number}
                        </span>
                      )}
                    </div>

                    {highlight.my_thoughts && (
                      <div className="mt-3 p-3 bg-slate-700/50 rounded-lg">
                        <p className="text-sm text-gray-300 flex items-start gap-2">
                          <MessageCircle size={16} className="flex-shrink-0 mt-0.5 text-purple-300" />
                          {highlight.my_thoughts}
                        </p>
                      </div>
                    )}

                    <div className="mt-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => openAISuggestion(highlight)}
                          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-purple-500/30 transition-all text-sm"
                        >
                          <Lightbulb size={16} />
                          <span>AI 행동 제안받기</span>
                        </button>
                        <span className="text-xs text-gray-400">
                          {new Date(highlight.created_at).toLocaleDateString('ko-KR')}
                        </span>
                      </div>
                      <button
                        onClick={() => handleDeleteHighlight(highlight.id)}
                        className="px-3 py-2 rounded-lg transition-all text-sm border"
                        style={{
                          backgroundColor: 'rgba(127, 29, 29, 0.5)',
                          borderColor: 'rgba(185, 28, 28, 0.5)',
                          color: '#fca5a5'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = 'rgba(153, 27, 27, 0.5)';
                          e.currentTarget.style.color = '#ffffff';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'rgba(127, 29, 29, 0.5)';
                          e.currentTarget.style.color = '#fca5a5';
                        }}
                      >
                        <span className="flex items-center gap-1"><Trash2 size={14} /> 삭제</span>
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* 활동 이력 */}
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText size={24} className="text-purple-400" />
            활동 이력
          </h2>
          <span className="text-sm text-gray-400">
            {activities.length}개
          </span>
        </div>

        {loadingActivities ? (
          <div className="text-center py-8 text-gray-400">
            로딩 중...
          </div>
        ) : activities.length === 0 ? (
          <div className="text-center py-12">
            <div className="flex justify-center mb-4">
              <FileText size={64} className="text-purple-400" />
            </div>
            <p className="text-gray-400">아직 활동 이력이 없습니다</p>
            <p className="text-sm text-gray-500 mt-2">
              하이라이트를 추가하거나 AI 제안 행동을 실천해보세요
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {activities.map((activity, index) => {
              const isAISuggestion = activity.content?.startsWith('[AI 제안]');
              return (
                <motion.div
                  key={activity.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className={`p-4 rounded-lg border ${
                    isAISuggestion
                      ? activity.is_completed
                        ? 'bg-green-900/30 border-green-500/50'
                        : 'bg-purple-900/30 border-purple-500/50'
                      : 'bg-slate-800/80 border-slate-600'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    {/* AI 제안 활동에만 체크박스 표시 */}
                    {isAISuggestion && (
                      <button
                        onClick={() => handleActivityCompletion(activity.id, activity.is_completed)}
                        className="flex-shrink-0 w-7 h-7 rounded-md border-2 flex items-center justify-center transition-all"
                        style={{
                          backgroundColor: activity.is_completed ? '#22c55e' : '#334155',
                          borderColor: activity.is_completed ? '#22c55e' : '#c084fc',
                          color: '#ffffff'
                        }}
                      >
                        {activity.is_completed ? (
                          <span className="text-sm font-bold">✓</span>
                        ) : (
                          <span className="text-xs text-purple-300">○</span>
                        )}
                      </button>
                    )}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">
                          {isAISuggestion ? (activity.is_completed ? '✅' : '🤖') :
                           activity.activity_type === 'highlight' ? '✏️' :
                           activity.activity_type === 'read' ? '📖' :
                           activity.activity_type === 'connect' ? '🔗' :
                           activity.activity_type === 'writing' ? '✍️' :
                           activity.activity_type === 'action' ? '🎯' : '📝'}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          isAISuggestion
                            ? activity.is_completed
                              ? 'bg-green-600/50 text-green-200'
                              : 'bg-purple-600/50 text-purple-200'
                            : 'bg-slate-700 text-gray-300'
                        }`}>
                          {activity.activity_type}
                        </span>
                        <span className="text-green-400 font-bold text-sm">
                          {activity.reduction_points}pt
                        </span>
                        {activity.is_completed && (
                          <span className="text-xs text-green-400 font-semibold">실천 완료</span>
                        )}
                      </div>
                      {activity.content && (
                        <p className={`text-sm ${activity.is_completed ? 'text-gray-400 line-through' : 'text-gray-300'}`}>
                          {activity.content}
                        </p>
                      )}
                      {/* 완료 날짜 표시 */}
                      {activity.is_completed && activity.completed_at && (
                        <p className="text-xs text-green-400 mt-2">
                          실천일: {new Date(activity.completed_at).toLocaleDateString('ko-KR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                          })}
                        </p>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 whitespace-nowrap">
                      {new Date(activity.created_at).toLocaleDateString('ko-KR', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>

      {/* AI 제안 모달 */}
      {selectedHighlight && (
        <AISuggestionModal
          isOpen={showAIModal}
          onClose={() => {
            setShowAIModal(false);
            setSelectedHighlight(null);
          }}
          bookId={book.id}
          bookTitle={book.title}
          highlight={{
            id: selectedHighlight.id,
            text: selectedHighlight.original_text,
          }}
          onActionSelected={() => {
            // 활동이 기록되면 활동 이력 갱신 (페이지 유지)
            fetchActivities();
            setShowAIModal(false);
            setSelectedHighlight(null);
          }}
        />
      )}
    </motion.div>
  );
}


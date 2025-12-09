import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, PlusCircle, Sparkles, Library, BookMarked, Target, TrendingUp } from 'lucide-react';
import { CircularGauge } from './CircularGauge';
import { StatCard } from './StatCard';
import { ParticleEffect } from './ParticleEffect';
import { BookRegistrationForm } from './BookRegistrationForm';
import { ActivityForm } from './ActivityForm';
import { BookShelf } from './BookShelf';
import { BookDetail } from './BookDetail';
import { MixIdeasModal } from './MixIdeasModal';

interface DashboardStats {
  totalDebt: number;
  totalBooks: number;
  assetBooks: number;
  weeklyActivities: number;
}

interface Book {
  id: number;
  title: string;
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalDebt: 0,
    totalBooks: 0,
    assetBooks: 0,
    weeklyActivities: 0,
  });

  const [books, setBooks] = useState<any[]>([]);

  // API에서 가져온 책 정보를 프론트엔드 형식으로 변환
  const booksWithDebt = books.map(book => ({
    ...book,
    initialDebt: book.initial_debt_points || 0,
    currentDebt: book.current_remaining_points || 0,
    coverImageUrl: book.cover_image_url,
    pageCount: book.page_count,
    purchaseDate: book.purchase_date,
    progressPercentage: book.progress_percentage || 0,
    totalActivities: book.total_activities || 0,
    totalHighlights: book.total_highlights || 0,
    accumulatedMileage: book.accumulated_mileage || 0,
  }));

  const [showParticles, setShowParticles] = useState(false);
  const [debtChange, setDebtChange] = useState(0);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'register' | 'activity' | 'bookshelf'>('dashboard');
  const [selectedBookId, setSelectedBookId] = useState<number | null>(null);
  const [showMixModal, setShowMixModal] = useState(false);

  // API에서 책 목록 가져오기
  const fetchBooks = async () => {
    try {
      const response = await fetch('http://localhost:8000/books');
      const data = await response.json();
      setBooks(data);
    } catch (error) {
      console.error('책 목록 조회 실패:', error);
    }
  };

  // 대시보드 통계 가져오기
  const fetchDashboard = async () => {
    try {
      const response = await fetch('http://localhost:8000/dashboard');
      const data = await response.json();
      setStats({
        totalDebt: data.total_remaining_debt || 0,
        totalBooks: data.total_books || 0,
        assetBooks: data.asset_books || 0,
        weeklyActivities: 15, // TODO: 주간 활동 API 추가 필요
      });
    } catch (error) {
      console.error('대시보드 조회 실패:', error);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    fetchBooks();
    fetchDashboard();
  }, []);

  // 책 추가 핸들러 (API 연동)
  const handleAddBook = async (bookData: any) => {
    console.log('📚 책 등록 시작:', bookData);
    
    try {
      const payload = {
        title: bookData.title,
        author: bookData.author,
        genre: bookData.genre,
        purchase_date: bookData.purchaseDate,
        page_count: bookData.pageCount,
        cover_image_url: bookData.coverImageUrl || null,
      };
      
      console.log('📤 API 요청:', payload);
      
      const response = await fetch('http://localhost:8000/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      console.log('📥 API 응답 상태:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ 책 등록 성공:', result);
        
        const newDebt = 300 + bookData.pageCount * 0.5;
        setDebtChange(newDebt);

        // 데이터 갱신
        await fetchBooks();
        await fetchDashboard();

        // 애니메이션 후 리셋
        setTimeout(() => setDebtChange(0), 2000);

        // 대시보드로 전환
        setTimeout(() => setActiveTab('dashboard'), 1000);
      } else {
        const error = await response.text();
        console.error('❌ API 오류:', error);
        alert(`책 등록 실패: ${error}`);
      }
    } catch (error) {
      console.error('❌ 책 등록 실패:', error);
      alert(`네트워크 오류: ${error}`);
    }
  };

  // 활동 기록 핸들러 (API 연동)
  const handleRecordActivity = async (activityData: any) => {
    try {
      const response = await fetch('http://localhost:8000/activities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: activityData.bookId,
          activity_type: activityData.activityType,
          content: activityData.content,
        }),
      });

      if (response.ok) {
        // 파티클 효과 표시
        setShowParticles(true);
        setTimeout(() => setShowParticles(false), 1000);

        // 데이터 갱신
        await fetchBooks();
        await fetchDashboard();

        // 대시보드로 전환
        setTimeout(() => setActiveTab('dashboard'), 1000);
      }
    } catch (error) {
      console.error('활동 기록 실패:', error);
    }
  };

  // 부채 비율 계산 (0~100%)
  const maxDebt = 3000; // 최대 부채 기준
  const debtPercentage = Math.min((stats.totalDebt / maxDebt) * 100, 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-5xl font-bold text-white mb-4 flex items-center justify-center gap-4">
            <BookOpen size={48} className="text-purple-400" />
            지식 부채 관리
          </h1>
          <p className="text-xl text-purple-200">
            책을 읽고, 활동하고, 부채를 갚아나가세요
          </p>
        </motion.div>

        {/* 탭 네비게이션 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center gap-4 mb-8"
        >
          <motion.button
            onClick={() => setActiveTab('dashboard')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              backgroundColor: activeTab === 'dashboard' ? '#9333ea' : '#1e293b',
              color: '#ffffff',
            }}
            className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
              activeTab === 'dashboard'
                ? 'shadow-xl shadow-purple-500/50'
                : 'shadow-lg hover:brightness-125'
            }`}
          >
            <span className="flex items-center gap-2">
              <TrendingUp size={20} />
              대시보드
            </span>
          </motion.button>
          <motion.button
            onClick={() => setActiveTab('register')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              backgroundColor: activeTab === 'register' ? '#dc2626' : '#1e293b',
              color: '#ffffff',
            }}
            className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
              activeTab === 'register'
                ? 'shadow-xl shadow-red-500/50'
                : 'shadow-lg hover:brightness-125'
            }`}
          >
            <span className="flex items-center gap-2">
              <PlusCircle size={20} />
              책 등록
            </span>
          </motion.button>
          <motion.button
            onClick={() => setActiveTab('activity')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              backgroundColor: activeTab === 'activity' ? '#16a34a' : '#1e293b',
              color: '#ffffff',
            }}
            className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
              activeTab === 'activity'
                ? 'shadow-xl shadow-green-500/50'
                : 'shadow-lg hover:brightness-125'
            }`}
          >
            <span className="flex items-center gap-2">
              <Sparkles size={20} />
              활동 기록
            </span>
          </motion.button>
          <motion.button
            onClick={() => {
              setActiveTab('bookshelf');
              setSelectedBookId(null);
              fetchBooks(); // 서재 탭 클릭 시 데이터 새로고침
              fetchDashboard();
            }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              backgroundColor: activeTab === 'bookshelf' ? '#f59e0b' : '#1e293b',
              color: '#ffffff',
            }}
            className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
              activeTab === 'bookshelf'
                ? 'shadow-xl shadow-amber-500/50'
                : 'shadow-lg hover:brightness-125'
            }`}
          >
            <span className="flex items-center gap-2">
              <Library size={20} />
              서재
            </span>
          </motion.button>
          <motion.button
            onClick={() => setShowMixModal(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              backgroundColor: '#7c3aed',
              color: '#ffffff',
            }}
            className="px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-lg hover:brightness-125 hover:shadow-xl hover:shadow-purple-500/50"
          >
            🔗 Mix
          </motion.button>
        </motion.div>

        {/* 탭 컨텐츠 */}
        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              {/* 메인 게이지 */}
              <div className="flex justify-center mb-16 relative">
                <CircularGauge
                  value={stats.totalDebt}
                  maxValue={maxDebt}
                  percentage={debtPercentage}
                />
                
                {/* 부채 증가 애니메이션 */}
                <AnimatePresence>
                  {debtChange > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 0, scale: 0.5 }}
                      animate={{ opacity: 1, y: -100, scale: 1.5 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none"
                    >
                      <span className="text-6xl font-bold text-red-500">
                        +{debtChange}
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* 파티클 효과 */}
                {showParticles && <ParticleEffect />}
              </div>

              {/* 통계 카드들 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                  icon="📚"
                  label="총 보유 책"
                  value={stats.totalBooks}
                  suffix="권"
                  color="blue"
                />
                <StatCard
                  icon="✨"
                  label="자산화된 책"
                  value={stats.assetBooks}
                  suffix="권"
                  color="green"
                />
                <StatCard
                  icon="🎯"
                  label="이번 주 활동"
                  value={stats.weeklyActivities}
                  suffix="회"
                  color="purple"
                />
              </div>
            </motion.div>
          )}

          {activeTab === 'register' && (
            <motion.div
              key="register"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="max-w-2xl mx-auto"
            >
              <BookRegistrationForm onSubmit={handleAddBook} />
            </motion.div>
          )}

          {activeTab === 'activity' && (
            <motion.div
              key="activity"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="max-w-3xl mx-auto"
            >
              <ActivityForm books={books} onSubmit={handleRecordActivity} />
            </motion.div>
          )}

          {activeTab === 'bookshelf' && (
            <motion.div
              key="bookshelf"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              {selectedBookId ? (
                <BookDetail
                  book={booksWithDebt.find(b => b.id === selectedBookId)!}
                  onBack={() => {
                    setSelectedBookId(null);
                    fetchBooks(); // 서재로 돌아갈 때 책 목록 갱신
                    fetchDashboard(); // 통계도 갱신
                  }}
                />
              ) : (
                <BookShelf
                  books={booksWithDebt}
                  onBookClick={(id) => setSelectedBookId(id)}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Mix Ideas 모달 */}
        <MixIdeasModal
          isOpen={showMixModal}
          onClose={() => setShowMixModal(false)}
          books={books}
          onMixComplete={() => {
            fetchBooks();
            fetchDashboard();
          }}
        />
      </div>
    </div>
  );
}

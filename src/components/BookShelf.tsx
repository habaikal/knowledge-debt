import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Library, BookOpen } from 'lucide-react';
import { BookCard } from './BookCard';

interface Book {
  id: number;
  title: string;
  author: string;
  coverImageUrl?: string;
  initialDebt: number;
  currentDebt: number;
  status: 'debt' | 'partial' | 'asset';
  progressPercentage: number;
}

interface BookShelfProps {
  books: Book[];
  onBookClick: (bookId: number) => void;
}

type FilterType = 'all' | 'debt' | 'partial' | 'asset';

export function BookShelf({ books, onBookClick }: BookShelfProps) {
  const [filter, setFilter] = useState<FilterType>('all');

  // 필터링된 책 목록
  const filteredBooks = books.filter((book) => {
    if (filter === 'all') return true;
    if (filter === 'debt') return book.status === 'debt' || book.status === 'partial';
    return book.status === filter;
  });

  // 통계
  const stats = {
    total: books.length,
    debt: books.filter((b) => b.status === 'debt' || b.status === 'partial').length,
    asset: books.filter((b) => b.status === 'asset').length,
  };

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Library size={32} className="text-purple-400" />
            내 서재
          </h2>
          <p className="text-purple-200">총 {stats.total}권의 책이 있습니다</p>
        </div>

        {/* 필터 탭 */}
        <div 
          className="flex gap-2 p-1 rounded-lg border"
          style={{ 
            backgroundColor: 'rgba(30, 41, 59, 0.9)', 
            borderColor: 'rgba(71, 85, 105, 0.5)' 
          }}
        >
          <button
            onClick={() => setFilter('all')}
            className="px-4 py-2 rounded-md font-semibold transition-all shadow-lg"
            style={filter === 'all' 
              ? { backgroundColor: '#9333ea', color: '#ffffff' }
              : { backgroundColor: 'transparent', color: '#cbd5e1' }
            }
          >
            전체 ({stats.total})
          </button>
          <button
            onClick={() => setFilter('debt')}
            className="px-4 py-2 rounded-md font-semibold transition-all shadow-lg"
            style={filter === 'debt' 
              ? { backgroundColor: '#dc2626', color: '#ffffff' }
              : { backgroundColor: 'transparent', color: '#cbd5e1' }
            }
          >
            부채 ({stats.debt})
          </button>
          <button
            onClick={() => setFilter('asset')}
            className="px-4 py-2 rounded-md font-semibold transition-all shadow-lg"
            style={filter === 'asset' 
              ? { backgroundColor: '#16a34a', color: '#ffffff' }
              : { backgroundColor: 'transparent', color: '#cbd5e1' }
            }
          >
            자산 ({stats.asset})
          </button>
        </div>
      </motion.div>

      {/* 책 그리드 */}
      <AnimatePresence mode="wait">
        {filteredBooks.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center py-20"
          >
            <div className="flex justify-center mb-4">
              <BookOpen size={64} className="text-purple-400" />
            </div>
            <p className="text-xl text-gray-400">
              {filter === 'all'
                ? '아직 등록된 책이 없습니다'
                : filter === 'asset'
                ? '자산화된 책이 없습니다'
                : '부채 상태의 책이 없습니다'}
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="grid"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4"
          >
            {filteredBooks.map((book, index) => (
              <motion.div
                key={book.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <BookCard book={book} onClick={() => onBookClick(book.id)} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 하단 요약 */}
      {filteredBooks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex justify-center gap-8 pt-8 text-sm text-gray-300"
        >
          <div className="text-center">
            <div className="text-2xl font-bold text-white">
              {Math.round(filteredBooks.reduce((sum, book) => sum + book.currentDebt, 0))}pt
            </div>
            <div>총 잔여 부채</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {Math.round(filteredBooks
                .reduce((sum, book) => sum + book.progressPercentage, 0) / filteredBooks.length) || 0}%
            </div>
            <div>평균 진행률</div>
          </div>
        </motion.div>
      )}
    </div>
  );
}


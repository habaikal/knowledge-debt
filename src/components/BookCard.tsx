import { motion } from 'framer-motion';

interface BookCardProps {
  book: {
    id: number;
    title: string;
    author: string;
    coverImageUrl?: string;
    initialDebt: number;
    currentDebt: number;
    status: 'debt' | 'partial' | 'asset';
    progressPercentage: number;
  };
  onClick: () => void;
}

export function BookCard({ book, onClick }: BookCardProps) {
  const getStatusConfig = () => {
    switch (book.status) {
      case 'asset':
        return {
          badge: '🟢 자산',
          bgColor: 'from-green-500/20 to-emerald-500/20',
          borderColor: 'border-green-500/50',
          progressColor: 'bg-gradient-to-r from-green-500 to-emerald-500',
        };
      case 'partial':
        return {
          badge: '🟡 상환중',
          bgColor: 'from-yellow-500/20 to-orange-500/20',
          borderColor: 'border-yellow-500/50',
          progressColor: 'bg-gradient-to-r from-yellow-500 to-orange-500',
        };
      default:
        return {
          badge: '🔴 부채',
          bgColor: 'from-red-500/20 to-pink-500/20',
          borderColor: 'border-red-500/50',
          progressColor: 'bg-gradient-to-r from-red-500 to-pink-500',
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="cursor-pointer"
    >
      <div className={`relative bg-gradient-to-br ${statusConfig.bgColor} backdrop-blur-lg rounded-xl p-3 border ${statusConfig.borderColor} shadow-lg hover:shadow-xl transition-all`}>
        {/* 상태 뱃지 */}
        <div className="absolute top-2 right-2 px-2 py-0.5 bg-black/50 backdrop-blur-md rounded-full text-xs font-bold">
          {statusConfig.badge}
        </div>

        {/* 책 표지 - 크기 축소 */}
        <div className="mb-2 aspect-[3/4] bg-gradient-to-br from-purple-900 to-indigo-900 rounded-lg overflow-hidden shadow-md">
          {book.coverImageUrl ? (
            <img
              src={book.coverImageUrl}
              alt={book.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-4xl">📚</span>
            </div>
          )}
        </div>

        {/* 책 정보 - 컴팩트하게 */}
        <div className="space-y-1">
          <h3 className="text-sm font-bold text-white line-clamp-2 min-h-[2.5rem]">
            {book.title}
          </h3>
          <p className="text-xs text-purple-200 truncate">{book.author}</p>

          {/* 진행률 바 */}
          <div className="pt-1">
            <div className="flex justify-between text-[10px] text-gray-300 mb-0.5">
              <span>진행률</span>
              <span className="font-bold">{Math.round(book.progressPercentage || 0)}%</span>
            </div>
            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${book.progressPercentage || 0}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className={`h-full ${statusConfig.progressColor}`}
              />
            </div>
          </div>

          {/* 부채 정보 - 컴팩트하게 */}
          <div className="pt-1 flex justify-between items-center">
            <div>
              <p className="text-[10px] text-gray-400">남은 부채</p>
              <p className="text-base font-bold text-white">{Math.round(book.currentDebt)}pt</p>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-gray-400">초기</p>
              <p className="text-xs text-gray-300">{Math.round(book.initialDebt)}pt</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}


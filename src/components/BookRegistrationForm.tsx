import { useState, FormEvent } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

interface BookFormData {
  title: string;
  author: string;
  genre: string;
  purchaseDate: string;
  pageCount: number;
  coverImageUrl: string;
}

interface BookRegistrationFormProps {
  onSubmit: (book: BookFormData) => void;
}

const GENRES = [
  '자기계발',
  '소설',
  '에세이',
  '시',
  '경영/경제',
  '인문',
  '역사',
  '과학',
  '기술/컴퓨터',
  '예술',
  '종교',
  '여행',
  '건강',
  '요리',
  '기타',
];

export function BookRegistrationForm({ onSubmit }: BookRegistrationFormProps) {
  const [formData, setFormData] = useState<BookFormData>({
    title: '',
    author: '',
    genre: '',
    purchaseDate: new Date().toISOString().split('T')[0],
    pageCount: 300,
    coverImageUrl: '',
  });

  const [errors, setErrors] = useState<Partial<Record<keyof BookFormData, string>>>({});

  // 유효성 검사
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof BookFormData, string>> = {};

    if (!formData.title.trim()) {
      newErrors.title = '제목을 입력해주세요';
    }

    if (!formData.author.trim()) {
      newErrors.author = '저자를 입력해주세요';
    }

    if (!formData.genre) {
      newErrors.genre = '장르를 선택해주세요';
    }

    if (!formData.purchaseDate) {
      newErrors.purchaseDate = '구매일을 선택해주세요';
    }

    if (formData.pageCount <= 0) {
      newErrors.pageCount = '페이지 수는 1 이상이어야 합니다';
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

    // 부채 계산
    const debtPoints = 300 + formData.pageCount * 0.5;

    // 성공 토스트
    toast.success(
      (t) => (
        <div className="flex flex-col gap-1">
          <div className="font-bold text-lg">📚 새로운 부채가 등록되었습니다</div>
          <div className="text-red-600 font-semibold">+{debtPoints}pt</div>
          <div className="text-sm text-gray-600">{formData.title}</div>
        </div>
      ),
      {
        duration: 4000,
        style: {
          background: '#fef2f2',
          border: '2px solid #ef4444',
        },
      }
    );

    onSubmit(formData);

    // 폼 초기화
    setFormData({
      title: '',
      author: '',
      genre: '',
      purchaseDate: new Date().toISOString().split('T')[0],
      pageCount: 300,
      coverImageUrl: '',
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
        📖 책 등록하기
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 제목 */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-purple-200 mb-2">
            제목 *
          </label>
          <input
            id="title"
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className={`w-full px-4 py-3 bg-white/5 border ${
              errors.title ? 'border-red-500' : 'border-white/20'
            } rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all`}
            placeholder="예: 클린 코드"
          />
          {errors.title && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-400 text-sm mt-1"
            >
              {errors.title}
            </motion.p>
          )}
        </div>

        {/* 저자 */}
        <div>
          <label htmlFor="author" className="block text-sm font-medium text-purple-200 mb-2">
            저자 *
          </label>
          <input
            id="author"
            type="text"
            value={formData.author}
            onChange={(e) => setFormData({ ...formData, author: e.target.value })}
            className={`w-full px-4 py-3 bg-white/5 border ${
              errors.author ? 'border-red-500' : 'border-white/20'
            } rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all`}
            placeholder="예: 로버트 C. 마틴"
          />
          {errors.author && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-red-400 text-sm mt-1"
            >
              {errors.author}
            </motion.p>
          )}
        </div>

        {/* 책표지 이미지 URL */}
        <div>
          <label htmlFor="coverImageUrl" className="block text-sm font-medium text-purple-200 mb-2">
            책표지 이미지 URL (선택)
          </label>
          <div className="flex gap-4">
            <input
              id="coverImageUrl"
              type="url"
              value={formData.coverImageUrl}
              onChange={(e) => setFormData({ ...formData, coverImageUrl: e.target.value })}
              className="flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
              placeholder="https://example.com/book-cover.jpg"
            />
            {formData.coverImageUrl && (
              <div className="w-16 h-20 rounded-lg overflow-hidden bg-purple-900/50 flex-shrink-0">
                <img
                  src={formData.coverImageUrl}
                  alt="미리보기"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">
            책표지 이미지 URL을 입력하면 서재에서 책표지가 표시됩니다
          </p>
        </div>

        {/* 장르 & 구매일 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 장르 */}
          <div>
            <label htmlFor="genre" className="block text-sm font-medium text-purple-200 mb-2">
              장르 *
            </label>
            <select
              id="genre"
              value={formData.genre}
              onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
              className={`w-full px-4 py-3 bg-white/5 border ${
                errors.genre ? 'border-red-500' : 'border-white/20'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all cursor-pointer`}
            >
              <option value="" className="bg-gray-800">
                장르 선택
              </option>
              {GENRES.map((genre) => (
                <option key={genre} value={genre} className="bg-gray-800">
                  {genre}
                </option>
              ))}
            </select>
            {errors.genre && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-400 text-sm mt-1"
              >
                {errors.genre}
              </motion.p>
            )}
          </div>

          {/* 구매일 */}
          <div>
            <label htmlFor="purchaseDate" className="block text-sm font-medium text-purple-200 mb-2">
              구매일 *
            </label>
            <input
              id="purchaseDate"
              type="date"
              value={formData.purchaseDate}
              onChange={(e) => setFormData({ ...formData, purchaseDate: e.target.value })}
              className={`w-full px-4 py-3 bg-white/5 border ${
                errors.purchaseDate ? 'border-red-500' : 'border-white/20'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all`}
            />
            {errors.purchaseDate && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-red-400 text-sm mt-1"
              >
                {errors.purchaseDate}
              </motion.p>
            )}
          </div>
        </div>

        {/* 페이지 수 */}
        <div>
          <label htmlFor="pageCount" className="block text-sm font-medium text-purple-200 mb-2">
            페이지 수: {formData.pageCount}쪽
          </label>
          <div className="flex items-center gap-4">
            <input
              id="pageCount"
              type="range"
              min="50"
              max="1000"
              step="10"
              value={formData.pageCount}
              onChange={(e) => setFormData({ ...formData, pageCount: Number(e.target.value) })}
              className="flex-1 h-2"
            />
            <input
              type="number"
              value={formData.pageCount}
              onChange={(e) => setFormData({ ...formData, pageCount: Number(e.target.value) })}
              className="w-24 px-3 py-2 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              min="1"
            />
          </div>
          <p className="text-sm text-gray-400 mt-2">
            예상 부채: <span className="text-red-400 font-semibold">{300 + formData.pageCount * 0.5}pt</span>
          </p>
        </div>

        {/* 제출 버튼 */}
        <motion.button
          type="submit"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-4 bg-gradient-to-r from-red-600 to-pink-600 text-white font-bold rounded-lg shadow-lg hover:shadow-red-500/50 transition-all"
        >
          📚 책 등록하기
        </motion.button>
      </form>
    </motion.div>
  );
}


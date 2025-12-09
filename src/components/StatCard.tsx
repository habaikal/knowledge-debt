import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface StatCardProps {
  icon: string;
  label: string;
  value: number;
  suffix?: string;
  color: 'blue' | 'green' | 'purple';
}

export function StatCard({ icon, label, value, suffix = '', color }: StatCardProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const [prevValue, setPrevValue] = useState(0);

  // 숫자 카운트 애니메이션
  useEffect(() => {
    if (value === displayValue) return;

    const duration = 500;
    const steps = 30;
    const increment = (value - displayValue) / steps;
    let current = displayValue;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current += increment;
      setDisplayValue(Math.round(current));

      if (step >= steps) {
        setDisplayValue(value);
        clearInterval(timer);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  // 값 변경 감지
  useEffect(() => {
    setPrevValue(displayValue);
  }, [value]);

  const colorClasses = {
    blue: {
      bg: 'from-blue-600 to-blue-400',
      glow: 'shadow-blue-500/50',
      text: 'text-blue-300',
    },
    green: {
      bg: 'from-green-600 to-emerald-400',
      glow: 'shadow-green-500/50',
      text: 'text-green-300',
    },
    purple: {
      bg: 'from-purple-600 to-purple-400',
      glow: 'shadow-purple-500/50',
      text: 'text-purple-300',
    },
  };

  const isIncreasing = value > prevValue;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.05, y: -5 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="relative"
    >
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-2xl border border-white/20">
        {/* 아이콘 */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', delay: 0.2 }}
          className="text-5xl mb-4"
        >
          {icon}
        </motion.div>

        {/* 라벨 */}
        <div className="text-sm text-purple-200 mb-2">{label}</div>

        {/* 값 */}
        <div className="flex items-baseline">
          <motion.div
            key={displayValue}
            initial={{ scale: isIncreasing ? 1.2 : 0.8 }}
            animate={{ scale: 1 }}
            className={`text-4xl font-bold bg-gradient-to-br ${colorClasses[color].bg} bg-clip-text text-transparent`}
          >
            {displayValue}
          </motion.div>
          <span className="text-lg text-white ml-2">{suffix}</span>
        </div>

        {/* 변화 표시 */}
        {value !== prevValue && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`absolute top-2 right-2 text-sm font-semibold ${
              isIncreasing ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {isIncreasing ? '↑' : '↓'} {Math.abs(value - prevValue)}
          </motion.div>
        )}

        {/* 빛나는 효과 */}
        <motion.div
          animate={{
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${colorClasses[color].bg} blur-xl ${colorClasses[color].glow} -z-10 opacity-30`}
        />
      </div>
    </motion.div>
  );
}


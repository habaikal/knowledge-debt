import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface CircularGaugeProps {
  value: number;
  maxValue: number;
  percentage: number;
}

export function CircularGauge({ value, maxValue, percentage }: CircularGaugeProps) {
  const [displayValue, setDisplayValue] = useState(0);

  // 숫자 카운트 애니메이션
  useEffect(() => {
    const duration = 1000; // 1초
    const steps = 60;
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

  // 색상 계산 (부채 많으면 빨강, 적으면 초록)
  const getColor = () => {
    if (percentage > 70) return 'from-red-600 to-red-400';
    if (percentage > 40) return 'from-orange-500 to-yellow-400';
    return 'from-green-500 to-emerald-400';
  };

  const getGlowColor = () => {
    if (percentage > 70) return 'shadow-red-500/50';
    if (percentage > 40) return 'shadow-yellow-500/50';
    return 'shadow-green-500/50';
  };

  // 원형 진행률 계산
  const circumference = 2 * Math.PI * 140; // 반지름 140
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <motion.div
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ type: 'spring', stiffness: 100, damping: 15 }}
      className="relative"
    >
      {/* 배경 원 */}
      <div className="relative w-80 h-80">
        <svg className="transform -rotate-90 w-full h-full">
          {/* 배경 트랙 */}
          <circle
            cx="160"
            cy="160"
            r="140"
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth="20"
            fill="none"
          />
          
          {/* 진행률 원 */}
          <motion.circle
            cx="160"
            cy="160"
            r="140"
            stroke="url(#gradient)"
            strokeWidth="20"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: 'easeInOut' }}
          />
          
          {/* 그라데이션 정의 */}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop
                offset="0%"
                className={percentage > 70 ? 'text-red-600' : percentage > 40 ? 'text-orange-500' : 'text-green-500'}
                stopColor="currentColor"
              />
              <stop
                offset="100%"
                className={percentage > 70 ? 'text-red-400' : percentage > 40 ? 'text-yellow-400' : 'text-emerald-400'}
                stopColor="currentColor"
              />
            </linearGradient>
          </defs>
        </svg>

        {/* 중앙 내용 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            key={displayValue}
            initial={{ scale: 1.2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className={`text-6xl font-bold bg-gradient-to-br ${getColor()} bg-clip-text text-transparent`}
          >
            {displayValue.toLocaleString()}
          </motion.div>
          <div className="text-2xl text-white mt-2">포인트</div>
          <div className="text-sm text-purple-300 mt-1">총 부채</div>
          
          {/* 상태 표시 */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: 'spring' }}
            className={`mt-4 px-4 py-2 rounded-full ${
              percentage > 70
                ? 'bg-red-500/20 text-red-300'
                : percentage > 40
                ? 'bg-yellow-500/20 text-yellow-300'
                : 'bg-green-500/20 text-green-300'
            }`}
          >
            {percentage > 70 ? '🔴 위험' : percentage > 40 ? '🟡 주의' : '🟢 양호'}
          </motion.div>
        </div>

        {/* 빛나는 효과 */}
        <motion.div
          animate={{
            scale: [1, 1.05, 1],
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className={`absolute inset-0 rounded-full bg-gradient-to-br ${getColor()} blur-3xl ${getGlowColor()} -z-10`}
        />
      </div>
    </motion.div>
  );
}


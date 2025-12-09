import { motion } from 'framer-motion';

export function ParticleEffect() {
  // 랜덤 파티클 생성
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 400 - 200,
    y: Math.random() * 400 - 200,
    scale: Math.random() * 1 + 0.5,
    duration: Math.random() * 0.5 + 0.5,
  }));

  return (
    <div className="absolute inset-0 pointer-events-none overflow-visible">
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          initial={{
            x: 0,
            y: 0,
            scale: 0,
            opacity: 1,
          }}
          animate={{
            x: particle.x,
            y: particle.y,
            scale: particle.scale,
            opacity: 0,
          }}
          transition={{
            duration: particle.duration,
            ease: 'easeOut',
          }}
          className="absolute top-1/2 left-1/2"
        >
          {/* 초록색 별 */}
          <div className="relative">
            {/* 외곽 빛 */}
            <div className="absolute inset-0 w-8 h-8 bg-green-400 rounded-full blur-md" />
            {/* 별 모양 */}
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              className="relative"
            >
              <path
                d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                fill="#4ade80"
                className="drop-shadow-[0_0_8px_rgba(74,222,128,0.8)]"
              />
            </svg>
          </div>
        </motion.div>
      ))}

      {/* 중앙 플래시 효과 */}
      <motion.div
        initial={{ scale: 0, opacity: 1 }}
        animate={{ scale: 3, opacity: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
      >
        <div className="w-32 h-32 bg-green-400 rounded-full blur-3xl" />
      </motion.div>

      {/* 원형 파동 효과 */}
      <motion.div
        initial={{ scale: 0, opacity: 0.8 }}
        animate={{ scale: 4, opacity: 0 }}
        transition={{ duration: 1, ease: 'easeOut' }}
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
      >
        <div className="w-32 h-32 border-4 border-green-400 rounded-full" />
      </motion.div>

      <motion.div
        initial={{ scale: 0, opacity: 0.6 }}
        animate={{ scale: 5, opacity: 0 }}
        transition={{ duration: 1.2, ease: 'easeOut', delay: 0.1 }}
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
      >
        <div className="w-32 h-32 border-4 border-green-300 rounded-full" />
      </motion.div>
    </div>
  );
}


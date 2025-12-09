import { motion, AnimatePresence } from 'framer-motion';
import type { Task } from '../types';

interface TaskListProps {
  tasks: Task[];
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

export function TaskList({ tasks, onToggle, onDelete }: TaskListProps) {
  return (
    <div className="space-y-2">
      <AnimatePresence>
        {tasks.map((task) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.2 }}
            className={`
              p-4 rounded-lg border-2 transition-colors
              ${task.completed 
                ? 'bg-gray-100 border-gray-300 dark:bg-gray-800 dark:border-gray-600' 
                : 'bg-white border-blue-300 dark:bg-gray-900 dark:border-blue-600'
              }
            `}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 flex-1">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => task.id && onToggle(task.id)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex-1">
                  <h3 className={`
                    text-lg font-semibold
                    ${task.completed ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}
                  `}>
                    {task.title}
                  </h3>
                  {task.description && (
                    <p className={`
                      text-sm mt-1
                      ${task.completed ? 'text-gray-400' : 'text-gray-600 dark:text-gray-400'}
                    `}>
                      {task.description}
                    </p>
                  )}
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => task.id && onDelete(task.id)}
                className="ml-4 px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
              >
                삭제
              </motion.button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}


// Task 타입 정의
export interface Task {
  id?: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at?: string;
}


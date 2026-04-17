export interface Task {
  id: string;
  text: string;
  category: string | null;
  duration_minutes: number | null;
  deadline: string | null;
  confirmed: boolean;
}

export interface TasksResponse {
  tasks: Task[];
}

export interface TimeBlock {
  start: string;
  end: string;
}

export interface Constraints {
  available_blocks: TimeBlock[];
  category_weights: {
    work: number;
    personal: number;
    health: number;
  };
}

export interface ScheduledTask {
  task_id: string;
  start_time: string;
  end_time: string;
  category: string;
}

export interface Schedule {
  id: string;
  created_at: string;
  tasks: ScheduledTask[];
}

export interface OptimizeResponse {
  schedule: Schedule;
  algorithm_used: string;
}

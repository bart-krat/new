export interface FixedTimeConstraint {
  task_id: string;
  start_minutes: number;  // Minutes from start of day (0-1439)
  end_minutes: number;    // Minutes from start of day (0-1439)
}

export interface Task {
  id: string;
  text: string;
  category: string | null;
  duration_minutes: number;  // Default 30 minutes
  deadline: string | null;
  confirmed: boolean;
  fixed_time_constraint: FixedTimeConstraint | null;
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

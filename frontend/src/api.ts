import { Task, TasksResponse, Constraints, Schedule, OptimizeResponse } from './types';

const API_BASE = 'http://localhost:8000/api';

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}

export async function submitTasks(tasks: string[]): Promise<Task[]> {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tasks }),
  });
  const data: TasksResponse = await res.json();
  return data.tasks;
}

export async function getTasks(): Promise<Task[]> {
  const res = await fetch(`${API_BASE}/tasks`);
  const data: TasksResponse = await res.json();
  return data.tasks;
}

export async function deleteTask(taskId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  return data.deleted;
}

export async function clearAllTasks(): Promise<boolean> {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'DELETE',
  });
  const data = await res.json();
  return data.cleared;
}

export async function categorizeTasks(taskIds: string[]): Promise<Task[]> {
  const res = await fetch(`${API_BASE}/categorize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_ids: taskIds }),
  });
  const data: TasksResponse = await res.json();
  return data.tasks;
}

export async function saveConstraints(constraints: Constraints): Promise<boolean> {
  const res = await fetch(`${API_BASE}/constraints`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(constraints),
  });
  const data = await res.json();
  return data.saved;
}

export async function getConstraints(): Promise<Constraints> {
  const res = await fetch(`${API_BASE}/constraints`);
  return res.json();
}

export async function optimizeTasks(
  taskIds: string[],
  constraints?: Constraints
): Promise<OptimizeResponse> {
  const res = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_ids: taskIds, constraints }),
  });
  return res.json();
}

export async function getSchedule(): Promise<Schedule | null> {
  const res = await fetch(`${API_BASE}/schedule`);
  const data = await res.json();
  return data.schedule;
}

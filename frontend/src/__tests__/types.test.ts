import { describe, it, expectTypeOf } from 'vitest';
import type { Task, TasksResponse } from '../types';

describe('Type definitions', () => {
  describe('Task', () => {
    it('has correct shape', () => {
      const task: Task = {
        id: '123',
        text: 'Test task',
        category: null,
        duration_minutes: 30,
        deadline: null,
        confirmed: false,
        fixed_time_constraint: null,
      };

      expectTypeOf(task.id).toBeString();
      expectTypeOf(task.text).toBeString();
      expectTypeOf(task.category).toEqualTypeOf<string | null>();
      expectTypeOf(task.duration_minutes).toBeNumber();
      expectTypeOf(task.deadline).toEqualTypeOf<string | null>();
      expectTypeOf(task.confirmed).toBeBoolean();
    });

    it('allows non-null category values', () => {
      const task: Task = {
        id: '123',
        text: 'Work task',
        category: 'work',
        duration_minutes: 60,
        deadline: '2024-12-31',
        confirmed: true,
        fixed_time_constraint: null,
      };

      expectTypeOf(task.category).toEqualTypeOf<string | null>();
    });
  });

  describe('TasksResponse', () => {
    it('contains tasks array', () => {
      const response: TasksResponse = {
        tasks: [],
      };

      expectTypeOf(response.tasks).toEqualTypeOf<Task[]>();
    });
  });
});

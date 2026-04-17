import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { checkHealth, submitTasks, getTasks, deleteTask } from '../api';

describe('API functions', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    globalThis.fetch = mockFetch;
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('checkHealth', () => {
    it('returns true when API returns ok status', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ status: 'ok' }),
      });

      const result = await checkHealth();

      expect(result).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/health');
    });

    it('returns false when API returns non-ok status', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ status: 'error' }),
      });

      const result = await checkHealth();

      expect(result).toBe(false);
    });

    it('returns false when fetch throws error', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      const result = await checkHealth();

      expect(result).toBe(false);
    });
  });

  describe('submitTasks', () => {
    it('sends POST request with tasks', async () => {
      const mockTasks = [
        { id: '1', text: 'Task 1', category: null, duration_minutes: null, deadline: null, confirmed: false },
      ];
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: mockTasks }),
      });

      const result = await submitTasks(['Task 1']);

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tasks: ['Task 1'] }),
      });
      expect(result).toEqual(mockTasks);
    });

    it('returns array of created tasks', async () => {
      const mockTasks = [
        { id: '1', text: 'Buy groceries', category: null, duration_minutes: null, deadline: null, confirmed: false },
        { id: '2', text: 'Call mom', category: null, duration_minutes: null, deadline: null, confirmed: false },
      ];
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: mockTasks }),
      });

      const result = await submitTasks(['Buy groceries', 'Call mom']);

      expect(result).toHaveLength(2);
      expect(result[0].text).toBe('Buy groceries');
      expect(result[1].text).toBe('Call mom');
    });
  });

  describe('getTasks', () => {
    it('sends GET request to tasks endpoint', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: [] }),
      });

      await getTasks();

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/tasks');
    });

    it('returns empty array when no tasks exist', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: [] }),
      });

      const result = await getTasks();

      expect(result).toEqual([]);
    });

    it('returns array of tasks', async () => {
      const mockTasks = [
        { id: '1', text: 'Existing task', category: 'work', duration_minutes: 30, deadline: null, confirmed: true },
      ];
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: mockTasks }),
      });

      const result = await getTasks();

      expect(result).toHaveLength(1);
      expect(result[0].text).toBe('Existing task');
      expect(result[0].category).toBe('work');
    });
  });

  describe('deleteTask', () => {
    it('sends DELETE request to task endpoint', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ deleted: true }),
      });

      await deleteTask('task-123');

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/tasks/task-123', {
        method: 'DELETE',
      });
    });

    it('returns true when deletion succeeds', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ deleted: true }),
      });

      const result = await deleteTask('task-123');

      expect(result).toBe(true);
    });

    it('returns false when deletion fails', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ deleted: false }),
      });

      const result = await deleteTask('task-123');

      expect(result).toBe(false);
    });
  });
});

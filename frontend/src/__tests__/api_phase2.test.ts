import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { categorizeTasks, saveConstraints, getConstraints } from '../api';

describe('Phase 2 API functions', () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    globalThis.fetch = mockFetch;
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('categorizeTasks', () => {
    it('sends POST request with task IDs', async () => {
      const mockTasks = [
        { id: '1', text: 'Go to gym', category: 'health', duration_minutes: 45, deadline: null, confirmed: false },
      ];
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: mockTasks }),
      });

      await categorizeTasks(['1', '2']);

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/categorize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_ids: ['1', '2'] }),
      });
    });

    it('returns categorized tasks', async () => {
      const mockTasks = [
        { id: '1', text: 'Go to gym', category: 'health', duration_minutes: 45, deadline: null, confirmed: false },
        { id: '2', text: 'Send email', category: 'work', duration_minutes: 30, deadline: null, confirmed: false },
      ];
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: mockTasks }),
      });

      const result = await categorizeTasks(['1', '2']);

      expect(result).toHaveLength(2);
      expect(result[0].category).toBe('health');
      expect(result[1].category).toBe('work');
    });

    it('returns empty array when no tasks', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ tasks: [] }),
      });

      const result = await categorizeTasks([]);

      expect(result).toEqual([]);
    });
  });

  describe('saveConstraints', () => {
    it('sends POST request with constraints', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ saved: true }),
      });

      const constraints = {
        available_blocks: [{ start: '09:00', end: '17:00' }],
        category_weights: { work: 0.5, personal: 0.3, health: 0.2 },
      };

      await saveConstraints(constraints);

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/constraints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(constraints),
      });
    });

    it('returns true when save succeeds', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ saved: true }),
      });

      const result = await saveConstraints({
        available_blocks: [],
        category_weights: { work: 0.33, personal: 0.33, health: 0.34 },
      });

      expect(result).toBe(true);
    });

    it('returns false when save fails', async () => {
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve({ saved: false }),
      });

      const result = await saveConstraints({
        available_blocks: [],
        category_weights: { work: 0.5, personal: 0.3, health: 0.2 },
      });

      expect(result).toBe(false);
    });
  });

  describe('getConstraints', () => {
    it('sends GET request to constraints endpoint', async () => {
      mockFetch.mockResolvedValue({
        json: () =>
          Promise.resolve({
            available_blocks: [],
            category_weights: { work: 0.4, personal: 0.3, health: 0.3 },
          }),
      });

      await getConstraints();

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/constraints');
    });

    it('returns constraints data', async () => {
      const mockConstraints = {
        available_blocks: [{ start: '09:00', end: '17:00' }],
        category_weights: { work: 0.5, personal: 0.3, health: 0.2 },
      };
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve(mockConstraints),
      });

      const result = await getConstraints();

      expect(result.available_blocks).toHaveLength(1);
      expect(result.available_blocks[0].start).toBe('09:00');
      expect(result.category_weights.work).toBe(0.5);
    });

    it('returns default constraints when none saved', async () => {
      mockFetch.mockResolvedValue({
        json: () =>
          Promise.resolve({
            available_blocks: [],
            category_weights: { work: 0.4, personal: 0.3, health: 0.3 },
          }),
      });

      const result = await getConstraints();

      expect(result.available_blocks).toEqual([]);
      expect(result.category_weights).toBeDefined();
    });

    it('handles multiple time blocks', async () => {
      const mockConstraints = {
        available_blocks: [
          { start: '09:00', end: '12:00' },
          { start: '13:00', end: '17:00' },
        ],
        category_weights: { work: 0.5, personal: 0.3, health: 0.2 },
      };
      mockFetch.mockResolvedValue({
        json: () => Promise.resolve(mockConstraints),
      });

      const result = await getConstraints();

      expect(result.available_blocks).toHaveLength(2);
    });
  });
});

import { describe, it, expectTypeOf } from 'vitest';
import type { TimeBlock, Constraints } from '../types';

describe('Phase 2 Type definitions', () => {
  describe('TimeBlock', () => {
    it('has correct shape', () => {
      const block: TimeBlock = {
        start: '09:00',
        end: '17:00',
      };

      expectTypeOf(block.start).toBeString();
      expectTypeOf(block.end).toBeString();
    });
  });

  describe('Constraints', () => {
    it('has correct shape', () => {
      const constraints: Constraints = {
        available_blocks: [{ start: '09:00', end: '17:00' }],
        category_weights: {
          work: 0.5,
          personal: 0.3,
          health: 0.2,
        },
      };

      expectTypeOf(constraints.available_blocks).toEqualTypeOf<TimeBlock[]>();
      expectTypeOf(constraints.category_weights.work).toBeNumber();
      expectTypeOf(constraints.category_weights.personal).toBeNumber();
      expectTypeOf(constraints.category_weights.health).toBeNumber();
    });

    it('allows empty available_blocks', () => {
      const constraints: Constraints = {
        available_blocks: [],
        category_weights: {
          work: 0.5,
          personal: 0.3,
          health: 0.2,
        },
      };

      expectTypeOf(constraints.available_blocks).toEqualTypeOf<TimeBlock[]>();
    });

    it('allows multiple time blocks', () => {
      const constraints: Constraints = {
        available_blocks: [
          { start: '09:00', end: '12:00' },
          { start: '13:00', end: '17:00' },
          { start: '19:00', end: '21:00' },
        ],
        category_weights: {
          work: 0.4,
          personal: 0.4,
          health: 0.2,
        },
      };

      expectTypeOf(constraints.available_blocks).toEqualTypeOf<TimeBlock[]>();
    });
  });
});

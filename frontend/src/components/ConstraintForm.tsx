import { useState } from 'react';
import { TimeBlock } from '../types';

interface ConstraintFormProps {
  blocks: TimeBlock[];
  onChange: (blocks: TimeBlock[]) => void;
}

export function ConstraintForm({ blocks, onChange }: ConstraintFormProps) {
  const [newStart, setNewStart] = useState('09:00');
  const [newEnd, setNewEnd] = useState('12:00');

  const addBlock = () => {
    onChange([...blocks, { start: newStart, end: newEnd }]);
    setNewStart('09:00');
    setNewEnd('12:00');
  };

  const removeBlock = (index: number) => {
    onChange(blocks.filter((_, i) => i !== index));
  };

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <h3>Available Time Blocks</h3>
      <p style={{ fontSize: '0.9rem', color: '#666' }}>
        Add time blocks when you're available to work on tasks
      </p>

      {blocks.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {blocks.map((block, i) => (
            <li
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '0.5rem',
              }}
            >
              <span>
                {block.start} - {block.end}
              </span>
              <button type="button" onClick={() => removeBlock(i)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <input
          type="time"
          value={newStart}
          onChange={(e) => setNewStart(e.target.value)}
        />
        <span>to</span>
        <input
          type="time"
          value={newEnd}
          onChange={(e) => setNewEnd(e.target.value)}
        />
        <button type="button" onClick={addBlock}>
          Add Block
        </button>
      </div>
    </div>
  );
}

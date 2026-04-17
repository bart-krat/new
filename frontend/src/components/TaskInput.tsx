import { useState } from 'react';

interface TaskInputProps {
  onSubmit: (tasks: string[]) => void;
  disabled?: boolean;
}

export function TaskInput({ onSubmit, disabled }: TaskInputProps) {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const tasks = text
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);
    if (tasks.length > 0) {
      onSubmit(tasks);
      setText('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
      <h2>Add Tasks</h2>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter tasks separated by commas (e.g., buy groceries, finish report, call mom)"
        disabled={disabled}
        style={{ width: '100%', padding: '0.5rem', fontSize: '1rem', boxSizing: 'border-box' }}
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        style={{ marginTop: '0.5rem', padding: '0.5rem 1rem' }}
      >
        {disabled ? 'Adding...' : 'Add Tasks'}
      </button>
    </form>
  );
}

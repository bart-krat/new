import { useState } from 'react';
import { FixedTimeConstraint as FixedTimeConstraintType } from '../types';

interface FixedTimeConstraintProps {
  taskId: string;
  constraint: FixedTimeConstraintType | null;
  onSave: (taskId: string, startMinutes: number, endMinutes: number) => void;
  onClear: (taskId: string) => void;
}

function minutesToTimeString(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

function timeStringToMinutes(timeStr: string): number {
  const [hours, mins] = timeStr.split(':').map(Number);
  return hours * 60 + mins;
}

function formatTimeDisplay(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
}

export function FixedTimeConstraintEditor({
  taskId,
  constraint,
  onSave,
  onClear,
}: FixedTimeConstraintProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [startTime, setStartTime] = useState(
    constraint ? minutesToTimeString(constraint.start_minutes) : '09:00'
  );
  const [endTime, setEndTime] = useState(
    constraint ? minutesToTimeString(constraint.end_minutes) : '10:00'
  );

  const handleSave = () => {
    const startMinutes = timeStringToMinutes(startTime);
    const endMinutes = timeStringToMinutes(endTime);

    if (endMinutes <= startMinutes) {
      alert('End time must be after start time');
      return;
    }

    onSave(taskId, startMinutes, endMinutes);
    setIsEditing(false);
  };

  const handleClear = () => {
    onClear(taskId);
    setIsEditing(false);
  };

  if (!isEditing && !constraint) {
    return (
      <button
        onClick={() => setIsEditing(true)}
        style={{
          background: '#e5e7eb',
          border: 'none',
          borderRadius: '4px',
          padding: '0.2rem 0.4rem',
          fontSize: '0.7rem',
          cursor: 'pointer',
          color: '#4b5563',
        }}
        title="Set fixed time window"
      >
        + Time
      </button>
    );
  }

  if (!isEditing && constraint) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        <span
          style={{
            background: '#dbeafe',
            color: '#1d4ed8',
            padding: '0.2rem 0.4rem',
            borderRadius: '4px',
            fontSize: '0.7rem',
            cursor: 'pointer',
          }}
          onClick={() => setIsEditing(true)}
          title="Click to edit fixed time window"
        >
          {formatTimeDisplay(constraint.start_minutes)} - {formatTimeDisplay(constraint.end_minutes)}
        </span>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem',
        background: '#f3f4f6',
        padding: '0.25rem',
        borderRadius: '4px',
      }}
    >
      <input
        type="time"
        value={startTime}
        onChange={(e) => setStartTime(e.target.value)}
        style={{ fontSize: '0.75rem', padding: '0.1rem' }}
      />
      <span style={{ fontSize: '0.75rem' }}>-</span>
      <input
        type="time"
        value={endTime}
        onChange={(e) => setEndTime(e.target.value)}
        style={{ fontSize: '0.75rem', padding: '0.1rem' }}
      />
      <button
        onClick={handleSave}
        style={{
          background: '#22c55e',
          color: 'white',
          border: 'none',
          borderRadius: '3px',
          padding: '0.15rem 0.3rem',
          fontSize: '0.7rem',
          cursor: 'pointer',
        }}
      >
        Save
      </button>
      {constraint && (
        <button
          onClick={handleClear}
          style={{
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            padding: '0.15rem 0.3rem',
            fontSize: '0.7rem',
            cursor: 'pointer',
          }}
        >
          Clear
        </button>
      )}
      <button
        onClick={() => setIsEditing(false)}
        style={{
          background: '#9ca3af',
          color: 'white',
          border: 'none',
          borderRadius: '3px',
          padding: '0.15rem 0.3rem',
          fontSize: '0.7rem',
          cursor: 'pointer',
        }}
      >
        Cancel
      </button>
    </div>
  );
}

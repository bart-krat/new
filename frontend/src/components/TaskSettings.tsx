import { useState, useEffect } from 'react';
import { FixedTimeConstraint as FixedTimeConstraintType } from '../types';

interface TaskSettingsProps {
  taskId: string;
  duration: number;  // Default 30 minutes
  fixedConstraint: FixedTimeConstraintType | null;
  onDurationChange: (taskId: string, duration: number) => void;
  onFixedConstraintSave: (taskId: string, startMinutes: number, endMinutes: number) => void;
  onFixedConstraintClear: (taskId: string) => void;
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

export function TaskSettings({
  taskId,
  duration,
  fixedConstraint,
  onDurationChange,
  onFixedConstraintSave,
  onFixedConstraintClear,
}: TaskSettingsProps) {
  const [localDuration, setLocalDuration] = useState<string>(String(duration));
  const [localStartTime, setLocalStartTime] = useState<string>(
    fixedConstraint ? minutesToTimeString(fixedConstraint.start_minutes) : ''
  );

  // Sync local state when props change
  useEffect(() => {
    setLocalDuration(String(duration));
  }, [duration]);

  useEffect(() => {
    setLocalStartTime(fixedConstraint ? minutesToTimeString(fixedConstraint.start_minutes) : '');
  }, [fixedConstraint]);

  const handleDurationBlur = () => {
    const parsed = parseInt(localDuration) || duration;
    const clamped = Math.max(1, Math.min(480, parsed));
    setLocalDuration(String(clamped));
    if (clamped !== duration) {
      onDurationChange(taskId, clamped);
    }
  };

  const handleStartTimeBlur = () => {
    const currentStart = fixedConstraint ? minutesToTimeString(fixedConstraint.start_minutes) : '';

    if (localStartTime === '') {
      // Clear the constraint if it was set before
      if (fixedConstraint) {
        onFixedConstraintClear(taskId);
      }
    } else if (localStartTime !== currentStart) {
      // Only save if the value has changed
      const startMinutes = timeStringToMinutes(localStartTime);
      const durationMins = parseInt(localDuration) || duration;
      const endMinutes = Math.min(startMinutes + durationMins, 1439); // Cap at 23:59
      onFixedConstraintSave(taskId, startMinutes, endMinutes);
    }
  };

  const handleClearTime = () => {
    setLocalStartTime('');
    if (fixedConstraint) {
      onFixedConstraintClear(taskId);
    }
  };

  const currentDuration = parseInt(localDuration) || duration;

  return (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontSize: '0.85rem' }}>
      {/* Duration */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        <label style={{ color: '#6b7280' }}>Duration:</label>
        <input
          type="number"
          value={localDuration}
          onChange={(e) => setLocalDuration(e.target.value)}
          onBlur={handleDurationBlur}
          min={1}
          max={480}
          style={{
            width: '50px',
            padding: '0.25rem',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            fontSize: '0.85rem',
          }}
        />
        <span style={{ color: '#6b7280' }}>min</span>
      </div>

      {/* Fixed Start Time */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        <label style={{ color: '#6b7280' }}>Start at:</label>
        <input
          type="time"
          value={localStartTime}
          onChange={(e) => setLocalStartTime(e.target.value)}
          onBlur={handleStartTimeBlur}
          style={{
            padding: '0.25rem',
            border: '1px solid #d1d5db',
            borderRadius: '4px',
            fontSize: '0.85rem',
            minWidth: '100px',
          }}
        />
        {localStartTime && (
          <>
            <span style={{ color: '#6b7280', fontSize: '0.75rem' }}>
              (ends {formatTimeDisplay(timeStringToMinutes(localStartTime) + currentDuration)})
            </span>
            <button
              onClick={handleClearTime}
              style={{
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                padding: '0.15rem 0.4rem',
                fontSize: '0.7rem',
                cursor: 'pointer',
              }}
              title="Clear fixed time"
            >
              X
            </button>
          </>
        )}
      </div>
    </div>
  );
}

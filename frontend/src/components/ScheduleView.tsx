import { Schedule, Task } from '../types';

interface ScheduleViewProps {
  schedule: Schedule | null;
  tasks: Task[];
  algorithmUsed: string | null;
}

const CATEGORY_COLORS: Record<string, string> = {
  work: '#3b82f6',
  personal: '#22c55e',
  health: '#f59e0b',
};

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

function getDurationMinutes(start: string, end: string): number {
  const startDate = new Date(start);
  const endDate = new Date(end);
  return Math.round((endDate.getTime() - startDate.getTime()) / 60000);
}

export function ScheduleView({ schedule, tasks, algorithmUsed }: ScheduleViewProps) {
  if (!schedule || schedule.tasks.length === 0) {
    return (
      <div style={{ marginTop: '1.5rem' }}>
        <h2>Your Schedule</h2>
        <p style={{ color: '#666' }}>
          No schedule generated yet. Add tasks and click "Generate Schedule".
        </p>
      </div>
    );
  }

  // Create a map of task_id to task for quick lookup
  const taskMap = new Map(tasks.map((t) => [t.id, t]));

  return (
    <div style={{ marginTop: '1.5rem' }}>
      <h2>Your Schedule</h2>
      {algorithmUsed && (
        <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
          Generated using: <strong>{algorithmUsed}</strong> algorithm
        </p>
      )}

      <div
        style={{
          border: '1px solid #ddd',
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      >
        {schedule.tasks.map((scheduledTask, index) => {
          const task = taskMap.get(scheduledTask.task_id);
          const duration = getDurationMinutes(
            scheduledTask.start_time,
            scheduledTask.end_time
          );

          return (
            <div
              key={scheduledTask.task_id}
              style={{
                display: 'flex',
                alignItems: 'stretch',
                borderBottom:
                  index < schedule.tasks.length - 1 ? '1px solid #eee' : 'none',
              }}
            >
              {/* Time column */}
              <div
                style={{
                  width: '100px',
                  padding: '1rem',
                  background: '#f9f9f9',
                  borderRight: '1px solid #eee',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                }}
              >
                <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>
                  {formatTime(scheduledTask.start_time)}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#666' }}>
                  {duration} min
                </div>
              </div>

              {/* Category bar */}
              <div
                style={{
                  width: '4px',
                  background: CATEGORY_COLORS[scheduledTask.category] || '#888',
                }}
              />

              {/* Task details */}
              <div style={{ flex: 1, padding: '1rem' }}>
                <div style={{ fontWeight: '500' }}>
                  {task?.text || 'Unknown task'}
                </div>
                <div
                  style={{
                    display: 'flex',
                    gap: '0.5rem',
                    marginTop: '0.25rem',
                    alignItems: 'center',
                  }}
                >
                  <span
                    style={{
                      background: CATEGORY_COLORS[scheduledTask.category] || '#888',
                      color: 'white',
                      padding: '0.1rem 0.4rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                    }}
                  >
                    {scheduledTask.category}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#666' }}>
                    {formatTime(scheduledTask.start_time)} -{' '}
                    {formatTime(scheduledTask.end_time)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.5rem' }}>
        {schedule.tasks.length} task{schedule.tasks.length !== 1 ? 's' : ''} scheduled
      </p>
    </div>
  );
}

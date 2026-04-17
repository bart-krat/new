import { useState, useEffect } from 'react';
import { TaskInput } from './components/TaskInput';
import { ConstraintForm } from './components/ConstraintForm';
import { UtilityWeights } from './components/UtilityWeights';
import { ScheduleView } from './components/ScheduleView';
import {
  checkHealth,
  submitTasks,
  categorizeTasks,
  saveConstraints,
  getConstraints,
  deleteTask,
  clearAllTasks,
  optimizeTasks,
} from './api';
import { Task, TimeBlock, Constraints, Schedule } from './types';

const CATEGORY_COLORS: Record<string, string> = {
  work: '#3b82f6',
  personal: '#22c55e',
  health: '#f59e0b',
};

function App() {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [processing, setProcessing] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [blocks, setBlocks] = useState<TimeBlock[]>([]);
  const [weights, setWeights] = useState({ work: 0.4, personal: 0.3, health: 0.3 });
  const [constraintsSaved, setConstraintsSaved] = useState(false);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [algorithmUsed, setAlgorithmUsed] = useState<string | null>(null);

  useEffect(() => {
    const init = async () => {
      // Check backend health
      const isConnected = await checkHealth();
      setConnected(isConnected);

      // Clear tasks on page load (also clears schedule on backend)
      await clearAllTasks().catch(() => {});

      // Load saved constraints (but not schedule since we just cleared it)
      try {
        const c = await getConstraints();
        setBlocks(c.available_blocks || []);
        setWeights(c.category_weights || { work: 0.4, personal: 0.3, health: 0.3 });
      } catch {
        // Use defaults if fetch fails
      }

      // Don't fetch schedule - it was just cleared with tasks
      setSchedule(null);
    };

    init();
  }, []);

  const handleSubmit = async (newTasks: string[]) => {
    setProcessing(true);
    setError(null);
    try {
      // Add tasks
      const created = await submitTasks(newTasks);
      setTasks((prev) => [...prev, ...created]);

      // Auto-categorize the new tasks
      if (created.length > 0) {
        try {
          const categorized = await categorizeTasks(created.map((t) => t.id));
          setTasks((prev) =>
            prev.map((t) => {
              const updated = categorized.find((c) => c.id === t.id);
              return updated || t;
            })
          );
        } catch (catError) {
          console.error('Categorization failed:', catError);
          // Tasks are still added, just not categorized
        }
      }
    } catch (err) {
      console.error('Failed to add tasks:', err);
      setError('Failed to add tasks. Make sure the backend is running.');
    } finally {
      setProcessing(false);
    }
  };

  const handleDelete = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error('Failed to delete task:', err);
      setError('Failed to delete task.');
    }
  };

  const handleSaveConstraints = async () => {
    const constraints: Constraints = {
      available_blocks: blocks,
      category_weights: weights,
    };
    try {
      await saveConstraints(constraints);
      setConstraintsSaved(true);
      setTimeout(() => setConstraintsSaved(false), 2000);
    } catch (err) {
      console.error('Failed to save constraints:', err);
      setError('Failed to save settings.');
    }
  };

  const handleOptimize = async () => {
    if (tasks.length === 0) {
      setError('Add some tasks first!');
      return;
    }
    if (blocks.length === 0) {
      setError('Add at least one time block in Planning Settings.');
      return;
    }

    setOptimizing(true);
    setError(null);
    try {
      const constraints: Constraints = {
        available_blocks: blocks,
        category_weights: weights,
      };
      const result = await optimizeTasks(
        tasks.map((t) => t.id),
        constraints
      );
      setSchedule(result.schedule);
      setAlgorithmUsed(result.algorithm_used);
    } catch (err) {
      console.error('Failed to optimize:', err);
      setError('Failed to generate schedule.');
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
      <h1>AI Daily Planner</h1>
      <p>
        Backend status:{' '}
        {connected === null
          ? 'Checking...'
          : connected
          ? '✓ Connected'
          : '✗ Not connected'}
      </p>

      {error && (
        <p style={{ color: 'red', background: '#fee2e2', padding: '0.5rem', borderRadius: '4px' }}>
          {error}
        </p>
      )}

      <TaskInput onSubmit={handleSubmit} disabled={processing} />

      <h2>Your Tasks</h2>
      {processing && <p>Adding and categorizing tasks...</p>}
      {tasks.length === 0 && !processing ? (
        <p>No tasks yet. Add some above!</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {tasks.map((task) => (
            <li
              key={task.id}
              style={{
                padding: '0.5rem',
                marginBottom: '0.5rem',
                background: '#f5f5f5',
                borderRadius: '4px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span>{task.text}</span>
              <span style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                {task.category && (
                  <span
                    style={{
                      background: CATEGORY_COLORS[task.category] || '#888',
                      color: 'white',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                    }}
                  >
                    {task.category}
                  </span>
                )}
                {task.duration_minutes && (
                  <span style={{ fontSize: '0.8rem', color: '#666' }}>
                    {task.duration_minutes}m
                  </span>
                )}
                <button
                  onClick={() => handleDelete(task.id)}
                  style={{
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '0.2rem 0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                  }}
                >
                  Delete
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}

      <hr style={{ margin: '2rem 0' }} />

      <h2>Planning Settings</h2>
      <ConstraintForm blocks={blocks} onChange={setBlocks} />
      <UtilityWeights weights={weights} onChange={setWeights} />

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '1rem' }}>
        <button
          onClick={handleSaveConstraints}
          style={{ padding: '0.5rem 1rem' }}
        >
          Save Settings
        </button>
        {constraintsSaved && (
          <span style={{ color: 'green' }}>✓ Saved</span>
        )}
      </div>

      <hr style={{ margin: '2rem 0' }} />

      <button
        onClick={handleOptimize}
        disabled={optimizing || tasks.length === 0}
        style={{
          padding: '0.75rem 1.5rem',
          fontSize: '1rem',
          background: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: tasks.length === 0 ? 'not-allowed' : 'pointer',
          opacity: tasks.length === 0 ? 0.5 : 1,
        }}
      >
        {optimizing ? 'Generating...' : 'Generate Schedule'}
      </button>

      <ScheduleView schedule={schedule} tasks={tasks} algorithmUsed={algorithmUsed} />
    </div>
  );
}

export default App;

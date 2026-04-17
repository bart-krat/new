import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import * as api from '../api';

vi.mock('../api');

describe('App', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    // Default mocks for all API calls
    vi.mocked(api.checkHealth).mockResolvedValue(true);
    vi.mocked(api.getConstraints).mockResolvedValue({
      available_blocks: [],
      category_weights: { work: 0.4, personal: 0.3, health: 0.3 },
    });
    vi.mocked(api.deleteTask).mockResolvedValue(true);
    vi.mocked(api.submitTasks).mockResolvedValue([]);
    vi.mocked(api.categorizeTasks).mockResolvedValue([]);
    vi.mocked(api.saveConstraints).mockResolvedValue(true);
    vi.mocked(api.clearAllTasks).mockResolvedValue(true);
    vi.mocked(api.optimizeTasks).mockResolvedValue({
      schedule: { id: '1', created_at: new Date().toISOString(), tasks: [] },
      algorithm_used: 'greedy',
    });
    vi.mocked(api.getSchedule).mockResolvedValue(null);
  });

  it('renders app title', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /ai daily planner/i })).toBeInTheDocument();
  });

  it('shows checking status initially', () => {
    vi.mocked(api.checkHealth).mockImplementation(() => new Promise(() => {}));

    render(<App />);

    expect(screen.getByText(/checking/i)).toBeInTheDocument();
  });

  it('shows connected when health check passes', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/connected/i)).toBeInTheDocument();
    });
  });

  it('shows not connected when health check fails', async () => {
    vi.mocked(api.checkHealth).mockResolvedValue(false);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/not connected/i)).toBeInTheDocument();
    });
  });

  it('shows no tasks message when task list is empty', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument();
    });
  });

  it('renders Generate Schedule button', async () => {
    render(<App />);

    expect(screen.getByRole('button', { name: /generate schedule/i })).toBeInTheDocument();
  });

  it('renders TaskInput component', async () => {
    render(<App />);

    expect(screen.getByPlaceholderText(/enter tasks separated by commas/i)).toBeInTheDocument();
  });

  it('renders Your Tasks heading', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /your tasks/i })).toBeInTheDocument();
  });

  it('renders Planning Settings section', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /planning settings/i })).toBeInTheDocument();
  });

  it('renders ConstraintForm component', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /available time blocks/i })).toBeInTheDocument();
  });

  it('renders UtilityWeights component', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /category priorities/i })).toBeInTheDocument();
  });

  it('renders Save Settings button', async () => {
    render(<App />);

    expect(screen.getByRole('button', { name: /save settings/i })).toBeInTheDocument();
  });

  it('renders ScheduleView component', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /your schedule/i })).toBeInTheDocument();
  });

  it('shows no schedule message when schedule is empty', async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText(/no schedule generated yet/i)).toBeInTheDocument();
    });
  });
});

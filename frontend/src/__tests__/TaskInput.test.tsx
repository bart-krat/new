import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskInput } from '../components/TaskInput';

describe('TaskInput', () => {
  it('renders input and submit button', () => {
    render(<TaskInput onSubmit={() => {}} />);
    expect(screen.getByPlaceholderText(/enter tasks separated by commas/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add tasks/i })).toBeInTheDocument();
  });

  it('calls onSubmit with parsed tasks when form is submitted', () => {
    const onSubmit = vi.fn();
    render(<TaskInput onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i);
    fireEvent.change(input, { target: { value: 'Task 1, Task 2, Task 3' } });
    fireEvent.click(screen.getByRole('button', { name: /add tasks/i }));

    expect(onSubmit).toHaveBeenCalledWith(['Task 1', 'Task 2', 'Task 3']);
  });

  it('clears input after submission', () => {
    render(<TaskInput onSubmit={() => {}} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Task to clear' } });
    fireEvent.click(screen.getByRole('button', { name: /add tasks/i }));

    expect(input.value).toBe('');
  });

  it('filters out empty entries from comma separation', () => {
    const onSubmit = vi.fn();
    render(<TaskInput onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i);
    fireEvent.change(input, { target: { value: 'Task 1,, ,Task 2,   ,Task 3' } });
    fireEvent.click(screen.getByRole('button', { name: /add tasks/i }));

    expect(onSubmit).toHaveBeenCalledWith(['Task 1', 'Task 2', 'Task 3']);
  });

  it('trims whitespace from tasks', () => {
    const onSubmit = vi.fn();
    render(<TaskInput onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i);
    fireEvent.change(input, { target: { value: '  Task with spaces  ' } });
    fireEvent.click(screen.getByRole('button', { name: /add tasks/i }));

    expect(onSubmit).toHaveBeenCalledWith(['Task with spaces']);
  });

  it('does not call onSubmit when input is empty', () => {
    const onSubmit = vi.fn();
    render(<TaskInput onSubmit={onSubmit} />);

    // Button should be disabled when empty
    const button = screen.getByRole('button', { name: /add tasks/i });
    expect(button).toBeDisabled();
  });

  it('does not call onSubmit when input has only whitespace', () => {
    const onSubmit = vi.fn();
    render(<TaskInput onSubmit={onSubmit} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i);
    fireEvent.change(input, { target: { value: '   ' } });

    // Button should still be disabled
    const button = screen.getByRole('button', { name: /add tasks/i });
    expect(button).toBeDisabled();
  });

  it('renders heading', () => {
    render(<TaskInput onSubmit={() => {}} />);
    expect(screen.getByRole('heading', { name: /add tasks/i })).toBeInTheDocument();
  });

  it('disables input when disabled prop is true', () => {
    render(<TaskInput onSubmit={() => {}} disabled={true} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i);
    expect(input).toBeDisabled();
  });

  it('shows Adding... text when disabled', () => {
    render(<TaskInput onSubmit={() => {}} disabled={true} />);

    expect(screen.getByRole('button', { name: /adding/i })).toBeInTheDocument();
  });

  it('enables button when input has content', () => {
    render(<TaskInput onSubmit={() => {}} />);

    const input = screen.getByPlaceholderText(/enter tasks separated by commas/i);
    fireEvent.change(input, { target: { value: 'Some task' } });

    const button = screen.getByRole('button', { name: /add tasks/i });
    expect(button).not.toBeDisabled();
  });
});

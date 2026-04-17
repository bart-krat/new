import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConstraintForm } from '../components/ConstraintForm';

describe('ConstraintForm', () => {
  const defaultProps = {
    blocks: [],
    onChange: vi.fn(),
  };

  it('renders heading and description', () => {
    render(<ConstraintForm {...defaultProps} />);
    expect(screen.getByRole('heading', { name: /available time blocks/i })).toBeInTheDocument();
    expect(screen.getByText(/add time blocks/i)).toBeInTheDocument();
  });

  it('renders time input fields', () => {
    render(<ConstraintForm {...defaultProps} />);
    // Time inputs don't have role="textbox", query by type attribute
    const timeInputs = document.querySelectorAll('input[type="time"]');
    expect(timeInputs.length).toBe(2);
  });

  it('renders add block button', () => {
    render(<ConstraintForm {...defaultProps} />);
    expect(screen.getByRole('button', { name: /add block/i })).toBeInTheDocument();
  });

  it('calls onChange when adding a block', () => {
    const onChange = vi.fn();
    render(<ConstraintForm blocks={[]} onChange={onChange} />);

    fireEvent.click(screen.getByRole('button', { name: /add block/i }));

    expect(onChange).toHaveBeenCalledWith([{ start: '09:00', end: '12:00' }]);
  });

  it('displays existing blocks', () => {
    const blocks = [
      { start: '09:00', end: '12:00' },
      { start: '14:00', end: '17:00' },
    ];
    render(<ConstraintForm blocks={blocks} onChange={vi.fn()} />);

    expect(screen.getByText('09:00 - 12:00')).toBeInTheDocument();
    expect(screen.getByText('14:00 - 17:00')).toBeInTheDocument();
  });

  it('renders remove button for each block', () => {
    const blocks = [
      { start: '09:00', end: '12:00' },
      { start: '14:00', end: '17:00' },
    ];
    render(<ConstraintForm blocks={blocks} onChange={vi.fn()} />);

    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    expect(removeButtons).toHaveLength(2);
  });

  it('calls onChange with filtered blocks when removing', () => {
    const onChange = vi.fn();
    const blocks = [
      { start: '09:00', end: '12:00' },
      { start: '14:00', end: '17:00' },
    ];
    render(<ConstraintForm blocks={blocks} onChange={onChange} />);

    const removeButtons = screen.getAllByRole('button', { name: /remove/i });
    fireEvent.click(removeButtons[0]);

    expect(onChange).toHaveBeenCalledWith([{ start: '14:00', end: '17:00' }]);
  });

  it('adds block with custom time values', () => {
    const onChange = vi.fn();
    render(<ConstraintForm blocks={[]} onChange={onChange} />);

    // Find time inputs and change values
    const inputs = document.querySelectorAll('input[type="time"]');
    fireEvent.change(inputs[0], { target: { value: '10:30' } });
    fireEvent.change(inputs[1], { target: { value: '15:00' } });

    fireEvent.click(screen.getByRole('button', { name: /add block/i }));

    expect(onChange).toHaveBeenCalledWith([{ start: '10:30', end: '15:00' }]);
  });

  it('resets inputs to default after adding', () => {
    render(<ConstraintForm blocks={[]} onChange={vi.fn()} />);

    const inputs = document.querySelectorAll('input[type="time"]') as NodeListOf<HTMLInputElement>;
    fireEvent.change(inputs[0], { target: { value: '10:30' } });
    fireEvent.change(inputs[1], { target: { value: '15:00' } });

    fireEvent.click(screen.getByRole('button', { name: /add block/i }));

    // Inputs should reset to defaults
    expect(inputs[0].value).toBe('09:00');
    expect(inputs[1].value).toBe('12:00');
  });

  it('does not show block list when empty', () => {
    render(<ConstraintForm blocks={[]} onChange={vi.fn()} />);

    // Should not find any list items
    expect(screen.queryByRole('listitem')).not.toBeInTheDocument();
  });

  it('appends to existing blocks when adding', () => {
    const onChange = vi.fn();
    const existingBlocks = [{ start: '09:00', end: '12:00' }];
    render(<ConstraintForm blocks={existingBlocks} onChange={onChange} />);

    // Change inputs to new values
    const inputs = document.querySelectorAll('input[type="time"]');
    fireEvent.change(inputs[0], { target: { value: '14:00' } });
    fireEvent.change(inputs[1], { target: { value: '17:00' } });

    fireEvent.click(screen.getByRole('button', { name: /add block/i }));

    expect(onChange).toHaveBeenCalledWith([
      { start: '09:00', end: '12:00' },
      { start: '14:00', end: '17:00' },
    ]);
  });
});

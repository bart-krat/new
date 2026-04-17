import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { UtilityWeights } from '../components/UtilityWeights';

describe('UtilityWeights', () => {
  const defaultWeights = { work: 0.4, personal: 0.3, health: 0.3 };

  const defaultProps = {
    weights: defaultWeights,
    onChange: vi.fn(),
  };

  it('renders heading and description', () => {
    render(<UtilityWeights {...defaultProps} />);
    expect(screen.getByRole('heading', { name: /category priorities/i })).toBeInTheDocument();
    expect(screen.getByText(/adjust sliders/i)).toBeInTheDocument();
  });

  it('renders all three category sliders', () => {
    render(<UtilityWeights {...defaultProps} />);
    expect(screen.getByText(/work:/i)).toBeInTheDocument();
    expect(screen.getByText(/personal:/i)).toBeInTheDocument();
    expect(screen.getByText(/health:/i)).toBeInTheDocument();
  });

  it('displays current weight values', () => {
    render(<UtilityWeights {...defaultProps} />);
    expect(screen.getByText(/work: 0.40/i)).toBeInTheDocument();
    expect(screen.getByText(/personal: 0.30/i)).toBeInTheDocument();
    expect(screen.getByText(/health: 0.30/i)).toBeInTheDocument();
  });

  it('displays total sum of weights', () => {
    render(<UtilityWeights {...defaultProps} />);
    expect(screen.getByText(/total: 1.00/i)).toBeInTheDocument();
  });

  it('shows valid indicator when sum equals 1', () => {
    const weights = { work: 0.5, personal: 0.3, health: 0.2 };
    render(<UtilityWeights weights={weights} onChange={vi.fn()} />);
    // Check mark should be visible
    expect(screen.getByText(/✓/)).toBeInTheDocument();
  });

  it('shows invalid indicator when sum not equal to 1', () => {
    const weights = { work: 0.5, personal: 0.5, health: 0.5 };
    render(<UtilityWeights weights={weights} onChange={vi.fn()} />);
    expect(screen.getByText(/should equal 1.0/i)).toBeInTheDocument();
  });

  it('calls onChange when work slider changes', () => {
    const onChange = vi.fn();
    render(<UtilityWeights weights={defaultWeights} onChange={onChange} />);

    const sliders = screen.getAllByRole('slider');
    fireEvent.change(sliders[0], { target: { value: '0.5' } });

    expect(onChange).toHaveBeenCalledWith({
      work: 0.5,
      personal: 0.3,
      health: 0.3,
    });
  });

  it('calls onChange when personal slider changes', () => {
    const onChange = vi.fn();
    render(<UtilityWeights weights={defaultWeights} onChange={onChange} />);

    const sliders = screen.getAllByRole('slider');
    fireEvent.change(sliders[1], { target: { value: '0.5' } });

    expect(onChange).toHaveBeenCalledWith({
      work: 0.4,
      personal: 0.5,
      health: 0.3,
    });
  });

  it('calls onChange when health slider changes', () => {
    const onChange = vi.fn();
    render(<UtilityWeights weights={defaultWeights} onChange={onChange} />);

    const sliders = screen.getAllByRole('slider');
    fireEvent.change(sliders[2], { target: { value: '0.5' } });

    expect(onChange).toHaveBeenCalledWith({
      work: 0.4,
      personal: 0.3,
      health: 0.5,
    });
  });

  it('sliders have correct min, max, and step attributes', () => {
    render(<UtilityWeights {...defaultProps} />);

    const sliders = screen.getAllByRole('slider');
    sliders.forEach((slider) => {
      expect(slider).toHaveAttribute('min', '0');
      expect(slider).toHaveAttribute('max', '1');
      expect(slider).toHaveAttribute('step', '0.05');
    });
  });

  it('sliders reflect current weight values', () => {
    const weights = { work: 0.6, personal: 0.25, health: 0.15 };
    render(<UtilityWeights weights={weights} onChange={vi.fn()} />);

    const sliders = screen.getAllByRole('slider') as HTMLInputElement[];
    expect(sliders[0].value).toBe('0.6');
    expect(sliders[1].value).toBe('0.25');
    expect(sliders[2].value).toBe('0.15');
  });

  it('handles zero weight values', () => {
    const weights = { work: 0, personal: 0.5, health: 0.5 };
    render(<UtilityWeights weights={weights} onChange={vi.fn()} />);

    expect(screen.getByText(/work: 0.00/i)).toBeInTheDocument();
  });

  it('handles weight values at maximum', () => {
    const weights = { work: 1, personal: 0, health: 0 };
    render(<UtilityWeights weights={weights} onChange={vi.fn()} />);

    expect(screen.getByText(/work: 1.00/i)).toBeInTheDocument();
    expect(screen.getByText(/✓/)).toBeInTheDocument();
  });

  it('calculates total correctly with floating point', () => {
    // Test floating point precision handling
    const weights = { work: 0.33, personal: 0.33, health: 0.34 };
    render(<UtilityWeights weights={weights} onChange={vi.fn()} />);

    expect(screen.getByText(/total: 1.00/i)).toBeInTheDocument();
  });
});

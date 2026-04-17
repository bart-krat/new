interface UtilityWeightsProps {
  weights: {
    work: number;
    personal: number;
    health: number;
  };
  onChange: (weights: { work: number; personal: number; health: number }) => void;
}

export function UtilityWeights({ weights, onChange }: UtilityWeightsProps) {
  const handleChange = (category: 'work' | 'personal' | 'health', value: number) => {
    onChange({ ...weights, [category]: value });
  };

  const total = weights.work + weights.personal + weights.health;
  const isValid = Math.abs(total - 1) < 0.01;

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <h3>Category Priorities</h3>
      <p style={{ fontSize: '0.9rem', color: '#666' }}>
        Adjust sliders to set priority for each category (should sum to 1.0)
      </p>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.25rem' }}>
          Work: {weights.work.toFixed(2)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={weights.work}
          onChange={(e) => handleChange('work', parseFloat(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.25rem' }}>
          Personal: {weights.personal.toFixed(2)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={weights.personal}
          onChange={(e) => handleChange('personal', parseFloat(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.25rem' }}>
          Health: {weights.health.toFixed(2)}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={weights.health}
          onChange={(e) => handleChange('health', parseFloat(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>

      <p style={{ color: isValid ? 'green' : 'red' }}>
        Total: {total.toFixed(2)} {isValid ? '✓' : '(should equal 1.0)'}
      </p>
    </div>
  );
}

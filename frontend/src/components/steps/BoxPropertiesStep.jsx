import React, { useState } from 'react';

const LAYER_LABELS = ['Bottom', 'Flute', 'Top'];

export default function BoxPropertiesStep({ formData, updateField, options }) {
  const qualityWeights = options.quality_weights || {};
  const qualities = options.paper_qualities || [];
  const customGsmQualities = options.custom_gsm_qualities || [];

  // Track which layers are using custom GSM input
  const [customGsm, setCustomGsm] = useState([false, false, false]);

  const handleQualityChange = (index, value) => {
    const updated = [...formData.paper_quality];
    updated[index] = value;
    updateField('paper_quality', updated);

    // Reset custom GSM mode when quality changes
    const newCustom = [...customGsm];
    newCustom[index] = false;
    setCustomGsm(newCustom);

    // Auto-select first available weight for new quality
    const weights = qualityWeights[value] || [];
    if (weights.length > 0) {
      const updatedWeights = [...formData.paper_weight];
      updatedWeights[index] = weights[0];
      updateField('paper_weight', updatedWeights);
    }
  };

  const handleWeightChange = (index, value) => {
    const updated = [...formData.paper_weight];
    updated[index] = Number(value);
    updateField('paper_weight', updated);
  };

  const toggleCustomGsm = (index) => {
    const newCustom = [...customGsm];
    newCustom[index] = !newCustom[index];
    setCustomGsm(newCustom);
  };

  return (
    <div className="step-content">
      <h2>Paper Properties</h2>
      <table className="properties-table">
        <thead>
          <tr>
            <th>Layer</th>
            <th>Paper Quality</th>
            <th>Paper Weight (GSM)</th>
          </tr>
        </thead>
        <tbody>
          {LAYER_LABELS.map((label, idx) => {
            const currentQuality = formData.paper_quality[idx];
            const availableWeights = qualityWeights[currentQuality] || [];
            const allowsCustom = idx === 2 && customGsmQualities.includes(currentQuality);
            const isCustom = customGsm[idx];

            return (
              <tr key={idx}>
                <td>{label}</td>
                <td>
                  <select
                    value={currentQuality}
                    onChange={(e) => handleQualityChange(idx, e.target.value)}
                  >
                    {qualities.map((q) => (
                      <option key={q} value={q}>{q}</option>
                    ))}
                  </select>
                </td>
                <td>
                  {isCustom ? (
                    <div className="custom-gsm-row">
                      <input
                        type="number"
                        min="1"
                        value={formData.paper_weight[idx]}
                        onChange={(e) => handleWeightChange(idx, e.target.value)}
                        placeholder="Enter GSM"
                      />
                      <button
                        type="button"
                        className="btn-sm"
                        onClick={() => toggleCustomGsm(idx)}
                        title="Switch back to dropdown"
                      >
                        List
                      </button>
                    </div>
                  ) : availableWeights.length > 1 || allowsCustom ? (
                    <div className="custom-gsm-row">
                      <select
                        value={formData.paper_weight[idx]}
                        onChange={(e) => handleWeightChange(idx, e.target.value)}
                      >
                        {availableWeights.map((w) => (
                          <option key={w} value={w}>{w === 0 ? 'N/A' : w}</option>
                        ))}
                      </select>
                      {allowsCustom && (
                        <button
                          type="button"
                          className="btn-sm"
                          onClick={() => toggleCustomGsm(idx)}
                          title="Enter custom GSM value"
                        >
                          Custom
                        </button>
                      )}
                    </div>
                  ) : (
                    <input
                      type="text"
                      value={availableWeights[0] === 0 ? 'N/A' : (availableWeights[0] || '')}
                      disabled
                    />
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

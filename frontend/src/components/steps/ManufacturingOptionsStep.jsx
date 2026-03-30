import React from 'react';

export default function ManufacturingOptionsStep({ formData, updateField }) {
  return (
    <div className="step-content">
      <h2>Manufacturing Options</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>Flute Type</label>
          <select
            value={formData.flute_type}
            onChange={(e) => updateField('flute_type', e.target.value)}
          >
            <option value="EF">EF (Standard)</option>
            <option value="NF">NF</option>
          </select>
        </div>

        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={formData.only_corrugation}
              onChange={(e) => updateField('only_corrugation', e.target.checked)}
            />
            Only Corrugation
          </label>
        </div>

        {!formData.only_corrugation && (
          <>
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.is_punching}
                  onChange={(e) => updateField('is_punching', e.target.checked)}
                />
                Punching
              </label>
            </div>

            {!formData.is_punching && (
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_scoring}
                    onChange={(e) => updateField('is_scoring', e.target.checked)}
                  />
                  Scoring
                </label>
              </div>
            )}

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.is_laminated}
                  onChange={(e) => updateField('is_laminated', e.target.checked)}
                />
                Lamination
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.is_printed}
                  onChange={(e) => updateField('is_printed', e.target.checked)}
                />
                Printed
              </label>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

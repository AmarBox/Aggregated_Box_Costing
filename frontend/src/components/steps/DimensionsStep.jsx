import React from 'react';

export default function DimensionsStep({ formData, updateField, options }) {
  if (formData.input_mode === 'box') {
    return (
      <div className="step-content">
        <h2>Box Dimensions</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Length</label>
            <input
              type="number"
              value={formData.box_length}
              onChange={(e) => updateField('box_length', e.target.value)}
              min="0"
              step="0.5"
            />
          </div>
          <div className="form-group">
            <label>Width</label>
            <input
              type="number"
              value={formData.box_width}
              onChange={(e) => updateField('box_width', e.target.value)}
              min="0"
              step="0.5"
            />
          </div>
          <div className="form-group">
            <label>Height</label>
            <input
              type="number"
              value={formData.box_height}
              onChange={(e) => updateField('box_height', e.target.value)}
              min="0"
              step="0.5"
            />
          </div>
          <div className="form-group">
            <label>Units</label>
            <select
              value={formData.units}
              onChange={(e) => updateField('units', e.target.value)}
            >
              {(options.units || ['cm', 'm', 'inch']).map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Box Type</label>
            <select
              value={formData.box_type}
              onChange={(e) => updateField('box_type', e.target.value)}
            >
              {(options.box_types || []).map((bt) => (
                <option key={bt} value={bt}>
                  {bt.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="step-content">
      <h2>Sheet Dimensions (inches)</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>Sheet Length</label>
          <input
            type="number"
            value={formData.sheet_length}
            onChange={(e) => updateField('sheet_length', e.target.value)}
            min="0"
            step="0.5"
          />
        </div>
        <div className="form-group">
          <label>Sheet Width</label>
          <input
            type="number"
            value={formData.sheet_width}
            onChange={(e) => updateField('sheet_width', e.target.value)}
            min="0"
            step="0.5"
          />
        </div>
      </div>
    </div>
  );
}

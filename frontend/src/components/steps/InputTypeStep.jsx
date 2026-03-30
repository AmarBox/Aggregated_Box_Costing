import React from 'react';

export default function InputTypeStep({ formData, updateField }) {
  return (
    <div className="step-content">
      <h2>Select Input Type</h2>
      <p>How would you like to specify your box dimensions?</p>
      <div className="radio-group">
        <label className={`radio-card ${formData.input_mode === 'box' ? 'selected' : ''}`}>
          <input
            type="radio"
            name="input_mode"
            value="box"
            checked={formData.input_mode === 'box'}
            onChange={() => updateField('input_mode', 'box')}
          />
          <div className="radio-card-content">
            <strong>Box Dimensions</strong>
            <span>Enter length, width, and height of the box</span>
          </div>
        </label>
        <label className={`radio-card ${formData.input_mode === 'sheet' ? 'selected' : ''}`}>
          <input
            type="radio"
            name="input_mode"
            value="sheet"
            checked={formData.input_mode === 'sheet'}
            onChange={() => updateField('input_mode', 'sheet')}
          />
          <div className="radio-card-content">
            <strong>Sheet Size</strong>
            <span>Enter sheet length and width directly (in inches)</span>
          </div>
        </label>
      </div>
    </div>
  );
}

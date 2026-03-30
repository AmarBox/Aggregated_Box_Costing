import React from 'react';

const STEP_LABELS = [
  'Input Type',
  'Dimensions',
  'Box Properties',
  'Production',
  'Manufacturing',
  'Results',
];

export default function Stepper({ currentStep, onStepClick }) {
  return (
    <div className="stepper">
      {STEP_LABELS.map((label, idx) => (
        <div
          key={idx}
          className={`stepper-item ${idx === currentStep ? 'active' : ''} ${idx < currentStep ? 'completed' : ''}`}
          onClick={() => idx < currentStep && onStepClick(idx)}
        >
          <div className="stepper-circle">{idx < currentStep ? '✓' : idx + 1}</div>
          <div className="stepper-label">{label}</div>
        </div>
      ))}
    </div>
  );
}

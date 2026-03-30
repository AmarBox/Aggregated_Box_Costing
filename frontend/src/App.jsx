import React, { useState, useEffect } from 'react';
import Stepper from './components/Stepper';
import InputTypeStep from './components/steps/InputTypeStep';
import DimensionsStep from './components/steps/DimensionsStep';
import BoxPropertiesStep from './components/steps/BoxPropertiesStep';
import ProductionDetailsStep from './components/steps/ProductionDetailsStep';
import ManufacturingOptionsStep from './components/steps/ManufacturingOptionsStep';
import ResultsStep from './components/steps/ResultsStep';
import AdminPage from './components/AdminPage';
import { fetchOptions, calculateCost } from './api/calculatorApi';

const INITIAL_FORM = {
  input_mode: 'box',
  // Box dimensions
  box_length: 23,
  box_width: 17,
  box_height: 6,
  units: 'cm',
  box_type: 'universal',
  // Sheet dimensions
  sheet_length: 26,
  sheet_width: 18,
  // Paper properties
  paper_quality: ['KRAFT', 'KRAFT', 'PREPRINTED'],
  paper_weight: [100, 100, 0],
  // Production details
  ply_num: 3,
  box_per_sheet: 1,
  number_of_boxes: 10000,
  attachment_type: 'pinning',
  pins_per_box: 6,
  // Manufacturing options
  flute_type: 'EF',
  is_punching: true,
  is_scoring: false,
  is_laminated: false,
  is_printed: false,
  only_corrugation: false,
  cost_date: '',  // empty = use latest month's material costs
};

export default function App() {
  const [page, setPage] = useState('calculator'); // 'calculator' | 'admin'
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState(INITIAL_FORM);
  const [options, setOptions] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOptions()
      .then(setOptions)
      .catch((err) => console.error('Failed to load options:', err));
  }, []);

  const updateField = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const buildPayload = () => {
    const payload = {
      input_mode: formData.input_mode,
      paper_weight: formData.paper_weight,
      paper_quality: formData.paper_quality,
      ply_num: formData.ply_num,
      box_per_sheet: formData.box_per_sheet,
      number_of_boxes: formData.number_of_boxes,
      attachment_type: formData.attachment_type,
      pins_per_box: formData.pins_per_box,
      flute_type: formData.flute_type,
      is_punching: formData.is_punching,
      is_scoring: formData.is_scoring,
      is_laminated: formData.is_laminated,
      is_printed: formData.is_printed,
      only_corrugation: formData.only_corrugation,
      cost_date: formData.cost_date || undefined,
    };

    if (formData.input_mode === 'box') {
      payload.box_dimensions = {
        length: parseFloat(formData.box_length),
        width: parseFloat(formData.box_width),
        height: parseFloat(formData.box_height),
        units: formData.units,
        box_type: formData.box_type,
      };
    } else {
      payload.sheet_dimensions = {
        length: parseFloat(formData.sheet_length),
        width: parseFloat(formData.sheet_width),
      };
    }

    return payload;
  };

  const handleNext = async () => {
    if (step < 4) {
      setStep(step + 1);
    } else if (step === 4) {
      // Moving to results — trigger calculation
      setStep(5);
      setLoading(true);
      setError(null);
      try {
        const data = await calculateCost(buildPayload());
        setResults(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const handleReset = () => {
    setFormData(INITIAL_FORM);
    setResults(null);
    setError(null);
    setStep(0);
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return <InputTypeStep formData={formData} updateField={updateField} />;
      case 1:
        return <DimensionsStep formData={formData} updateField={updateField} options={options} />;
      case 2:
        return <BoxPropertiesStep formData={formData} updateField={updateField} options={options} />;
      case 3:
        return <ProductionDetailsStep formData={formData} updateField={updateField} />;
      case 4:
        return <ManufacturingOptionsStep formData={formData} updateField={updateField} />;
      case 5:
        return <ResultsStep results={results} loading={loading} error={error} />;
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Corrugated Box Costing</h1>
        <nav className="app-nav">
          <button
            className={`nav-tab ${page === 'calculator' ? 'active' : ''}`}
            onClick={() => setPage('calculator')}
          >
            Calculator
          </button>
          <button
            className={`nav-tab ${page === 'admin' ? 'active' : ''}`}
            onClick={() => setPage('admin')}
          >
            Admin Console
          </button>
        </nav>
      </header>

      {page === 'calculator' ? (
        <>
          <Stepper currentStep={step} onStepClick={setStep} />
          <main className="app-main">
            {renderStep()}
            <div className="nav-buttons">
              {step > 0 && step < 5 && (
                <button className="btn btn-secondary" onClick={handleBack}>
                  Back
                </button>
              )}
              {step < 5 && (
                <button className="btn btn-primary" onClick={handleNext}>
                  {step === 4 ? 'Calculate' : 'Next'}
                </button>
              )}
              {step === 5 && (
                <button className="btn btn-secondary" onClick={handleReset}>
                  Start Over
                </button>
              )}
            </div>
          </main>
        </>
      ) : (
        <main className="app-main">
          <AdminPage />
        </main>
      )}
    </div>
  );
}

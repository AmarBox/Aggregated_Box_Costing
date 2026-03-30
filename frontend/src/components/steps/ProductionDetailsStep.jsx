import React from 'react';

export default function ProductionDetailsStep({ formData, updateField }) {
  return (
    <div className="step-content">
      <h2>Production Details</h2>
      <div className="form-grid">
        <div className="form-group">
          <label>Number of Plies</label>
          <select
            value={formData.ply_num}
            onChange={(e) => updateField('ply_num', Number(e.target.value))}
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={7}>7</option>
          </select>
        </div>
        <div className="form-group">
          <label>Boxes per Sheet</label>
          <input
            type="number"
            value={formData.box_per_sheet}
            onChange={(e) => updateField('box_per_sheet', Number(e.target.value))}
            min="1"
          />
        </div>
        <div className="form-group">
          <label>Number of Boxes</label>
          <input
            type="number"
            value={formData.number_of_boxes}
            onChange={(e) => updateField('number_of_boxes', Number(e.target.value))}
            min="1"
            step="100"
          />
        </div>
        <div className="form-group">
          <label>Attachment Type</label>
          <select
            value={formData.attachment_type}
            onChange={(e) => updateField('attachment_type', e.target.value)}
          >
            <option value="none">None</option>
            <option value="pinning">Pinning</option>
            <option value="hand_pasting">Hand Pasting</option>
          </select>
        </div>
        {formData.attachment_type === 'pinning' && (
          <div className="form-group">
            <label>Pins per Box</label>
            <input
              type="number"
              value={formData.pins_per_box}
              onChange={(e) => updateField('pins_per_box', Number(e.target.value))}
              min="0"
            />
          </div>
        )}
        <div className="form-group">
          <label>Cost Date (optional)</label>
          <input
            type="month"
            value={formData.cost_date}
            onChange={(e) => updateField('cost_date', e.target.value)}
          />
          <small className="form-hint">
            Leave empty to use latest material costs
          </small>
        </div>
      </div>
    </div>
  );
}

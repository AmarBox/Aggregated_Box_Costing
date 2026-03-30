import React from 'react';

export default function ResultsStep({ results, loading, error }) {
  if (loading) {
    return (
      <div className="step-content">
        <h2>Calculating...</h2>
        <div className="loading-spinner" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="step-content">
        <h2>Error</h2>
        <p className="error-message">{error}</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="step-content">
        <h2>Results</h2>
        <p>No results yet.</p>
      </div>
    );
  }

  const { sheet_size, sheet_weight, cost_breakdown, manufacturing_cost_per_box, sales_prices, material_costs_used, cost_date } = results;

  return (
    <div className="step-content results-step">
      <h2>Cost Breakdown</h2>

      {material_costs_used && (
        <div className="results-section">
          <h3>Material Costs Used {cost_date ? `(${cost_date})` : '(Latest)'}</h3>
          <table className="results-table">
            <thead>
              <tr><th>Paper Quality</th><th>Cost (INR/kg)</th></tr>
            </thead>
            <tbody>
              {Object.entries(material_costs_used).map(([quality, cost]) => (
                <tr key={quality}>
                  <td>{quality}</td>
                  <td>{cost > 0 ? `₹ ${cost}` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="results-section">
        <h3>Sheet Details</h3>
        <table className="results-table">
          <tbody>
            <tr><td>Sheet Size</td><td>{sheet_size.length}" x {sheet_size.width}"</td></tr>
            <tr><td>Sheet Area</td><td>{sheet_size.area} sq in</td></tr>
            <tr><td>Backing Weight</td><td>{sheet_weight.backing} kg</td></tr>
            <tr><td>Fluting Weight</td><td>{sheet_weight.fluting} kg</td></tr>
            <tr><td>Top Weight</td><td>{sheet_weight.top} kg</td></tr>
            <tr><td><strong>Total Weight</strong></td><td><strong>{sheet_weight.total} kg</strong></td></tr>
          </tbody>
        </table>
      </div>

      <div className="results-section">
        <h3>Cost Components (per sheet)</h3>
        <table className="results-table">
          <tbody>
            {Object.entries(cost_breakdown).map(([key, value]) => (
              <tr key={key}>
                <td>{key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</td>
                <td>₹ {value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="results-section highlight">
        <h3>Manufacturing Cost per Box</h3>
        <div className="big-number">₹ {manufacturing_cost_per_box}</div>
      </div>

      <div className="results-section">
        <h3>Sales Prices</h3>
        <table className="results-table sales-table">
          <thead>
            <tr>
              <th>Margin</th>
              <th>Price</th>
              <th>With Legacy Tax (12%)</th>
              <th>With New Tax (5%)</th>
            </tr>
          </thead>
          <tbody>
            {sales_prices.map((sp) => (
              <tr key={sp.margin_pct}>
                <td>{sp.margin_pct}%</td>
                <td>₹ {sp.price}</td>
                <td>₹ {sp.with_legacy_tax}</td>
                <td>₹ {sp.with_new_tax}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

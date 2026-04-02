import React, { useState, useEffect, useRef } from 'react';
import {
  fetchMaterialCosts,
  updateMaterialCosts,
  uploadFile,
  batchProcess,
  downloadUrl,
  fetchInventory,
  addInventoryReel,
  updateInventoryReel,
  deleteInventoryReel,
} from '../api/calculatorApi';

// ─── Paper type display order ───
const PAPER_TYPES = ['KRAFT', 'GOLDEN', 'DUPLEX', 'ITC', 'PREPRINTED'];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('costs');

  return (
    <div className="admin-page">
      <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'costs' ? 'active' : ''}`}
          onClick={() => setActiveTab('costs')}
        >
          Material Costs
        </button>
        <button
          className={`admin-tab ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => setActiveTab('inventory')}
        >
          Inventory
        </button>
        <button
          className={`admin-tab ${activeTab === 'batch' ? 'active' : ''}`}
          onClick={() => setActiveTab('batch')}
        >
          Batch Processing
        </button>
      </div>

      {activeTab === 'costs' && <MaterialCostsSection />}
      {activeTab === 'inventory' && <InventorySection />}
      {activeTab === 'batch' && <BatchSection />}
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════
// Material Costs Section — inline editable table
// ═══════════════════════════════════════════════════════════════════════

function MaterialCostsSection() {
  const [costs, setCosts] = useState({});
  const [editMonth, setEditMonth] = useState(null);
  const [editCosts, setEditCosts] = useState({});
  const [costMsg, setCostMsg] = useState('');
  const [isNew, setIsNew] = useState(false);
  const [newMonthKey, setNewMonthKey] = useState('');

  useEffect(() => { loadCosts(); }, []);

  async function loadCosts() {
    try {
      const data = await fetchMaterialCosts();
      setCosts(data);
    } catch (e) {
      setCostMsg('Failed to load costs: ' + e.message);
    }
  }

  // Get quality keys from first month, or use default list
  const qualities = Object.keys(Object.values(costs)[0] || {});

  function startEdit(month) {
    setEditMonth(month);
    setEditCosts({ ...costs[month] });
    setIsNew(false);
    setNewMonthKey('');
    setCostMsg('');
  }

  function startNewMonth() {
    const now = new Date();
    const key = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    const months = Object.keys(costs).sort().reverse();
    setEditMonth('__new__');
    setNewMonthKey(key);
    setEditCosts(months.length > 0 ? { ...costs[months[0]] } : {});
    setIsNew(true);
    setCostMsg('');
  }

  function cancelEdit() {
    setEditMonth(null);
    setEditCosts({});
    setIsNew(false);
    setNewMonthKey('');
  }

  async function saveCosts() {
    const monthKey = isNew ? newMonthKey : editMonth;
    if (!monthKey) { setCostMsg('Month is required'); return; }
    try {
      await updateMaterialCosts(monthKey, editCosts);
      setCostMsg(`Saved costs for ${monthKey}`);
      cancelEdit();
      loadCosts();
    } catch (e) {
      setCostMsg('Error: ' + e.message);
    }
  }

  return (
    <section className="admin-section">
      <h2>Monthly Material Costs</h2>
      <p className="admin-hint">
        Raw material costs (INR/kg) used for calculations. Click Edit to modify a month's costs inline.
      </p>

      {costMsg && <p className="admin-msg">{costMsg}</p>}

      <div className="costs-table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>Month</th>
              {qualities.map((q) => <th key={q}>{q}</th>)}
              <th></th>
            </tr>
          </thead>
          <tbody>
            {/* New month row at top when adding */}
            {isNew && (
              <tr className="edit-row">
                <td>
                  <input
                    type="month"
                    value={newMonthKey}
                    onChange={(e) => setNewMonthKey(e.target.value)}
                    className="inline-input month-input"
                  />
                </td>
                {qualities.map((q) => (
                  <td key={q}>
                    <input
                      type="number"
                      step="0.5"
                      value={editCosts[q] ?? ''}
                      onChange={(e) =>
                        setEditCosts((prev) => ({ ...prev, [q]: parseFloat(e.target.value) || 0 }))
                      }
                      className="inline-input"
                    />
                  </td>
                ))}
                <td>
                  <div className="inline-actions">
                    <button className="btn-sm btn-save" onClick={saveCosts}>Save</button>
                    <button className="btn-sm" onClick={cancelEdit}>Cancel</button>
                  </div>
                </td>
              </tr>
            )}

            {Object.entries(costs).map(([month, vals]) => (
              <tr key={month} className={editMonth === month ? 'edit-row' : ''}>
                <td><strong>{month}</strong></td>
                {qualities.map((q) => (
                  <td key={q}>
                    {editMonth === month ? (
                      <input
                        type="number"
                        step="0.5"
                        value={editCosts[q] ?? ''}
                        onChange={(e) =>
                          setEditCosts((prev) => ({ ...prev, [q]: parseFloat(e.target.value) || 0 }))
                        }
                        className="inline-input"
                      />
                    ) : (
                      vals[q]
                    )}
                  </td>
                ))}
                <td>
                  {editMonth === month ? (
                    <div className="inline-actions">
                      <button className="btn-sm btn-save" onClick={saveCosts}>Save</button>
                      <button className="btn-sm" onClick={cancelEdit}>Cancel</button>
                    </div>
                  ) : (
                    <button
                      className="btn-sm"
                      onClick={() => startEdit(month)}
                      disabled={editMonth !== null}
                    >
                      Edit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        className="btn btn-secondary"
        onClick={startNewMonth}
        disabled={editMonth !== null}
        style={{ marginTop: 12 }}
      >
        + Add Month
      </button>
    </section>
  );
}


// ═══════════════════════════════════════════════════════════════════════
// Inventory Section — paper reel tracking
// ═══════════════════════════════════════════════════════════════════════

function InventorySection() {
  const [reels, setReels] = useState([]);
  const [msg, setMsg] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editData, setEditData] = useState({});
  const [newReel, setNewReel] = useState({
    type: 'KRAFT', gsm: '', deckel: '', weight: '', count: 1,
  });

  useEffect(() => { loadReels(); }, []);

  async function loadReels() {
    try {
      const data = await fetchInventory();
      setReels(data);
    } catch (e) {
      setMsg('Failed to load inventory: ' + e.message);
    }
  }

  async function handleAdd() {
    if (!newReel.gsm || !newReel.deckel || !newReel.weight) {
      setMsg('Please fill in all fields');
      return;
    }
    try {
      await addInventoryReel(newReel);
      setMsg(`Added ${newReel.count || 1} reel(s)`);
      setNewReel({ type: 'KRAFT', gsm: '', deckel: '', weight: '', count: 1 });
      setShowAdd(false);
      loadReels();
    } catch (e) {
      setMsg('Error: ' + e.message);
    }
  }

  function startEditReel(reel) {
    setEditId(reel.id);
    setEditData({ type: reel.type, gsm: reel.gsm, deckel: reel.deckel, weight: reel.weight });
    setMsg('');
  }

  async function saveEditReel() {
    try {
      await updateInventoryReel(editId, editData);
      setEditId(null);
      setEditData({});
      setMsg('Reel updated');
      loadReels();
    } catch (e) {
      setMsg('Error: ' + e.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this reel?')) return;
    try {
      await deleteInventoryReel(id);
      setMsg('Reel deleted');
      loadReels();
    } catch (e) {
      setMsg('Error: ' + e.message);
    }
  }

  // Group reels by type for display
  const grouped = {};
  reels.forEach((r) => {
    if (!grouped[r.type]) grouped[r.type] = [];
    grouped[r.type].push(r);
  });

  return (
    <section className="admin-section">
      <h2>Paper Reel Inventory</h2>
      <p className="admin-hint">
        Track individual paper reels. Organized by type, then grammage (GSM), then deckel (inches).
      </p>

      {msg && <p className="admin-msg">{msg}</p>}

      <button
        className="btn btn-primary"
        onClick={() => { setShowAdd(!showAdd); setMsg(''); }}
        style={{ marginBottom: 16 }}
      >
        {showAdd ? 'Cancel' : '+ Add Reel'}
      </button>

      {showAdd && (
        <div className="edit-panel" style={{ marginBottom: 16 }}>
          <h3>Add New Reel</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Paper Type</label>
              <select
                value={newReel.type}
                onChange={(e) => setNewReel({ ...newReel, type: e.target.value })}
              >
                {PAPER_TYPES.filter(t => t !== 'PREPRINTED').map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>GSM (Grammage)</label>
              <input
                type="number"
                value={newReel.gsm}
                onChange={(e) => setNewReel({ ...newReel, gsm: e.target.value })}
                placeholder="e.g. 100"
              />
            </div>
            <div className="form-group">
              <label>Deckel (inches)</label>
              <input
                type="number"
                step="0.5"
                value={newReel.deckel}
                onChange={(e) => setNewReel({ ...newReel, deckel: e.target.value })}
                placeholder="e.g. 36"
              />
            </div>
            <div className="form-group">
              <label>Weight (kg)</label>
              <input
                type="number"
                step="0.1"
                value={newReel.weight}
                onChange={(e) => setNewReel({ ...newReel, weight: e.target.value })}
                placeholder="e.g. 500"
              />
            </div>
            <div className="form-group">
              <label>Count (identical reels)</label>
              <input
                type="number"
                min="1"
                value={newReel.count}
                onChange={(e) => setNewReel({ ...newReel, count: parseInt(e.target.value) || 1 })}
              />
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleAdd} style={{ marginTop: 12 }}>
            Add Reel{newReel.count > 1 ? 's' : ''}
          </button>
        </div>
      )}

      {PAPER_TYPES.filter(t => t !== 'PREPRINTED' && grouped[t]).map((type) => (
        <div key={type} className="inventory-group">
          <h3 className="inventory-type-header">{type}</h3>
          <table className="results-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>GSM</th>
                <th>Deckel (in)</th>
                <th>Weight (kg)</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {grouped[type].map((reel) => (
                <tr key={reel.id} className={editId === reel.id ? 'edit-row' : ''}>
                  <td>{reel.id}</td>
                  <td>
                    {editId === reel.id ? (
                      <input
                        type="number"
                        value={editData.gsm}
                        onChange={(e) => setEditData({ ...editData, gsm: parseInt(e.target.value) || 0 })}
                        className="inline-input"
                      />
                    ) : reel.gsm}
                  </td>
                  <td>
                    {editId === reel.id ? (
                      <input
                        type="number"
                        step="0.5"
                        value={editData.deckel}
                        onChange={(e) => setEditData({ ...editData, deckel: parseFloat(e.target.value) || 0 })}
                        className="inline-input"
                      />
                    ) : reel.deckel}
                  </td>
                  <td>
                    {editId === reel.id ? (
                      <input
                        type="number"
                        step="0.1"
                        value={editData.weight}
                        onChange={(e) => setEditData({ ...editData, weight: parseFloat(e.target.value) || 0 })}
                        className="inline-input"
                      />
                    ) : reel.weight}
                  </td>
                  <td>
                    {editId === reel.id ? (
                      <div className="inline-actions">
                        <button className="btn-sm btn-save" onClick={saveEditReel}>Save</button>
                        <button className="btn-sm" onClick={() => setEditId(null)}>Cancel</button>
                      </div>
                    ) : (
                      <div className="inline-actions">
                        <button className="btn-sm" onClick={() => startEditReel(reel)}>Edit</button>
                        <button className="btn-sm btn-danger" onClick={() => handleDelete(reel.id)}>Delete</button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {reels.length === 0 && (
        <p style={{ color: '#888', marginTop: 16 }}>No reels in inventory. Click "+ Add Reel" to get started.</p>
      )}
    </section>
  );
}


// ═══════════════════════════════════════════════════════════════════════
// Batch Processing Section
// ═══════════════════════════════════════════════════════════════════════

function BatchSection() {
  const [rawWorkFile, setRawWorkFile] = useState(null);
  const [estimatesFile, setEstimatesFile] = useState(null);
  const [batchStatus, setBatchStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [transferMode, setTransferMode] = useState('fresh');

  const rawRef = useRef();
  const estRef = useRef();

  async function handleUploadRaw() {
    if (!rawWorkFile) return;
    setLoading(true);
    setBatchStatus('');
    try {
      const res = await uploadFile('/upload/raw-work', rawWorkFile);
      setBatchStatus(res.message);
    } catch (e) {
      setBatchStatus('Upload error: ' + e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUploadEstimates() {
    if (!estimatesFile) return;
    setLoading(true);
    setBatchStatus('');
    try {
      const res = await uploadFile('/upload/estimates', estimatesFile);
      setBatchStatus(res.message);
    } catch (e) {
      setBatchStatus('Upload error: ' + e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleProcess() {
    setLoading(true);
    setBatchStatus('Processing...');
    try {
      const res = await batchProcess(transferMode);
      setBatchStatus(`Processed ${res.rows_processed} rows, transferred ${res.transferred} to Estimates.`);
    } catch (e) {
      setBatchStatus('Process error: ' + e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="admin-section">
      <h2>Batch Processing</h2>
      <p className="admin-hint">
        Upload a Raw_Work.xlsx file, then process to calculate costs and generate the Estimates file for download.
      </p>

      <div className="upload-row">
        <div className="upload-group">
          <label>Raw_Work.xlsx</label>
          <input
            ref={rawRef}
            type="file"
            accept=".xlsx"
            onChange={(e) => setRawWorkFile(e.target.files[0])}
          />
          <button className="btn btn-secondary" onClick={handleUploadRaw} disabled={!rawWorkFile || loading}>
            Upload
          </button>
        </div>
        <div className="upload-group">
          <label>Estimates.xlsx (for Append mode)</label>
          <input
            ref={estRef}
            type="file"
            accept=".xlsx"
            onChange={(e) => setEstimatesFile(e.target.files[0])}
          />
          <button className="btn btn-secondary" onClick={handleUploadEstimates} disabled={!estimatesFile || loading}>
            Upload
          </button>
        </div>
      </div>

      <div className="transfer-section">
        <div className="transfer-controls">
          <div className="segment-toggle">
            <button
              className={`segment-btn ${transferMode === 'fresh' ? 'active' : ''}`}
              onClick={() => setTransferMode('fresh')}
            >
              Fresh
            </button>
            <button
              className={`segment-btn ${transferMode === 'append' ? 'active' : ''}`}
              onClick={() => setTransferMode('append')}
            >
              Append
            </button>
          </div>
          <button className="btn btn-primary" onClick={handleProcess} disabled={loading}>
            Process & Generate Estimates
          </button>
        </div>
        <p className="transfer-hint">
          {transferMode === 'fresh'
            ? 'Creates a new Estimates file — previous data will not be included'
            : 'Adds to the existing Estimates file — upload one above or uses the last generated file'}
        </p>
      </div>

      {batchStatus && <p className="admin-msg">{batchStatus}</p>}

      <div className="download-row">
        <h3>Download Files</h3>
        <a className="btn btn-secondary" href={downloadUrl('template')} download>
          Empty Template
        </a>
        <a className="btn btn-secondary" href={downloadUrl('raw-work')} download>
          Raw_Work.xlsx
        </a>
        <a className="btn btn-secondary" href={downloadUrl('estimates')} download>
          Estimates.xlsx
        </a>
      </div>
    </section>
  );
}

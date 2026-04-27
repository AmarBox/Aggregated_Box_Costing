import React, { useState, useRef } from 'react';
import {
  uploadFile,
  batchProcess,
  downloadUrl,
} from '../api/calculatorApi';

export default function BatchProcessingPage() {
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

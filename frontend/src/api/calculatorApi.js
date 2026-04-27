const BASE = '/api';

export async function fetchOptions() {
  const res = await fetch(`${BASE}/options`);
  if (!res.ok) throw new Error('Failed to fetch options');
  return res.json();
}

export async function calculateSheetSize(boxData) {
  const res = await fetch(`${BASE}/sheet-size`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(boxData),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Sheet size calculation failed');
  return data;
}

export async function calculateCost(payload) {
  const res = await fetch(`${BASE}/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Cost calculation failed');
  return data;
}

// --- Batch processing ---

export async function uploadFile(endpoint, file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE}${endpoint}`, { method: 'POST', body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Upload failed');
  return data;
}

export async function batchProcess(mode = 'fresh') {
  const res = await fetch(`${BASE}/batch/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Processing failed');
  return data;
}

export function downloadUrl(filename) {
  return `${BASE}/download/${filename}`;
}


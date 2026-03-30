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

// --- Material costs ---

export async function fetchMaterialCosts() {
  const res = await fetch(`${BASE}/material-costs`);
  if (!res.ok) throw new Error('Failed to fetch material costs');
  return res.json();
}

export async function updateMaterialCosts(month, costs) {
  const res = await fetch(`${BASE}/material-costs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ month, costs }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to update costs');
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

export async function batchProcess() {
  const res = await fetch(`${BASE}/batch/process`, { method: 'POST' });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Processing failed');
  return data;
}

export async function batchTransfer() {
  const res = await fetch(`${BASE}/batch/transfer`, { method: 'POST' });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Transfer failed');
  return data;
}

export function downloadUrl(filename) {
  return `${BASE}/download/${filename}`;
}

// --- Inventory ---

export async function fetchInventory() {
  const res = await fetch(`${BASE}/inventory`);
  if (!res.ok) throw new Error('Failed to fetch inventory');
  return res.json();
}

export async function fetchInventorySummary() {
  const res = await fetch(`${BASE}/inventory/summary`);
  if (!res.ok) throw new Error('Failed to fetch inventory summary');
  return res.json();
}

export async function addInventoryReel(reel) {
  const res = await fetch(`${BASE}/inventory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reel),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to add reel');
  return data;
}

export async function updateInventoryReel(reelId, updates) {
  const res = await fetch(`${BASE}/inventory/${reelId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to update reel');
  return data;
}

export async function deleteInventoryReel(reelId) {
  const res = await fetch(`${BASE}/inventory/${reelId}`, { method: 'DELETE' });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to delete reel');
  return data;
}

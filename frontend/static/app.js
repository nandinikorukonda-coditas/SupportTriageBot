const BASE = window.__env?.API_URL || 'http://localhost:8000';

async function $(id){return document.getElementById(id)}

async function loadCorpus(){
  const el = await $('corpus-list');
  el.innerText = 'Loading...';
  try{
    const res = await fetch(`${BASE}/tickets`);
    const data = await res.json();
    el.innerHTML = data.map(t => `<div class="ticket-item"><strong>${t.id}</strong> [${t.category}] - ${t.text}</div>`).join('\n');
  }catch(e){ el.innerText = 'Error loading corpus: '+e }
}

async function ingest(){
  try{
    const res = await fetch(`${BASE}/ingest`, {method:'POST'});
    const j = await res.json();
    alert('Ingested: '+j.indexed);
    await loadCorpus();
  }catch(e){ alert('Ingest failed: '+e) }
}

async function submitText(){
  const text = (await $('ticket-text')).value.trim();
  if(!text){ alert('Enter text'); return }
  (await $('processing')).classList.remove('hidden');
  try{
    const form = new FormData(); form.append('text', text);
    const res = await fetch(`${BASE}/submit`, {method:'POST', body: form});
    const j = await res.json();
    displayResult(j);
  }catch(e){ alert('Submit failed: '+e) }
  (await $('processing')).classList.add('hidden');
}

async function submitVoice(){
  const file = (await $('voice-file')).files[0];
  if(!file){ alert('Select a voice file'); return }
  (await $('processing')).classList.remove('hidden');
  try{
    const form = new FormData(); form.append('file', file);
    const res = await fetch(`${BASE}/submit-voice`, {method:'POST', body: form});
    const j = await res.json();
    displayResult(j);
  }catch(e){ alert('Voice submit failed: '+e) }
  (await $('processing')).classList.add('hidden');
}

function displayResult(j){
  const out = document.getElementById('result-output');
  out.innerText = JSON.stringify(j, null, 2);
  const traceEl = document.getElementById('agent-trace');
  // Build a simple trace view from returned fields
  const parts = [];
  parts.push(`<div><strong>Category:</strong> ${j.category || 'N/A'}</div>`);
  parts.push(`<div><strong>Confidence:</strong> ${j.confidence ?? 'N/A'}</div>`);
  parts.push(`<div><strong>Similar tickets:</strong> ${(j.similar_ticket_ids||[]).join(', ')}</div>`);
  parts.push(`<div><strong>Timing (ms):</strong> ${j.timing_ms ?? 'N/A'}</div>`);
  traceEl.innerHTML = parts.join('');
}

function init(){
  document.getElementById('btn-ingest').addEventListener('click', ingest);
  document.getElementById('btn-refresh').addEventListener('click', loadCorpus);
  document.getElementById('btn-submit').addEventListener('click', submitText);
  document.getElementById('btn-submit-voice').addEventListener('click', submitVoice);
  loadCorpus();
}

window.addEventListener('load', init);

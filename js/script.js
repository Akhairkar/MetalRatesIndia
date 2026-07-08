/* =========================================================
   Metal Rates India — core app logic
   Works from any page depth via the global DATA_ROOT variable
   set in each page's inline script before this file loads.
   ========================================================= */

const ROOT = window.DATA_ROOT || './';

/* ---------------- Theme ---------------- */
(function initTheme(){
  const saved = localStorage.getItem('mri-theme');
  const theme = saved || 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('themeToggle');
    if(!btn) return;
    btn.textContent = theme === 'light' ? '☀️' : '🌙';
    btn.addEventListener('click', () => {
      const cur = document.documentElement.getAttribute('data-theme');
      const next = cur === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('mri-theme', next);
      btn.textContent = next === 'light' ? '☀️' : '🌙';
    });
  });
})();

/* ---------------- Mobile nav ---------------- */
document.addEventListener('DOMContentLoaded', () => {
  const burger = document.getElementById('hamburger');
  const nav = document.getElementById('mainNav');
  if(burger && nav){
    burger.addEventListener('click', () => nav.classList.toggle('open'));
  }
});

/* ---------------- Search ---------------- */
let SEARCH_INDEX = null;

async function loadSearchIndex(){
  if(SEARCH_INDEX) return SEARCH_INDEX;
  try{
    const res = await fetch(ROOT + 'data/metals.json');
    const json = await res.json();
    const items = Object.values(json.metals).map(m => ({
      id: m.id, name: m.name, nameHi: m.nameHi, symbol: m.symbol, color: m.color,
      url: `${ROOT}pages/${m.id}-rate-today.html`,
      keywords: `${m.name} ${m.nameHi} ${m.id} ${m.name} scrap rate price today ${m.symbol}`.toLowerCase()
    }));
    items.push(
      { id:'gold', name:'Gold', nameHi:'सोना', symbol:'AU', color:'#d4af37', url: ROOT+'pages/gold-silver-rate-today.html', keywords:'gold sona rate price today 24k 22k 18k' },
      { id:'silver', name:'Silver', nameHi:'चांदी', symbol:'AG', color:'#c7c9cc', url: ROOT+'pages/gold-silver-rate-today.html', keywords:'silver chandi rate price today 999 925' }
    );
    SEARCH_INDEX = items;
    return items;
  }catch(e){ console.error('search index load failed', e); return []; }
}

document.addEventListener('DOMContentLoaded', () => {
  const openBtn = document.getElementById('searchOpenBtn');
  const overlay = document.getElementById('searchOverlay');
  const input = document.getElementById('searchInput');
  const results = document.getElementById('searchResults');
  if(!openBtn || !overlay) return;

  const open = async () => {
    overlay.classList.add('open');
    input.value = '';
    results.innerHTML = '';
    input.focus();
    await loadSearchIndex();
  };
  const close = () => overlay.classList.remove('open');

  openBtn.addEventListener('click', open);
  overlay.addEventListener('click', (e) => { if(e.target === overlay) close(); });
  document.addEventListener('keydown', (e) => {
    if((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)){ e.preventDefault(); open(); }
    if(e.key === 'Escape') close();
  });

  input && input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if(!q){ results.innerHTML = ''; return; }
    const matches = (SEARCH_INDEX || []).filter(i => i.keywords.includes(q)).slice(0, 8);
    if(!matches.length){
      results.innerHTML = `<div class="search-empty">No results for "${escapeHtml(input.value)}"</div>`;
      return;
    }
    results.innerHTML = matches.map(m => `
      <a href="${m.url}">
        <span class="swatch" style="background:${m.color}"></span>
        <span>${m.name} <span style="color:var(--text-faint)">· ${m.nameHi}</span></span>
      </a>`).join('');
  });
});

function escapeHtml(s){
  return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

/* ---------------- FAQ accordion ---------------- */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.faq-item .faq-q').forEach(q => {
    q.addEventListener('click', () => q.closest('.faq-item').classList.toggle('open'));
  });
});

/* ---------------- Formatting helpers ---------------- */
function fmtINR(n){
  return Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function fmtDate(iso){
  const d = new Date(iso);
  return d.toLocaleString('en-IN', { day:'2-digit', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' });
}
function changeSpan(change, pct){
  const cls = change >= 0 ? 'up' : 'down';
  const arrow = change >= 0 ? '▲' : '▼';
  return `<span class="${cls}">${arrow} ${Math.abs(pct).toFixed(2)}% (₹${Math.abs(change).toFixed(2)})</span>`;
}

/* ---------------- Homepage: ticker + cards + gold/silver ---------------- */
async function initHomepage(){
  const tickerTrack = document.getElementById('tickerTrack');
  const metalGrid = document.getElementById('metalGrid');
  const preciousGrid = document.getElementById('preciousGrid');
  const lastUpdatedEl = document.getElementById('lastUpdated');
  if(!metalGrid) return;

  try{
    const [metalsRes, preciousRes] = await Promise.all([
      fetch(ROOT + 'data/metals.json'),
      fetch(ROOT + 'data/goldsilver.json')
    ]);
    const metalsJson = await metalsRes.json();
    const preciousJson = await preciousRes.json();
    const metals = Object.values(metalsJson.metals);

    if(lastUpdatedEl) lastUpdatedEl.textContent = fmtDate(metalsJson.updated);

    /* ticker */
    if(tickerTrack){
      const items = metals.map(m => tickerItem(m)).join('');
      tickerTrack.innerHTML = items + items; // duplicate for seamless loop
    }

    /* metal cards */
    metalGrid.innerHTML = metals.map(m => metalCardHTML(m)).join('');
    metals.forEach(m => {
      const canvas = document.getElementById('spark-' + m.id);
      drawSparkline(canvas, m.history, m.color);
    });

    /* gold / silver */
    if(preciousGrid){
      preciousGrid.innerHTML = Object.values(preciousJson.precious).map(p => preciousCardHTML(p)).join('');
    }

    /* historical chart section */
    initHistoricalChart(metals);

  }catch(e){
    console.error('homepage init failed', e);
    metalGrid.innerHTML = `<p style="color:var(--text-faint)">Unable to load live rates right now. Please refresh.</p>`;
  }
}

function tickerItem(m){
  const cls = m.change >= 0 ? 'up' : 'down';
  const arrow = m.change >= 0 ? '▲' : '▼';
  return `<span class="ticker-item"><b>${m.symbol}</b> ${m.name} ₹${fmtINR(m.rate)} <span class="${cls}">${arrow} ${Math.abs(m.changePct)}%</span></span>`;
}

function metalCardHTML(m){
  return `
  <a class="metal-card" style="--m-color:${m.color}" href="${ROOT}pages/${m.id}-rate-today.html">
    <div class="row1">
      <div class="id">
        <div class="sym">${m.symbol}</div>
        <div class="names"><b>${m.name}</b><small>${m.nameHi}</small></div>
      </div>
      <span class="live-dot" title="Live"></span>
    </div>
    <div class="price">₹${fmtINR(m.rate)} <small>${m.unit}</small></div>
    <div class="change">${changeSpan(m.change, m.changePct)}</div>
    <canvas class="spark" id="spark-${m.id}"></canvas>
    <div class="row-foot">
      <span>Updated ${new Date(m.lastUpdated).toLocaleDateString('en-IN',{day:'2-digit',month:'short'})}</span>
      <span class="view">View details →</span>
    </div>
  </a>`;
}

function preciousCardHTML(p){
  const rows = Object.entries(p.purities).map(([key, v]) => `
    <div class="purity-row">
      <span class="label">${v.label}</span>
      <span class="val">₹${fmtINR(v.perGram)}<small>per gram · ${changeSpanPlain(v.change, v.changePct)}</small></span>
    </div>`).join('');
  return `
  <div class="precious-card">
    <h3><span class="ico" style="background:${p.color}"></span>${p.name} <span style="color:var(--text-faint);font-family:var(--ff-body);font-weight:400;font-size:.9rem">· ${p.nameHi}</span></h3>
    <div class="updated">Last updated ${fmtDate(p.lastUpdated)}</div>
    <div class="purity-rows">${rows}</div>
    <a class="btn btn-outline" href="${ROOT}pages/gold-silver-rate-today.html" style="width:100%;justify-content:center">View full ${p.name.toLowerCase()} chart</a>
  </div>`;
}
function changeSpanPlain(change, pct){
  const cls = change >= 0 ? 'up' : 'down';
  const arrow = change >= 0 ? '▲' : '▼';
  return `<span class="${cls}">${arrow}${Math.abs(pct).toFixed(2)}%</span>`;
}

/* ---------------- Historical chart (homepage) ---------------- */
let mainChartInstance = null;
function initHistoricalChart(metals){
  const canvas = document.getElementById('mainChart');
  const switcher = document.getElementById('metalSwitcher');
  const tabs = document.querySelectorAll('.chart-tab');
  if(!canvas || !switcher) return;

  let activeIds = [metals[0].id];
  let activeRange = '30D';

  switcher.innerHTML = metals.map(m => `
    <button class="metal-pill ${activeIds.includes(m.id)?'active':''}" data-id="${m.id}">
      <span class="dot" style="background:${m.color}"></span>${m.name}
    </button>`).join('');

  function render(){
    if(mainChartInstance) mainChartInstance.destroy();
    const chosen = metals.filter(m => activeIds.includes(m.id));
    mainChartInstance = drawMainChart(canvas, chosen, activeRange);
  }

  switcher.addEventListener('click', (e) => {
    const btn = e.target.closest('.metal-pill');
    if(!btn) return;
    const id = btn.dataset.id;
    if(activeIds.includes(id)){
      if(activeIds.length > 1) activeIds = activeIds.filter(x => x !== id);
    } else {
      if(activeIds.length >= 3) activeIds.shift();
      activeIds.push(id);
    }
    switcher.querySelectorAll('.metal-pill').forEach(p => p.classList.toggle('active', activeIds.includes(p.dataset.id)));
    render();
  });

  tabs.forEach(tab => tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    activeRange = tab.dataset.range;
    render();
  }));

  render();
}

document.addEventListener('DOMContentLoaded', initHomepage);

/* ---------------- PWA: install prompt + SW register ---------------- */
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const toast = document.getElementById('installToast');
  if(toast) toast.classList.add('show');
});
document.addEventListener('DOMContentLoaded', () => {
  const installBtn = document.getElementById('installBtn');
  const dismissBtn = document.getElementById('dismissInstall');
  const toast = document.getElementById('installToast');
  installBtn && installBtn.addEventListener('click', async () => {
    if(!deferredPrompt) return;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    toast && toast.classList.remove('show');
  });
  dismissBtn && dismissBtn.addEventListener('click', () => toast && toast.classList.remove('show'));
});
if('serviceWorker' in navigator){
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(ROOT + 'service-worker.js').catch(() => {});
  });
}

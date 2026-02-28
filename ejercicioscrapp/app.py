import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from flask import Flask, jsonify, render_template_string
import json, re

BASE_URL = "https://datazone.darwinfoundation.org"
PAGE_URL = BASE_URL + "/es/checklist/checklists-archive"

app = Flask(__name__)

# ─────────────────────────────────────────
# SCRAPING & CLEANING
# ─────────────────────────────────────────

def scrape_csv_url(soup, keyword):
    for header in soup.find_all(["h3", "h4"]):
        if keyword in header.text:
            table = header.find_next("table")
            if table:
                first_csv = table.find("a", href=lambda h: h and h.endswith(".csv"))
                if first_csv:
                    return BASE_URL + first_csv["href"]
    return None

def clean_df(df):
    # Eliminar filas y columnas completamente vacías
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Limpiar strings
    for col in df.select_dtypes(include="object").columns:
        # Aseguramos que sea string antes de usar el accesor .str
        df[col] = df[col].astype(str).str.strip()
        # Reemplazar strings vacíos, solo espacios o "nan" (del astype) por NaN real
        df[col] = df[col].replace(["", "nan", "None", "NaN"], pd.NA)

    # Eliminar filas donde la columna principal esté vacía
    nombre_col = next(
        (c for c in df.columns if any(k in c.lower() for k in
         ["species", "especie", "taxon", "name", "nombre", "scientific", "taxonname", "family"])),
        df.columns[0]
    )
    df.dropna(subset=[nombre_col], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def load_data():
    print("🔍 Scrapeando el sitio web...")
    response = requests.get(PAGE_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    datasets = {}
    for keyword, label in [("Pisces", "peces"), ("Aves", "aves")]:
        url = scrape_csv_url(soup, keyword)
        if not url:
            print(f"⚠️  No se encontró CSV para {keyword}")
            continue
        print(f"⬇️  Descargando {label}: {url}")
        r = requests.get(url, timeout=20)
        
        # Probar diferentes codificaciones comunes para CSVs en español
        encodings = ['utf-8-sig', 'latin-1', 'cp1252']
        df = None
        
        for enc in encodings:
            try:
                content = r.content.decode(enc)
                # Si '�' está en el contenido, es probable que la codificación sea incorrecta
                if '�' in content:
                    continue
                df = pd.read_csv(StringIO(content))
                print(f"✅ {label} cargado con encoding: {enc}")
                break
            except Exception:
                continue
        
        if df is None:
            # Fallback a utf-8 con reemplazo si nada funciona
            print(f"⚠️  Fallo detección automática para {label}, usando fallback")
            df = pd.read_csv(StringIO(r.content.decode('utf-8', errors='replace')))
        df = clean_df(df)
        datasets[label] = df
        print(f"✅ {label}: {len(df)} filas, {len(df.columns)} columnas")

    return datasets

DATA = {}

# ─────────────────────────────────────────
# HTML TEMPLATE
# ─────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Fauna Marina de Galápagos</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --ink: #0d1117;
    --paper: #f5f0e8;
    --accent: #1a6b5a;
    --accent2: #c9622a;
    --muted: #7a7060;
    --border: #d4cfc3;
    --fish: #1a6b5a;
    --birds: #c9622a;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Mono', monospace;
    background: var(--paper);
    color: var(--ink);
    min-height: 100vh;
  }

  /* ── HEADER ── */
  header {
    background: var(--ink);
    color: var(--paper);
    padding: 2.5rem 3rem 2rem;
    position: relative;
    overflow: hidden;
  }
  header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 20px,
      rgba(255,255,255,0.015) 20px,
      rgba(255,255,255,0.015) 21px
    );
  }
  .header-inner { position: relative; z-index: 1; max-width: 1400px; margin: 0 auto; }
  header h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    letter-spacing: -0.02em;
    line-height: 1.1;
  }
  header h1 em { color: #6ee7d4; font-style: italic; }
  .subtitle {
    font-size: 0.75rem;
    color: rgba(245,240,232,0.5);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.6rem;
  }

  /* ── TABS ── */
  .tab-bar {
    display: flex;
    gap: 0;
    border-bottom: 2px solid var(--border);
    max-width: 1400px;
    margin: 2rem auto 0;
    padding: 0 3rem;
  }
  .tab {
    padding: 0.9rem 2rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    border: none;
    background: transparent;
    color: var(--muted);
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .tab:hover { color: var(--ink); }
  .tab.active { color: var(--ink); font-weight: 500; }
  .tab[data-tab="peces"].active { border-bottom-color: var(--fish); }
  .tab[data-tab="aves"].active  { border-bottom-color: var(--birds); }
  .dot {
    width: 8px; height: 8px; border-radius: 50%;
    display: inline-block;
  }
  .dot-peces { background: var(--fish); }
  .dot-aves  { background: var(--birds); }

  /* ── MAIN ── */
  main { max-width: 1400px; margin: 0 auto; padding: 2rem 3rem 4rem; }

  .panel { display: none; }
  .panel.active { display: block; }

  /* ── STATS BAR ── */
  .stats-bar {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: var(--ink);
    color: var(--paper);
    border-radius: 4px;
  }
  .stat { flex: 1; min-width: 120px; }
  .stat-val {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    line-height: 1;
  }
  .stat-val.fish-color  { color: #6ee7d4; }
  .stat-val.birds-color { color: #f4a96a; }
  .stat-label {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(245,240,232,0.45);
    margin-top: 0.2rem;
  }

  /* ── CONTROLS ── */
  .controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    align-items: center;
  }
  .search-box {
    flex: 1;
    min-width: 220px;
    position: relative;
  }
  .search-box input {
    width: 100%;
    padding: 0.65rem 1rem 0.65rem 2.5rem;
    border: 1.5px solid var(--border);
    background: white;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    border-radius: 3px;
    outline: none;
    transition: border-color 0.2s;
  }
  .search-box input:focus { border-color: var(--accent); }
  .search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--muted);
    font-size: 0.85rem;
  }

  select {
    padding: 0.65rem 1rem;
    border: 1.5px solid var(--border);
    background: white;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    border-radius: 3px;
    outline: none;
    cursor: pointer;
    color: var(--ink);
  }
  select:focus { border-color: var(--accent); }

  .count-badge {
    font-size: 0.7rem;
    color: var(--muted);
    white-space: nowrap;
    align-self: center;
    margin-left: auto;
  }
  .count-badge strong { color: var(--ink); }

  /* ── TABLE ── */
  .table-wrap {
    overflow-x: auto;
    border: 1.5px solid var(--border);
    border-radius: 4px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78rem;
  }
  thead { background: var(--ink); color: var(--paper); position: sticky; top: 0; z-index: 2; }
  thead th {
    padding: 0.85rem 1rem;
    text-align: left;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
  }
  thead th:hover { background: #1e2733; }
  thead th .sort-arrow { margin-left: 4px; opacity: 0.4; }
  thead th.sorted .sort-arrow { opacity: 1; }

  tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.1s;
  }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: rgba(26,107,90,0.05); }
  tbody td {
    padding: 0.75rem 1rem;
    max-width: 260px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--ink);
  }
  tbody td:first-child {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: var(--accent);
  }
  .peces-panel tbody td:first-child { color: var(--fish); }
  .aves-panel  tbody td:first-child { color: var(--birds); }

  .status-tag {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    font-size: 0.65rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 500;
  }
  .tag-native    { background: #d4ede8; color: #1a5c4e; }
  .tag-endemic   { background: #fde8d8; color: #8c3c0e; }
  .tag-introduced{ background: #fdf4d8; color: #7a5e00; }
  .tag-unknown   { background: #ebebeb; color: #666; }

  /* ── PAGINATION ── */
  .pagination {
    display: flex;
    gap: 0.4rem;
    justify-content: center;
    margin-top: 1.5rem;
    flex-wrap: wrap;
  }
  .page-btn {
    padding: 0.4rem 0.8rem;
    border: 1.5px solid var(--border);
    background: white;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    cursor: pointer;
    border-radius: 3px;
    color: var(--ink);
    transition: all 0.15s;
  }
  .page-btn:hover { border-color: var(--accent); color: var(--accent); }
  .page-btn.active { background: var(--ink); color: var(--paper); border-color: var(--ink); }
  .page-btn:disabled { opacity: 0.35; cursor: not-allowed; }

  /* ── EMPTY STATE ── */
  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--muted);
  }
  .empty-state .icon { font-size: 3rem; margin-bottom: 1rem; }
  .empty-state p { font-size: 0.85rem; }

  /* ── LOADING ── */
  #loading {
    position: fixed; inset: 0;
    background: var(--paper);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    z-index: 999;
    gap: 1.5rem;
  }
  .loader-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: var(--ink);
  }
  .loader-text em { color: var(--accent); font-style: italic; }
  .loader-sub {
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }
  .spinner {
    width: 40px; height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .fade-in { animation: fadeIn 0.4s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

  @media (max-width: 640px) {
    header, .tab-bar, main { padding-left: 1.2rem; padding-right: 1.2rem; }
    .stats-bar { gap: 1rem; }
  }
</style>
</head>
<body>

<div id="loading">
  <div class="spinner"></div>
  <div class="loader-text">Fauna de <em>Galápagos</em></div>
  <div class="loader-sub">Cargando datos…</div>
</div>

<header>
  <div class="header-inner">
    <h1>Fauna de <em>Galápagos</em></h1>
    <p class="subtitle">Lista de Especies — Fundación Charles Darwin · datazone.darwinfoundation.org</p>
  </div>
</header>

<div class="tab-bar">
  <button class="tab active" data-tab="peces">
    <span class="dot dot-peces"></span> Pisces — Peces
  </button>
  <button class="tab" data-tab="aves">
    <span class="dot dot-aves"></span> Aves
  </button>
</div>

<main>
  <!-- PECES -->
  <div class="panel peces-panel active" id="panel-peces">
    <div class="stats-bar" id="stats-peces"></div>
    <div class="controls">
      <div class="search-box">
        <span class="search-icon">⌕</span>
        <input type="text" placeholder="Buscar especie, familia, orden…" id="search-peces" oninput="filterTable('peces')"/>
      </div>
      <select id="filter-peces" onchange="filterTable('peces')">
        <option value="">Todos los grupos</option>
      </select>
      <span class="count-badge" id="badge-peces"></span>
    </div>
    <div class="table-wrap">
      <table id="table-peces">
        <thead id="thead-peces"></thead>
        <tbody id="tbody-peces"></tbody>
      </table>
    </div>
    <div class="pagination" id="pages-peces"></div>
  </div>

  <!-- AVES -->
  <div class="panel aves-panel" id="panel-aves">
    <div class="stats-bar" id="stats-aves"></div>
    <div class="controls">
      <div class="search-box">
        <span class="search-icon">⌕</span>
        <input type="text" placeholder="Buscar especie, familia, orden…" id="search-aves" oninput="filterTable('aves')"/>
      </div>
      <select id="filter-aves" onchange="filterTable('aves')">
        <option value="">Todos los grupos</option>
      </select>
      <span class="count-badge" id="badge-aves"></span>
    </div>
    <div class="table-wrap">
      <table id="table-aves">
        <thead id="thead-aves"></thead>
        <tbody id="tbody-aves"></tbody>
      </table>
    </div>
    <div class="pagination" id="pages-aves"></div>
  </div>
</main>

<script>
const PER_PAGE = 50;
const state = {
  peces: { data: [], filtered: [], page: 1, sortCol: null, sortDir: 1 },
  aves:  { data: [], filtered: [], page: 1, sortCol: null, sortDir: 1 }
};

// ── TABS ──
document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab, .panel').forEach(el => el.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('panel-' + btn.dataset.tab).classList.add('active');
  });
});

// ── STATUS TAG ──
function statusTag(val) {
  if (!val || val === 'nan') return '';
  const v = String(val).toLowerCase();
  let cls = 'tag-unknown', label = val;
  if (v.includes('native') || v.includes('nativa')) { cls = 'tag-native'; label = 'Nativa'; }
  else if (v.includes('endemic') || v.includes('endémica') || v.includes('endemica')) { cls = 'tag-endemic'; label = 'Endémica'; }
  else if (v.includes('introduc')) { cls = 'tag-introduced'; label = 'Introducida'; }
  return `<span class="status-tag ${cls}">${label}</span>`;
}

// ── RENDER TABLE ──
function renderTable(key) {
  const s = state[key];
  const start = (s.page - 1) * PER_PAGE;
  const slice = s.filtered.slice(start, start + PER_PAGE);
  const tbody = document.getElementById('tbody-' + key);
  
  if (s.filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="99">
      <div class="empty-state"><div class="icon">🔍</div><p>No se encontraron resultados</p></div>
    </td></tr>`;
    document.getElementById('badge-' + key).innerHTML = '<strong>0</strong> resultados';
    renderPages(key);
    return;
  }

  const cols = Object.keys(s.data[0]);
  tbody.innerHTML = slice.map(row => `
    <tr class="fade-in">
      ${cols.map((c, i) => {
        const v = row[c] ?? '';
        const isStatus = c.toLowerCase().includes('status') || c.toLowerCase().includes('estado');
        return `<td title="${String(v).replace(/"/g, '&quot;')}">${isStatus ? statusTag(v) : (v === 'nan' || v === null ? '<span style="color:#bbb">—</span>' : v)}</td>`;
      }).join('')}
    </tr>`).join('');

  document.getElementById('badge-' + key).innerHTML =
    `<strong>${s.filtered.length}</strong> de ${s.data.length} especies`;
  renderPages(key);
}

// ── PAGINATION ──
function renderPages(key) {
  const s = state[key];
  const total = Math.ceil(s.filtered.length / PER_PAGE);
  const pg = document.getElementById('pages-' + key);
  if (total <= 1) { pg.innerHTML = ''; return; }

  let html = `<button class="page-btn" onclick="goPage('${key}',${s.page-1})" ${s.page===1?'disabled':''}>←</button>`;
  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || Math.abs(i - s.page) <= 2) {
      html += `<button class="page-btn ${i===s.page?'active':''}" onclick="goPage('${key}',${i})">${i}</button>`;
    } else if (Math.abs(i - s.page) === 3) {
      html += `<span style="align-self:center;color:var(--muted)">…</span>`;
    }
  }
  html += `<button class="page-btn" onclick="goPage('${key}',${s.page+1})" ${s.page===total?'disabled':''}>→</button>`;
  pg.innerHTML = html;
}

function goPage(key, p) {
  const total = Math.ceil(state[key].filtered.length / PER_PAGE);
  if (p < 1 || p > total) return;
  state[key].page = p;
  renderTable(key);
  document.getElementById('panel-' + key).scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── FILTER ──
function filterTable(key) {
  const q = document.getElementById('search-' + key).value.toLowerCase().trim();
  const grp = document.getElementById('filter-' + key).value.toLowerCase();
  const cols = Object.keys(state[key].data[0] || {});
  const filterCol = cols.find(c => c.toLowerCase().includes('order') || c.toLowerCase().includes('orden') || c.toLowerCase().includes('family') || c.toLowerCase().includes('familia'));

  state[key].filtered = state[key].data.filter(row => {
    const matchQ = !q || Object.values(row).some(v => String(v).toLowerCase().includes(q));
    const matchG = !grp || (filterCol && String(row[filterCol]).toLowerCase() === grp);
    return matchQ && matchG;
  });
  state[key].page = 1;
  renderTable(key);
}

// ── SORT ──
function sortTable(key, col) {
  const s = state[key];
  if (s.sortCol === col) s.sortDir *= -1;
  else { s.sortCol = col; s.sortDir = 1; }

  s.filtered.sort((a, b) => {
    const av = String(a[col] ?? '').toLowerCase();
    const bv = String(b[col] ?? '').toLowerCase();
    return av < bv ? -s.sortDir : av > bv ? s.sortDir : 0;
  });
  s.page = 1;
  renderTable(key);

  // Update header arrows
  document.querySelectorAll(`#thead-${key} th`).forEach(th => {
    th.classList.remove('sorted');
    th.querySelector('.sort-arrow').textContent = ' ↕';
  });
  const ths = document.querySelectorAll(`#thead-${key} th`);
  const idx = Object.keys(s.data[0]).indexOf(col);
  if (idx >= 0) {
    ths[idx].classList.add('sorted');
    ths[idx].querySelector('.sort-arrow').textContent = s.sortDir === 1 ? ' ↑' : ' ↓';
  }
}

// ── INIT ──
async function init() {
  const res = await fetch('/api/data');
  const json = await res.json();

  for (const key of ['peces', 'aves']) {
    const rows = json[key] || [];
    state[key].data = rows;
    state[key].filtered = [...rows];

    if (rows.length === 0) continue;
    const cols = Object.keys(rows[0]);

    // Build header
    document.getElementById('thead-' + key).innerHTML = `<tr>
      ${cols.map(c => `<th onclick="sortTable('${key}','${c}')">${c}<span class="sort-arrow"> ↕</span></th>`).join('')}
    </tr>`;

    // Stats
    const statusCol = cols.find(c => c.toLowerCase().includes('status') || c.toLowerCase().includes('estado'));
    const familyCol  = cols.find(c => c.toLowerCase().includes('family') || c.toLowerCase().includes('familia'));
    const orderCol   = cols.find(c => c.toLowerCase().includes('order') || c.toLowerCase().includes('orden'));

    const endemic  = statusCol ? rows.filter(r => String(r[statusCol]).toLowerCase().includes('endemi')).length : '—';
    const families = familyCol ? new Set(rows.map(r => r[familyCol]).filter(Boolean)).size : '—';
    const orders   = orderCol  ? new Set(rows.map(r => r[orderCol]).filter(Boolean)).size : '—';

    const colorClass = key === 'peces' ? 'fish-color' : 'birds-color';
    document.getElementById('stats-' + key).innerHTML = `
      <div class="stat"><div class="stat-val ${colorClass}">${rows.length}</div><div class="stat-label">Especies registradas</div></div>
      <div class="stat"><div class="stat-val ${colorClass}">${endemic}</div><div class="stat-label">Endémicas</div></div>
      <div class="stat"><div class="stat-val ${colorClass}">${families}</div><div class="stat-label">Familias</div></div>
      <div class="stat"><div class="stat-val ${colorClass}">${orders}</div><div class="stat-label">Órdenes</div></div>
    `;

    // Populate filter dropdown
    const filterCol = orderCol || familyCol;
    if (filterCol) {
      const vals = [...new Set(rows.map(r => r[filterCol]).filter(Boolean))].sort();
      const sel = document.getElementById('filter-' + key);
      sel.innerHTML = `<option value="">Todos los ${filterCol}</option>` +
        vals.map(v => `<option value="${String(v).toLowerCase()}">${v}</option>`).join('');
    }

    renderTable(key);
  }

  document.getElementById('loading').style.display = 'none';
}

init();
</script>
</body>
</html>"""

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def api_data():
    out = {}
    for key, df in DATA.items():
        # Replace NaN with None for JSON serialization
        out[key] = json.loads(df.where(pd.notnull(df), None).to_json(orient="records", force_ascii=False))
    return jsonify(out)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    DATA.update(load_data())
    print("\n🌿 Servidor listo → http://localhost:5000\n")
    app.run(debug=False, port=5000)

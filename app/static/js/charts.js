let charts = {};
let currentFile = null;
let currentSheet = null;

const dropArea   = document.getElementById('drop-area');
const fileInput  = document.getElementById('file-input');

// ── DRAG & DROP ──
dropArea.addEventListener('dragover',  e => { e.preventDefault(); dropArea.classList.add('drag-over'); });
dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over'));
dropArea.addEventListener('drop', e => {
    e.preventDefault();
    dropArea.classList.remove('drag-over');
    handleUpload(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', e => handleUpload(e.target.files[0]));

    document.getElementById('btn-change-sheet').addEventListener('click', () => {
    currentSheet = document.getElementById('sheet-select').value;
    fetchPreview();
    });

    document.getElementById('btn-analyze').addEventListener('click', doAnalysis);

    document.getElementById('btn-reset').addEventListener('click', () => {
    currentFile = null; currentSheet = null;
    document.getElementById('results').hidden       = true;
    document.getElementById('btn-actions').hidden   = true;
    document.getElementById('preview-section').hidden = true;
    document.getElementById('sheet-selector').hidden  = true;
    document.getElementById('drop-area').hidden     = false;
    fileInput.value = '';
    setStep(1);
    });

    // ── PASO 1: subir y detectar tipo ──
    function handleUpload(file) {
    if (!file) return;
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv','xlsx','xls'].includes(ext)) {
        alert('Formato no válido. Usa CSV, .xlsx o .xls'); return;
    }

    const fd = new FormData();
    fd.append('file', file);

    fetch('/file-info', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
        if (data.error) { alert(data.error); return; }
        currentFile  = data.filename;
        currentSheet = null;

        if (data.hojas && data.hojas.length > 1) {
            // Excel multi-hoja → mostrar selector
            const sel = document.getElementById('sheet-select');
            sel.innerHTML = data.hojas.map(h => `<option value="${h}">${h}</option>`).join('');
            document.getElementById('sheet-selector').hidden = false;
            currentSheet = data.hojas[0];
            setStep(2);
        } else {
            document.getElementById('sheet-selector').hidden = true;
            setStep(3);
        }
        fetchPreview();
        })
        .catch(() => alert('Error de conexión al subir el archivo'));
    }

    // ── PASO 2-3: preview ──
    function fetchPreview() {
    const fd = new FormData();
    fd.append('filename', currentFile);
    if (currentSheet) fd.append('sheet_name', currentSheet);

    fetch('/preview', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
        if (data.error) { alert(data.error); return; }
        renderPreview(data.preview, data.total_filas);
        document.getElementById('btn-actions').hidden = false;
        setStep(3);
        });
    }

    function renderPreview(prev, total) {
    document.getElementById('preview-label').textContent =
        `Vista previa — primeras 5 filas de ${total} registros`;

    const thead = document.getElementById('preview-head');
    const tbody = document.getElementById('preview-body');
    thead.innerHTML = '<tr>' + prev.columnas.map(c => `<th>${c}</th>`).join('') + '</tr>';
    tbody.innerHTML = prev.filas.map(row =>
        '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
    ).join('');

    document.getElementById('preview-section').hidden = false;
    document.getElementById('drop-area').hidden = true;
    }

    // ── PASO 4: análisis completo ──
    function doAnalysis() {
    document.getElementById('loader').hidden  = false;
    document.getElementById('results').hidden = true;
    setStep(4);

    const fd = new FormData();
    fd.append('filename', currentFile);
    if (currentSheet) fd.append('sheet_name', currentSheet);

    fetch('/analyze', { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
        document.getElementById('loader').hidden = true;
        if (data.error) { alert('Error: ' + data.error); return; }
        renderDashboard(data);
        })
        .catch(() => {
        document.getElementById('loader').hidden = true;
        alert('Error de conexión al analizar');
        });
    }

    // ── RENDER DASHBOARD ──
    function renderDashboard(d) {
    const p = d.prediction;

    document.getElementById('info-filas').textContent      = d.filas;
    document.getElementById('info-cols').textContent       = d.columnas.length;
    document.getElementById('info-tendencia').textContent  = p.tendencia ? (p.tendencia === 'creciente' ? '📈 creciente' : '📉 decreciente') : '—';
    document.getElementById('info-r2').textContent         = p.r2_score ?? '—';

    const opts = { responsive: true, plugins: { legend: { labels: { color: '#B8C4D4', font: { size: 11 } } } }, scales: { x: { ticks: { color: '#8899BB' }, grid: { color: '#24355244' } }, y: { ticks: { color: '#8899BB' }, grid: { color: '#24355244' } } } };
    const optsNoScale = { responsive: true, plugins: { legend: { labels: { color: '#B8C4D4', font: { size: 11 } } } } };

    makeChart('chart-line',   'line',   d.chart_line,   opts);
    makeChart('chart-bar',    'bar',    d.chart_bar,    opts);
    makeChart('chart-pie',    'doughnut', d.chart_pie,  optsNoScale);
    makeChart('chart-radar',  'radar',  d.chart_radar,  optsNoScale);
    makeChart('chart-scatter','scatter',d.chart_scatter, opts);

    // Predicción
    if (p.predicciones) {
        const hist   = p.historico_reciente || [];
        const hLabels = hist.map((_, i) => `T-${hist.length - i}`);
        const predData = {
        labels: [...hLabels, ...p.labels_prediccion],
        datasets: [
            { label: 'Histórico', data: [...hist, ...Array(p.predicciones.length).fill(null)], borderColor: '#4F8EF7', backgroundColor: '#4F8EF733', tension: 0.4 },
            { label: 'Predicción', data: [...Array(hist.length - 1).fill(null), hist[hist.length-1], ...p.predicciones], borderColor: '#3BCEAC', backgroundColor: '#3BCEAC22', borderDash: [5,3], tension: 0.4 }
        ]
        };
        makeChart('chart-pred', 'line', predData, opts);
        document.getElementById('pred-info').textContent = `Columna: "${p.columna}" · Pendiente: ${p.pendiente} · R² = ${p.r2_score}`;
    }

    renderStats(d.stats);
    renderCorrelation(d.correlacion);
    renderOutliers(d.outliers);

    document.getElementById('results').hidden = false;
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }

    function makeChart(id, type, data, options) {
    if (!data) return;
    if (charts[id]) charts[id].destroy();
    charts[id] = new Chart(document.getElementById(id), { type, data, options });
    }

    function renderStats(stats) {
    const c = document.getElementById('stats-container');
    c.innerHTML = Object.entries(stats).map(([col, s]) => `
        <div class="stat-block">
        <div class="stat-col-title">${col}
            ${s.nulos > 0 ? `<span style="color:#F97316;font-size:.72rem;margin-left:.5rem">(${s.nulos} nulos)</span>` : ''}
        </div>
        <div class="stat-grid">
            <div class="stat-item"><span>Media</span><strong>${s.media}</strong></div>
            <div class="stat-item"><span>Mediana</span><strong>${s.mediana}</strong></div>
            <div class="stat-item"><span>Desv. estándar</span><strong>${s.desv_std}</strong></div>
            <div class="stat-item"><span>Varianza</span><strong>${s.varianza}</strong></div>
            <div class="stat-item"><span>Mínimo</span><strong>${s.minimo}</strong></div>
            <div class="stat-item"><span>Máximo</span><strong>${s.maximo}</strong></div>
            <div class="stat-item"><span>Q1</span><strong>${s.q1}</strong></div>
            <div class="stat-item"><span>Q3</span><strong>${s.q3}</strong></div>
            <div class="stat-item"><span>Registros</span><strong>${s.count}</strong></div>
        </div>
        </div>`).join('');
    }

    function renderCorrelation(corr) {
    if (!corr) return;
    document.getElementById('corr-card').hidden = false;
    const rows = corr.columnas.map((col, i) =>
        `<tr><th>${col}</th>` +
        corr.matriz[i].map(v => {
        const abs = Math.abs(v);
        const cls = abs > 0.7 ? 'corr-cell-high' : abs > 0.4 ? 'corr-cell-medium' : 'corr-cell-low';
        return `<td class="${cls}">${v}</td>`;
        }).join('') + '</tr>'
    ).join('');
    document.getElementById('corr-container').innerHTML =
        `<table class="corr-table"><thead><tr><th></th>${corr.columnas.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table>`;
    }

    function renderOutliers(outliers) {
    if (!outliers) return;
    document.getElementById('outliers-container').innerHTML =
        Object.entries(outliers).map(([col, o]) => `
        <div class="outlier-item">
            <span class="col-name">${col}</span>
            <span>${o.porcentaje}% de los datos</span>
            <span class="outlier-badge ${o.cantidad === 0 ? 'ok' : ''}">
            ${o.cantidad === 0 ? '✓ Sin outliers' : `⚠ ${o.cantidad} outliers`}
            </span>
        </div>`).join('');
    }

    function setStep(n) {
    [1,2,3,4].forEach(i => {
        const el = document.getElementById('step' + i);
        el.classList.remove('active','done');
        if (i === n) el.classList.add('active');
        if (i < n)  el.classList.add('done');
    });
}
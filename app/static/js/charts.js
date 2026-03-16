let chartMain = null;
let chartPred = null;

const dropArea  = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');

// Drag & Drop
dropArea.addEventListener('dragover',  e => { e.preventDefault(); dropArea.classList.add('drag-over'); });
dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over'));
dropArea.addEventListener('drop', e => {
    e.preventDefault();
    dropArea.classList.remove('drag-over');
    handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', e => handleFile(e.target.files[0]));

    function handleFile(file) {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    document.getElementById('loader').hidden  = false;
    document.getElementById('results').hidden = true;

    fetch('/upload', { method: 'POST', body: formData })
        .then(r => r.json())
        .then(data => {
        document.getElementById('loader').hidden = true;
        if (data.error) { alert('❌ ' + data.error); return; }
        renderDashboard(data);
        })
        .catch(() => {
        document.getElementById('loader').hidden = true;
        alert('Error de conexión con el servidor');
        });
    }

    function renderDashboard(data) {
    // Info bar
    document.getElementById('info-filas').textContent     = `📋 ${data.filas} filas`;
    document.getElementById('info-cols').textContent      = `🔢 ${data.columnas.length} columnas`;
    const p = data.prediction;
    if (p.tendencia) {
        const icono = p.tendencia === 'creciente' ? '📈' : '📉';
        document.getElementById('info-tendencia').textContent =
        `${icono} Tendencia ${p.tendencia} · R² ${p.r2_score}`;
    }

    // Gráfico principal
    if (chartMain) chartMain.destroy();
    chartMain = new Chart(document.getElementById('chart-main'), {
        type: 'line',
        data: data.chart_data,
        options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: { y: { beginAtZero: false } }
        }
    });

    // Gráfico predicción
    if (chartPred) chartPred.destroy();
    if (p.predicciones) {
        const hist   = p.historico_reciente;
        const histLabels = hist.map((_, i) => `T-${hist.length - i}`);

        chartPred = new Chart(document.getElementById('chart-pred'), {
        type: 'line',
        data: {
            labels: [...histLabels, ...p.labels_prediccion],
            datasets: [
            {
                label: `${p.columna} (histórico)`,
                data: [...hist, ...Array(p.predicciones.length).fill(null)],
                borderColor: '#4F8EF7', backgroundColor: '#4F8EF733',
                tension: 0.4
            },
            {
                label: 'Predicción',
                data: [...Array(hist.length - 1).fill(null), hist[hist.length - 1], ...p.predicciones],
                borderColor: '#F97316', backgroundColor: '#F9731633',
                borderDash: [6, 3], tension: 0.4
            }
            ]
        },
        options: { responsive: true, plugins: { legend: { position: 'top' } } }
        });

        document.getElementById('pred-info').textContent =
        `Pendiente: ${p.pendiente} por paso · R² = ${p.r2_score} · Columna: "${p.columna}"`;
    }

    // Tabla de estadísticas
    const container = document.getElementById('stats-container');
    container.innerHTML = '';
    for (const [col, s] of Object.entries(data.stats)) {
        container.innerHTML += `
        <div class="stat-block">
            <h3>${col}</h3>
            <div class="stat-grid">
            <div><span>Media</span><strong>${s.media}</strong></div>
            <div><span>Mediana</span><strong>${s.mediana}</strong></div>
            <div><span>Desv. estándar</span><strong>${s.desv_std}</strong></div>
            <div><span>Varianza</span><strong>${s.varianza}</strong></div>
            <div><span>Mínimo</span><strong>${s.minimo}</strong></div>
            <div><span>Máximo</span><strong>${s.maximo}</strong></div>
            <div><span>Registros</span><strong>${s.count}</strong></div>
            </div>
        </div>`;
    }

    document.getElementById('results').hidden = false;
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}
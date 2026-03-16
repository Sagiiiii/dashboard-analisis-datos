import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_info(filepath):
    """Retorna metadatos del archivo: tipo y hojas disponibles si es Excel."""
    ext = filepath.rsplit('.', 1)[1].lower()
    info = {'tipo': ext, 'hojas': None}
    if ext in ('xlsx', 'xls'):
        xf = pd.ExcelFile(filepath)
        info['hojas'] = xf.sheet_names
    return info

def load_file(filepath, sheet_name=None):
    """Carga CSV o Excel, con soporte multi-hoja."""
    ext = filepath.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        try:
            return pd.read_csv(filepath)
        except Exception:
            return pd.read_csv(filepath, sep=';')
    elif ext in ('xlsx', 'xls'):
        return pd.read_excel(filepath, sheet_name=sheet_name or 0)
    raise ValueError("Formato no soportado.")

def get_preview(df, rows=5):
    """Primeras filas para previsualizar el archivo."""
    preview = df.head(rows).copy()
    for col in preview.select_dtypes(include=['datetime64']).columns:
        preview[col] = preview[col].dt.strftime('%Y-%m-%d')
    return {
        'columnas': list(preview.columns),
        'filas':    preview.fillna('').values.tolist()
    }

def get_statistics(df):
    """Estadísticas descriptivas completas por columna numérica."""
    numeric = df.select_dtypes(include=[np.number])
    stats = {}
    for col in numeric.columns:
        data = numeric[col].dropna()
        q1   = float(data.quantile(0.25))
        q3   = float(data.quantile(0.75))
        stats[col] = {
            'media':    round(float(data.mean()), 4),
            'mediana':  round(float(data.median()), 4),
            'varianza': round(float(data.var()), 4),
            'desv_std': round(float(data.std()), 4),
            'minimo':   round(float(data.min()), 4),
            'maximo':   round(float(data.max()), 4),
            'q1':       round(q1, 4),
            'q3':       round(q3, 4),
            'count':    int(data.count()),
            'nulos':    int(numeric[col].isna().sum()),
        }
    return stats

def get_correlation(df):
    """Matriz de correlación entre columnas numéricas."""
    numeric = df.select_dtypes(include=[np.number])
    if len(numeric.columns) < 2:
        return None
    corr = numeric.corr().round(3)
    return {
        'columnas': list(corr.columns),
        'matriz':   corr.values.tolist()
    }

def get_outliers(df):
    """Detecta outliers por columna usando el método IQR."""
    numeric = df.select_dtypes(include=[np.number])
    outliers = {}
    for col in numeric.columns:
        data = numeric[col].dropna()
        q1   = data.quantile(0.25)
        q3   = data.quantile(0.75)
        iqr  = q3 - q1
        mask = (data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)
        outliers[col] = {
            'cantidad':   int(mask.sum()),
            'porcentaje': round(float(mask.sum() / len(data) * 100), 2),
            'valores':    data[mask].round(2).tolist()[:10]
        }
    return outliers

def get_nulls_summary(df):
    """Resumen de valores nulos por columna."""
    total = len(df)
    return {
        col: {
            'nulos':       int(df[col].isna().sum()),
            'porcentaje':  round(float(df[col].isna().sum() / total * 100), 2),
            'tipo':        str(df[col].dtype)
        }
        for col in df.columns
    }

def detect_date_column(df):
    """Detecta la columna de fecha automáticamente."""
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True)
            if parsed.notna().sum() > len(df) * 0.8:
                df[col] = parsed
                return col
        except Exception:
            pass
    return None

def get_chart_data(df):
    """Prepara datasets para Chart.js (líneas y barras)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    date_col     = detect_date_column(df)

    labels = (
        df[date_col].dt.strftime('%Y-%m-%d').tolist()
        if date_col else list(range(1, len(df) + 1))
    )

    COLORS = ['#3BCEAC','#4F8EF7','#F97316','#A855F7','#EF4444','#14B8A6']
    datasets = []
    for i, col in enumerate(numeric_cols[:6]):
        c = COLORS[i % len(COLORS)]
        datasets.append({
            'label':           col,
            'data':            df[col].fillna(0).round(2).tolist(),
            'borderColor':     c,
            'backgroundColor': c + '33',
            'tension':         0.4,
            'fill':            False,
            'pointRadius':     3,
        })
    return {'labels': labels, 'datasets': datasets}

def get_bar_chart_data(df):
    """Top 10 filas de la primera columna numérica para gráfico de barras."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None
    col    = numeric_cols[0]
    top10  = df[col].fillna(0).head(10)
    labels = [str(i + 1) for i in range(len(top10))]

    # Intentar usar una columna de texto como etiqueta
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    if text_cols:
        labels = df[text_cols[0]].fillna('').astype(str).head(10).tolist()

    return {
        'labels': labels,
        'datasets': [{
            'label':           col,
            'data':            top10.round(2).tolist(),
            'backgroundColor': '#3BCEAC99',
            'borderColor':     '#3BCEAC',
            'borderWidth':     1,
            'borderRadius':    4,
        }]
    }

def get_pie_chart_data(df):
    """Distribución proporcional de la primera columna numérica (top 6)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None
    col    = numeric_cols[0]
    series = df[col].fillna(0).abs().head(6)
    labels = [str(i + 1) for i in range(len(series))]
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    if text_cols:
        labels = df[text_cols[0]].fillna('').astype(str).head(6).tolist()

    COLORS = ['#3BCEAC','#4F8EF7','#F97316','#A855F7','#EF4444','#14B8A6']
    return {
        'labels': labels,
        'datasets': [{
            'data':            series.round(2).tolist(),
            'backgroundColor': COLORS[:len(series)],
            'borderColor':     '#0A1628',
            'borderWidth':     2,
        }]
    }

def get_radar_chart_data(df):
    """Radar con promedios normalizados de cada columna numérica."""
    numeric = df.select_dtypes(include=[np.number])
    if len(numeric.columns) < 3:
        return None
    cols  = numeric.columns[:7].tolist()
    means = numeric[cols].mean()
    # Normalizar 0-100
    mn, mx = means.min(), means.max()
    norm   = ((means - mn) / (mx - mn + 1e-9) * 100).round(1)
    return {
        'labels': cols,
        'datasets': [{
            'label':           'Promedio normalizado',
            'data':            norm.tolist(),
            'backgroundColor': '#3BCEAC22',
            'borderColor':     '#3BCEAC',
            'pointBackgroundColor': '#3BCEAC',
        }]
    }

def get_scatter_data(df):
    """Scatter plot entre las dos primeras columnas numéricas."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return None
    x_col, y_col = numeric_cols[0], numeric_cols[1]
    pairs = df[[x_col, y_col]].dropna().head(200)
    return {
        'x_label': x_col,
        'y_label': y_col,
        'datasets': [{
            'label':           f'{x_col} vs {y_col}',
            'data':            [{'x': round(r[x_col], 3), 'y': round(r[y_col], 3)}
                                for _, r in pairs.iterrows()],
            'backgroundColor': '#4F8EF799',
            'borderColor':     '#4F8EF7',
            'pointRadius':     4,
        }]
    }

def get_prediction(df, steps=6):
    """Regresión lineal sobre la primera columna numérica."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return {}
    col  = numeric_cols[0]
    data = df[col].dropna().values
    X    = np.arange(len(data)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, data)

    future_X     = np.arange(len(data), len(data) + steps).reshape(-1, 1)
    predictions  = model.predict(future_X).round(2).tolist()
    historico    = data[-10:].round(2).tolist()

    return {
        'columna':           col,
        'r2_score':          round(model.score(X, data), 4),
        'tendencia':         'creciente' if model.coef_[0] > 0 else 'decreciente',
        'pendiente':         round(float(model.coef_[0]), 4),
        'predicciones':      predictions,
        'historico_reciente': historico,
        'labels_prediccion': [f'+{i+1}' for i in range(steps)],
    }
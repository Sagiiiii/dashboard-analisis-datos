import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def load_file(filepath):
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith(('.xlsx', '.xls')):
        return pd.read_excel(filepath)
    raise ValueError("Formato no soportado. Usa CSV o Excel.")

def get_statistics(df):
    numeric_cols = df.select_dtypes(include=[np.number])
    stats = {}
    for col in numeric_cols.columns:
        data = numeric_cols[col].dropna()
        stats[col] = {
            'media':    round(float(data.mean()), 4),
            'mediana':  round(float(data.median()), 4),
            'varianza': round(float(data.var()), 4),
            'desv_std': round(float(data.std()), 4),
            'minimo':   round(float(data.min()), 4),
            'maximo':   round(float(data.max()), 4),
            'count':    int(data.count()),
        }
    return stats

def get_chart_data(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    date_col = None

    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True)
            if parsed.notna().sum() > len(df) * 0.8:
                date_col = col
                df[col] = parsed
                break
        except:
            pass

    if date_col:
        labels = df[date_col].dt.strftime('%Y-%m-%d').tolist()
    else:
        labels = list(range(1, len(df) + 1))

    colors = ['#4F8EF7','#F97316','#22C55E','#A855F7','#EF4444','#14B8A6']
    datasets = []
    for i, col in enumerate(numeric_cols[:5]):
        datasets.append({
            'label': col,
            'data': df[col].fillna(0).round(2).tolist(),
            'borderColor': colors[i % len(colors)],
            'backgroundColor': colors[i % len(colors)] + '33',
            'tension': 0.4,
            'fill': False,
        })
    return {'labels': labels, 'datasets': datasets}

def get_prediction(df, steps=5):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return {}

    col = numeric_cols[0]
    data = df[col].dropna().values
    X = np.arange(len(data)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, data)

    future_X = np.arange(len(data), len(data) + steps).reshape(-1, 1)
    predictions = model.predict(future_X).round(2).tolist()

    return {
        'columna':           col,
        'r2_score':          round(model.score(X, data), 4),
        'tendencia':         'creciente' if model.coef_[0] > 0 else 'decreciente',
        'pendiente':         round(float(model.coef_[0]), 4),
        'predicciones':      predictions,
        'labels_prediccion': [f'Paso +{i+1}' for i in range(steps)],
        'historico_reciente': data[-10:].round(2).tolist(),
    }
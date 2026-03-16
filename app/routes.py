from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from .analysis import (
    allowed_file, get_file_info, load_file, get_preview,
    get_statistics, get_correlation, get_outliers, get_nulls_summary,
    get_chart_data, get_bar_chart_data, get_pie_chart_data,
    get_radar_chart_data, get_scatter_data, get_prediction
)

main = Blueprint('main', __name__)

def save_upload(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath, filename

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/file-info', methods=['POST'])
def file_info():
    """Paso 1: recibe el archivo, retorna tipo y hojas disponibles."""
    if 'file' not in request.files:
        return jsonify({'error': 'No se recibió archivo'}), 400
    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Formato no válido. Usa CSV, .xlsx o .xls'}), 400

    filepath, filename = save_upload(file)
    try:
        info = get_file_info(filepath)
        info['filename'] = filename
        return jsonify(info)
    except Exception as e:
        os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@main.route('/preview', methods=['POST'])
def preview():
    """Paso 2: previsualiza las primeras filas según hoja seleccionada."""
    filename   = request.form.get('filename')
    sheet_name = request.form.get('sheet_name')
    if not filename:
        return jsonify({'error': 'Falta nombre de archivo'}), 400

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Archivo no encontrado. Vuelve a subirlo.'}), 404

    try:
        df   = load_file(filepath, sheet_name=sheet_name)
        prev = get_preview(df)
        return jsonify({'success': True, 'preview': prev, 'total_filas': len(df)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/analyze', methods=['POST'])
def analyze():
    """Paso 3: análisis completo del archivo."""
    filename   = request.form.get('filename')
    sheet_name = request.form.get('sheet_name')
    if not filename:
        return jsonify({'error': 'Falta nombre de archivo'}), 400

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Archivo no encontrado. Vuelve a subirlo.'}), 404

    try:
        df = load_file(filepath, sheet_name=sheet_name)
        response = {
            'success':     True,
            'filas':       len(df),
            'columnas':    list(df.columns),
            'stats':       get_statistics(df),
            'correlacion': get_correlation(df),
            'outliers':    get_outliers(df),
            'nulos':       get_nulls_summary(df),
            'chart_line':  get_chart_data(df),
            'chart_bar':   get_bar_chart_data(df),
            'chart_pie':   get_pie_chart_data(df),
            'chart_radar': get_radar_chart_data(df),
            'chart_scatter': get_scatter_data(df),
            'prediction':  get_prediction(df),
        }
    except Exception as e:
        response = {'error': str(e)}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return jsonify(response)
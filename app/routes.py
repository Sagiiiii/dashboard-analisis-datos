from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from .analysis import load_file, get_statistics, get_chart_data, get_prediction

main = Blueprint('main', __name__)
ALLOWED = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No se recibió ningún archivo'}), 400

    file = request.files['file']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Archivo inválido. Solo CSV o Excel'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        df = load_file(filepath)
        response = {
            'success':    True,
            'filas':      len(df),
            'columnas':   list(df.columns),
            'stats':      get_statistics(df),
            'chart_data': get_chart_data(df),
            'prediction': get_prediction(df),
        }
    except Exception as e:
        response = {'error': str(e)}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return jsonify(response)
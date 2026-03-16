# 📊 Dashboard de Análisis de Datos

> Aplicación web que convierte cualquier CSV o Excel en estadísticas, gráficos interactivos y predicciones automáticas — sin escribir una sola línea de código.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat&logo=flask&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=flat&logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.x-FF6384?style=flat&logo=chartdotjs&logoColor=white)

🔗 **[Ver demo en vivo](https://dashboard-analisis-datos.onrender.com)**

---

## ✨ ¿Qué hace?

Sube un archivo CSV o Excel y el dashboard genera automáticamente:

- 📈 Gráficos de líneas interactivos por columna numérica
- 📐 Estadísticas descriptivas: media, mediana, varianza, desviación estándar
- 🔮 Predicción de los próximos 5 valores con regresión lineal
- 📉 Detección de tendencia (creciente / decreciente) con coeficiente R²
- 🗓️ Detección automática de columnas de fecha para el eje temporal

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + Flask |
| Análisis | Pandas + NumPy |
| Predicción | Scikit-learn (LinearRegression) |
| Gráficos | Chart.js 4 |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Deploy | Render (free tier) |

## 🚀 Correr localmente
```bash
git clone https://github.com/Sagiiiii/dashboard-analisis-datos.git
cd dashboard-analisis-datos
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run.py
```

Abre http://127.0.0.1:5000 y sube cualquier CSV.

## 📁 Ejemplo de CSV compatible
```csv
fecha,ventas,gastos,clientes
2024-01,1500,900,120
2024-02,1800,950,145
2024-03,2100,1000,160
```

## 👤 Autor

**Sagiii** — [Portfolio](https://sagiiiii-portfolio.onrender.com) · [GitHub](https://github.com/Sagiiiii)
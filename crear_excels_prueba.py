import pandas as pd
import numpy as np

# ── EXCEL 1: Inventario con 1 sola hoja ──
df_inv = pd.DataFrame({
    'producto':    ['Laptop HP','Monitor LG','Teclado Logitech','Mouse Razer',
                    'Auriculares Sony','Webcam Logitech','SSD Samsung','RAM Corsair',
                    'Fuente EVGA','Gabinete NZXT'],
    'categoria':   ['Computadoras','Monitores','Periféricos','Periféricos',
                    'Audio','Periféricos','Almacenamiento','Memoria',
                    'Energía','Gabinetes'],
    'stock':       [45, 30, 120, 95, 60, 40, 200, 150, 80, 35],
    'precio_unit': [2500, 850, 180, 220, 350, 290, 320, 180, 250, 420],
    'vendidos_mes':[12, 8, 35, 28, 15, 10, 45, 38, 20, 6],
    'costo_unit':  [1800, 620, 120, 150, 240, 200, 210, 120, 170, 290],
})
df_inv.to_excel('inventario_tienda.xlsx', index=False)
print("✅ inventario_tienda.xlsx creado")

# ── EXCEL 2: Reporte multi-hoja (Ventas + RRHH + Producción) ──
with pd.ExcelWriter('reporte_empresa.xlsx', engine='openpyxl') as writer:

    # Hoja 1: Ventas por trimestre
    df_ventas = pd.DataFrame({
        'trimestre':    ['Q1-2023','Q2-2023','Q3-2023','Q4-2023',
                         'Q1-2024','Q2-2024','Q3-2024','Q4-2024'],
        'ingresos':     [85000, 92000, 98000, 125000, 91000, 107000, 115000, 142000],
        'costos':       [52000, 57000, 60000, 75000, 56000, 65000, 70000, 86000],
        'utilidad':     [33000, 35000, 38000, 50000, 35000, 42000, 45000, 56000],
        'clientes':     [320,   345,   380,   460,   350,   420,   445,   510],
        'meta_ingresos':[80000, 88000, 95000, 120000, 88000, 100000, 110000, 135000],
    })
    df_ventas.to_excel(writer, sheet_name='Ventas', index=False)

    # Hoja 2: RRHH
    df_rrhh = pd.DataFrame({
        'empleado':     ['Ana Torres','Carlos Quispe','María Flores','Pedro Mamani',
                         'Lucía Condori','Jorge Ticona','Rosa Vargas','Dante Ccoa'],
        'cargo':        ['Gerente','Analista','Desarrolladora','Contador',
                         'Diseñadora','Vendedor','RRHH','DevOps'],
        'departamento': ['Gerencia','TI','TI','Finanzas',
                         'Marketing','Ventas','RRHH','TI'],
        'salario':      [8500, 4200, 4800, 3900, 3500, 2800, 3200, 5100],
        'años_empresa': [8, 3, 5, 6, 2, 4, 7, 1],
        'evaluacion':   [95, 88, 92, 85, 90, 78, 87, 82],
        'ausencias_mes':[0, 1, 0, 2, 0, 3, 1, 0],
    })
    df_rrhh.to_excel(writer, sheet_name='RRHH', index=False)

    # Hoja 3: Producción
    df_prod = pd.DataFrame({
        'semana':          ['S01','S02','S03','S04','S05','S06','S07','S08',
                            'S09','S10','S11','S12'],
        'unidades_meta':   [1000,1000,1100,1100,1200,1200,1300,1300,
                            1400,1400,1500,1500],
        'unidades_prod':   [980, 1020,1085,1110,1195,1230,1280,1315,
                            1390,1420,1480,1510],
        'defectos':        [12,  8,   15,  9,   6,   11,  7,   5,
                            8,   4,   6,   3],
        'horas_maquina':   [168, 168, 176, 176, 184, 184, 192, 192,
                            200, 200, 208, 208],
        'eficiencia_pct':  [98.0,99.2,98.6,99.1,99.5,99.1,99.5,99.6,
                            99.4,99.7,99.6,99.8],
        'costo_produccion':[45000,46200,50200,51300,56800,57400,62400,63100,
                            68500,69200,74800,75200],
    })
    df_prod.to_excel(writer, sheet_name='Produccion', index=False)

print("✅ reporte_empresa.xlsx creado (3 hojas: Ventas, RRHH, Produccion)")

# ── EXCEL 3: Salud — datos de pacientes ──
np.random.seed(42)
n = 50
df_salud = pd.DataFrame({
    'paciente_id':  [f'PAC-{i:03d}' for i in range(1, n+1)],
    'edad':         np.random.randint(18, 75, n),
    'peso_kg':      np.round(np.random.normal(68, 12, n), 1),
    'altura_cm':    np.random.randint(155, 185, n),
    'presion_sis':  np.random.randint(110, 160, n),
    'presion_dia':  np.random.randint(70, 100, n),
    'glucosa':      np.round(np.random.normal(95, 18, n), 1),
    'colesterol':   np.round(np.random.normal(185, 30, n), 1),
    'frecuencia_c': np.random.randint(60, 95, n),
    'imc':          np.round(np.random.normal(24.5, 3.5, n), 2),
})
df_salud.to_excel('datos_pacientes.xlsx', index=False)
print("✅ datos_pacientes.xlsx creado (50 pacientes)")

print("\n🎉 Todos los archivos están listos para subir al dashboard.")
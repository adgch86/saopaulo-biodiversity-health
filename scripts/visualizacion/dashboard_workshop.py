#!/usr/bin/env python
"""
Dashboard Prototipo - Herramienta de Monitoreo Municipal
Proyecto: Resilient Landscapes - São Paulo

Workshop: Febrero 2026
Autor: Science Team / Dr. Adrian David González Chaves
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "outputs", "municipios_integrado_v5.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "dashboard_mockups")

# Crear directorio de salida
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cargar datos
print("Cargando datos...")
df = pd.read_csv(DATA_PATH)

# =============================================================================
# CLASIFICACIÓN DE MUNICIPIOS POR CUADRANTES DE RIESGO
# =============================================================================

def clasificar_municipios(df):
    """Clasifica municipios en cuadrantes basados en gobernanza y vulnerabilidad."""

    # Calcular medianas
    med_gob = df['idx_gobernanza'].median()
    med_vuln = df['idx_vulnerabilidad'].median()

    def asignar_cuadrante(row):
        alta_gob = row['idx_gobernanza'] >= med_gob
        alta_vuln = row['idx_vulnerabilidad'] >= med_vuln

        if alta_gob and not alta_vuln:
            return "Q1_Modelo"
        elif not alta_gob and not alta_vuln:
            return "Q2_Conservar"
        elif not alta_gob and alta_vuln:
            return "Q3_Vulnerable"  # PRIORIDAD
        else:
            return "Q4_Desarrollo"

    df['cuadrante'] = df.apply(asignar_cuadrante, axis=1)
    return df

df = clasificar_municipios(df)

# Colores por cuadrante
COLORES_CUADRANTE = {
    "Q1_Modelo": "#2ecc71",      # Verde - Modelo a seguir
    "Q2_Conservar": "#3498db",   # Azul - Conservar
    "Q3_Vulnerable": "#e74c3c",  # Rojo - Prioridad de intervención
    "Q4_Desarrollo": "#f39c12"   # Naranja - En desarrollo
}

# =============================================================================
# FIGURA 1: DASHBOARD PRINCIPAL - CUADRANTES DE RIESGO
# =============================================================================

def crear_dashboard_cuadrantes():
    """Crea el dashboard principal de clasificación de municipios."""

    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"colspan": 2}, None],
               [{"type": "domain"}, {"type": "bar"}]],
        subplot_titles=(
            "Clasificación de Municipios: Gobernanza vs Vulnerabilidad",
            "Distribución por Cuadrante",
            "Indicadores Promedio por Cuadrante"
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # Panel 1: Scatter plot de cuadrantes
    for cuad, color in COLORES_CUADRANTE.items():
        df_cuad = df[df['cuadrante'] == cuad]
        fig.add_trace(
            go.Scatter(
                x=df_cuad['idx_gobernanza'] * 100,
                y=df_cuad['idx_vulnerabilidad'],
                mode='markers',
                name=cuad.replace("_", " "),
                marker=dict(
                    size=8,
                    color=color,
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=df_cuad['Municipio'],
                hovertemplate="<b>%{text}</b><br>" +
                              "Gobernanza: %{x:.1f}%<br>" +
                              "Vulnerabilidad: %{y:.1f}<br>" +
                              "<extra></extra>"
            ),
            row=1, col=1
        )

    # Líneas de referencia (medianas)
    med_gob = df['idx_gobernanza'].median() * 100
    med_vuln = df['idx_vulnerabilidad'].median()

    fig.add_hline(y=med_vuln, line_dash="dash", line_color="gray",
                  annotation_text="Mediana Vulnerabilidad", row=1, col=1)
    fig.add_vline(x=med_gob, line_dash="dash", line_color="gray",
                  annotation_text="Mediana Gobernanza", row=1, col=1)

    # Panel 2: Pie chart de distribución
    conteo = df['cuadrante'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=[c.replace("_", " ") for c in conteo.index],
            values=conteo.values,
            marker=dict(colors=[COLORES_CUADRANTE[c] for c in conteo.index]),
            textinfo='label+percent',
            hole=0.4
        ),
        row=2, col=1
    )

    # Panel 3: Barras de indicadores por cuadrante
    indicadores = ['idx_biodiv', 'idx_clima', 'idx_carga_enfermedad']
    nombres_ind = ['Biodiversidad', 'Riesgo Climático', 'Carga Enfermedad']

    for cuad, color in COLORES_CUADRANTE.items():
        valores = df[df['cuadrante'] == cuad][indicadores].mean().values
        fig.add_trace(
            go.Bar(
                name=cuad.replace("_", " "),
                x=nombres_ind,
                y=valores,
                marker_color=color,
                showlegend=False
            ),
            row=2, col=2
        )

    fig.update_layout(
        height=800,
        title=dict(
            text="<b>🌿 Monitor Municipal de Resiliencia - São Paulo</b><br>" +
                 "<sup>Herramienta de apoyo a decisiones para adaptación climática</sup>",
            font=dict(size=20)
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.52,
            xanchor="center",
            x=0.5
        ),
        barmode='group'
    )

    fig.update_xaxes(title_text="Índice de Gobernanza (%)", row=1, col=1)
    fig.update_yaxes(title_text="Índice de Vulnerabilidad", row=1, col=1)

    return fig


# =============================================================================
# FIGURA 2: NEXO CLIMA-BIODIVERSIDAD-SALUD
# =============================================================================

def crear_nexo_correlaciones():
    """Visualiza las correlaciones del nexo multidimensional."""

    # Matriz de correlación
    vars_nexo = ['idx_clima', 'idx_biodiv', 'idx_vulnerabilidad',
                 'idx_carga_enfermedad', 'idx_gobernanza']
    nombres = ['Riesgo\nClimático', 'Biodiversidad', 'Vulnerabilidad',
               'Carga\nEnfermedad', 'Gobernanza']

    corr_matrix = df[vars_nexo].corr()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Matriz de Correlaciones del Nexo",
            "Efecto Dilución: Biodiversidad vs Enfermedades"
        ),
        column_widths=[0.5, 0.5]
    )

    # Heatmap de correlaciones
    fig.add_trace(
        go.Heatmap(
            z=corr_matrix.values,
            x=nombres,
            y=nombres,
            colorscale='RdBu_r',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="Correlación", x=0.45)
        ),
        row=1, col=1
    )

    # Scatter: Biodiversidad vs Carga de enfermedad
    fig.add_trace(
        go.Scatter(
            x=df['idx_biodiv'],
            y=df['idx_carga_enfermedad'],
            mode='markers',
            marker=dict(
                size=8,
                color=df['idx_vulnerabilidad'],
                colorscale='YlOrRd',
                showscale=True,
                colorbar=dict(title="Vulnerabilidad", x=1.02)
            ),
            text=df['Municipio'],
            hovertemplate="<b>%{text}</b><br>" +
                          "Biodiversidad: %{x:.1f}<br>" +
                          "Carga Enfermedad: %{y:.1f}<br>" +
                          "<extra></extra>"
        ),
        row=1, col=2
    )

    # Línea de tendencia
    z = np.polyfit(df['idx_biodiv'].dropna(),
                   df.loc[df['idx_biodiv'].notna(), 'idx_carga_enfermedad'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(df['idx_biodiv'].min(), df['idx_biodiv'].max(), 100)

    fig.add_trace(
        go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            line=dict(color='red', dash='dash', width=2),
            name='Tendencia',
            showlegend=False
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=500,
        title=dict(
            text="<b>🔗 Nexo Clima-Biodiversidad-Salud-Gobernanza</b><br>" +
                 "<sup>Correlaciones entre dimensiones del sistema agroalimentario</sup>",
            font=dict(size=18)
        )
    )

    fig.update_xaxes(title_text="Índice de Biodiversidad", row=1, col=2)
    fig.update_yaxes(title_text="Carga de Enfermedad", row=1, col=2)

    return fig


# =============================================================================
# FIGURA 3: PANEL DE MUNICIPIOS PRIORITARIOS
# =============================================================================

def crear_panel_prioritarios():
    """Panel mostrando los municipios que requieren intervención urgente."""

    # Filtrar Q3 (vulnerables con baja gobernanza)
    df_q3 = df[df['cuadrante'] == 'Q3_Vulnerable'].copy()
    df_q3['brecha'] = df_q3['idx_vulnerabilidad'] - (df_q3['idx_gobernanza'] * 100)
    df_q3 = df_q3.nlargest(15, 'brecha')

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "xy"}, {"type": "polar"}]],
        subplot_titles=(
            "Top 15 Municipios Prioritarios (Mayor Brecha)",
            "Perfil de Riesgos Acumulados"
        ),
        column_widths=[0.6, 0.4]
    )

    # Barras horizontales de brecha
    fig.add_trace(
        go.Bar(
            y=df_q3['Municipio'],
            x=df_q3['idx_vulnerabilidad'],
            name='Vulnerabilidad',
            orientation='h',
            marker_color='#e74c3c',
            text=df_q3['idx_vulnerabilidad'].round(1),
            textposition='inside'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            y=df_q3['Municipio'],
            x=df_q3['idx_gobernanza'] * 100,
            name='Gobernanza',
            orientation='h',
            marker_color='#3498db',
            text=(df_q3['idx_gobernanza'] * 100).round(1),
            textposition='inside'
        ),
        row=1, col=1
    )

    # Radar de riesgos promedio Q3
    categorias = ['Climático', 'Salud', 'Pobreza', 'Biodiv\n(inverso)', 'Gobernanza\n(inverso)']

    # Calcular valores normalizados (0-1) para el radar
    q3_mean = df_q3[['idx_clima', 'idx_carga_enfermedad', 'idx_vulnerabilidad',
                      'idx_biodiv', 'idx_gobernanza']].mean()

    valores_radar = [
        q3_mean['idx_clima'] / 100,
        q3_mean['idx_carga_enfermedad'] / df['idx_carga_enfermedad'].max(),
        q3_mean['idx_vulnerabilidad'] / 100,
        1 - (q3_mean['idx_biodiv'] / 100),  # Invertido: menor biodiv = mayor riesgo
        1 - q3_mean['idx_gobernanza']  # Invertido: menor gobernanza = mayor riesgo
    ]

    fig.add_trace(
        go.Scatterpolar(
            r=valores_radar + [valores_radar[0]],  # Cerrar el polígono
            theta=categorias + [categorias[0]],
            fill='toself',
            fillcolor='rgba(231, 76, 60, 0.3)',
            line=dict(color='#e74c3c', width=2),
            name='Q3 Vulnerables'
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=600,
        title=dict(
            text="<b>⚠️ Municipios Prioritarios para Intervención</b><br>" +
                 "<sup>Cuadrante Q3: Alta vulnerabilidad + Baja gobernanza</sup>",
            font=dict(size=18)
        ),
        barmode='group',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.3
        )
    )

    fig.update_xaxes(title_text="Índice (0-100)", row=1, col=1)

    return fig


# =============================================================================
# FIGURA 4: RECOMENDACIONES PEAC POR PERFIL
# =============================================================================

def crear_panel_recomendaciones():
    """Panel de recomendaciones basadas en el PEAC por perfil de municipio."""

    # Definir acciones PEAC por tipo de riesgo
    acciones_peac = {
        "Alto Riesgo Climático": [
            "Sistemas de alerta temprana",
            "Infraestructura verde urbana",
            "Planes de contingencia hídrica",
            "Reforestación de cuencas"
        ],
        "Alta Carga de Enfermedad": [
            "Vigilancia epidemiológica",
            "Control vectorial integrado",
            "Saneamiento básico",
            "Corredores ecológicos (efecto dilución)"
        ],
        "Alta Vulnerabilidad Social": [
            "Programas de agricultura urbana",
            "Capacitación técnica",
            "Acceso a crédito verde",
            "Fortalecimiento institucional"
        ],
        "Baja Biodiversidad": [
            "Restauración de hábitats",
            "Conectividad de fragmentos",
            "Agricultura regenerativa",
            "Protección de remanentes"
        ]
    }

    # Crear tabla visual
    fig = go.Figure()

    # Encabezados
    categorias = list(acciones_peac.keys())
    colores_cat = ['#e74c3c', '#9b59b6', '#f39c12', '#27ae60']

    for i, (cat, acciones) in enumerate(acciones_peac.items()):
        # Rectángulo de encabezado
        fig.add_shape(
            type="rect",
            x0=i, x1=i+0.9,
            y0=4.5, y1=5,
            fillcolor=colores_cat[i],
            line=dict(width=0)
        )

        # Texto encabezado
        fig.add_annotation(
            x=i+0.45, y=4.75,
            text=f"<b>{cat}</b>",
            showarrow=False,
            font=dict(color='white', size=10)
        )

        # Acciones
        for j, accion in enumerate(acciones):
            fig.add_annotation(
                x=i+0.45, y=3.5-j,
                text=f"• {accion}",
                showarrow=False,
                font=dict(size=9),
                align='left'
            )

    fig.update_layout(
        height=400,
        title=dict(
            text="<b>📋 Matriz de Acciones PEAC por Perfil de Riesgo</b><br>" +
                 "<sup>Recomendaciones del Plan Estadual de Acción Climática</sup>",
            font=dict(size=18)
        ),
        xaxis=dict(visible=False, range=[-0.2, 4]),
        yaxis=dict(visible=False, range=[0, 5.5]),
        plot_bgcolor='white'
    )

    return fig


# =============================================================================
# FIGURA 5: RESUMEN EJECUTIVO
# =============================================================================

def crear_resumen_ejecutivo():
    """Crea un panel de resumen ejecutivo con KPIs principales."""

    fig = make_subplots(
        rows=2, cols=3,
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
        vertical_spacing=0.3
    )

    # KPIs
    n_total = len(df)
    n_q3 = len(df[df['cuadrante'] == 'Q3_Vulnerable'])
    corr_biodiv_salud = df['idx_biodiv'].corr(df['idx_carga_enfermedad'])
    prom_vuln = df['idx_vulnerabilidad'].mean()
    prom_gob = df['idx_gobernanza'].mean() * 100
    n_alto_clima = len(df[df['idx_clima'] > 70])

    indicadores = [
        (n_total, "Municipios Analizados", None, "number"),
        (n_q3, "Municipios Prioritarios (Q3)", f"{n_q3/n_total*100:.0f}% del total", "number"),
        (corr_biodiv_salud, "Corr. Biodiv-Salud", "Efecto dilución confirmado", "number"),
        (prom_vuln, "Vulnerabilidad Promedio", "Escala 0-100", "gauge"),
        (prom_gob, "Gobernanza Promedio", "Escala 0-100%", "gauge"),
        (n_alto_clima, "Alto Riesgo Climático", f"{n_alto_clima/n_total*100:.0f}% del total", "number"),
    ]

    posiciones = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3)]

    for (valor, titulo, subtitulo, tipo), (row, col) in zip(indicadores, posiciones):
        if tipo == "gauge":
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=valor,
                    title={"text": titulo, "font": {"size": 14}},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#3498db"},
                        "steps": [
                            {"range": [0, 33], "color": "#2ecc71"},
                            {"range": [33, 66], "color": "#f39c12"},
                            {"range": [66, 100], "color": "#e74c3c"}
                        ]
                    }
                ),
                row=row, col=col
            )
        else:
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=valor,
                    title={"text": titulo, "font": {"size": 14}},
                    number={"font": {"size": 40}, "valueformat": ".2f" if abs(valor) < 10 else ".0f"}
                ),
                row=row, col=col
            )

    fig.update_layout(
        height=500,
        title=dict(
            text="<b>📊 Resumen Ejecutivo - Estado de São Paulo</b><br>" +
                 "<sup>Indicadores clave del sistema agroalimentario municipal</sup>",
            font=dict(size=20)
        )
    )

    return fig


# =============================================================================
# GENERAR Y GUARDAR TODAS LAS FIGURAS
# =============================================================================

def main():
    """Genera todas las figuras del dashboard."""

    print("\n" + "="*60)
    print("GENERANDO DASHBOARD DE MONITOREO MUNICIPAL")
    print("="*60 + "\n")

    figuras = [
        ("01_dashboard_cuadrantes", crear_dashboard_cuadrantes),
        ("02_nexo_correlaciones", crear_nexo_correlaciones),
        ("03_municipios_prioritarios", crear_panel_prioritarios),
        ("04_recomendaciones_peac", crear_panel_recomendaciones),
        ("05_resumen_ejecutivo", crear_resumen_ejecutivo),
    ]

    for nombre, func in figuras:
        print(f"Generando: {nombre}...")
        fig = func()

        # Guardar como HTML interactivo
        html_path = os.path.join(OUTPUT_DIR, f"{nombre}.html")
        fig.write_html(html_path)
        print(f"  [OK] HTML: {html_path}")

        # Guardar como PNG (screenshot para workshop)
        png_path = os.path.join(OUTPUT_DIR, f"{nombre}.png")
        try:
            fig.write_image(png_path, scale=2)
            print(f"  [OK] PNG: {png_path}")
        except Exception as e:
            print(f"  [WARN] Error exportando PNG: {e}")

    print("\n" + "="*60)
    print("DASHBOARD GENERADO EXITOSAMENTE")
    print("="*60)
    print(f"\nArchivos en: {OUTPUT_DIR}")
    print("\nPara ver el dashboard interactivo, abre los archivos .html")
    print("Para el workshop, usa los archivos .png como screenshots\n")

    # Generar tabla de municipios prioritarios
    df_q3 = df[df['cuadrante'] == 'Q3_Vulnerable'].copy()
    df_q3['brecha'] = df_q3['idx_vulnerabilidad'] - (df_q3['idx_gobernanza'] * 100)
    df_prioritarios = df_q3.nlargest(20, 'brecha')[
        ['Municipio', 'idx_vulnerabilidad', 'idx_gobernanza', 'idx_biodiv',
         'idx_clima', 'idx_carga_enfermedad', 'brecha']
    ]

    csv_path = os.path.join(OUTPUT_DIR, "municipios_prioritarios_top20.csv")
    df_prioritarios.to_csv(csv_path, index=False)
    print(f"Lista de municipios prioritarios: {csv_path}")


if __name__ == "__main__":
    main()

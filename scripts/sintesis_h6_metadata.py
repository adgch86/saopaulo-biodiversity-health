"""
Analisis H6 - Actualizacion de Metadata y Sintesis

6.1: Actualizar DATA_METHODOLOGY.md con descripcion de cada variable y fuente
6.2: Organizar variables segun diagramas de Adrian:
     - Diagrama 1: 5 Dimensiones del Nexus
     - Diagrama 2: 3 Componentes de Riesgo (IPCC/costero)
6.3: Tabla de mejores predictores por frecuencia en modelos seleccionados

Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)
Autor: Science Team / AP Digital
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import Counter
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h6_sintesis")
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# VARIABLE DEFINITIONS
# ============================================================

# Diagrama 1: 5 Dimensiones del Nexus
NEXUS_DIMENSIONS = {
    'Gobernanza': {
        'description': 'Capacidad adaptativa institucional y gestion publica',
        'variables': {
            'UAI_housing': {'label': 'UAI Vivienda', 'source': 'Neder et al. 2021', 'unit': '0-1'},
            'UAI_env': {'label': 'UAI Ambiental', 'source': 'Neder et al. 2021', 'unit': '0-1'},
            'UAI_food': {'label': 'UAI Alimentacion', 'source': 'Neder et al. 2021', 'unit': '0-1'},
            'UAI_mob': {'label': 'UAI Movilidad', 'source': 'Neder et al. 2021', 'unit': '0-1'},
            'UAI_Crisk': {'label': 'UAI Riesgo Climatico', 'source': 'Neder et al. 2021', 'unit': '0-1'},
            'idx_gobernanza': {'label': 'Indice Gobernanza', 'source': 'Calculado', 'unit': '0-1',
                              'formula': 'mean(UAI_housing, UAI_env, UAI_food, UAI_mob, UAI_Crisk)'},
        }
    },
    'Biodiversidad': {
        'description': 'Estado de ecosistemas y servicios ecosistemicos',
        'variables': {
            'forest_cover': {'label': 'Cobertura Forestal', 'source': 'MapBiomas', 'unit': '%'},
            'mean_species_richness': {'label': 'Riqueza Especies', 'source': 'Biodiversity data', 'unit': 'n especies'},
            'max_species_richness': {'label': 'Riqueza Max Especies', 'source': 'Biodiversity data', 'unit': 'n especies'},
            'pol_deficit': {'label': 'Deficit Polinizacion', 'source': 'Calculated', 'unit': '0-1'},
            'idx_biodiv': {'label': 'Indice Biodiversidad', 'source': 'Calculado', 'unit': '0-100',
                          'formula': 'normalized(forest_cover + mean_species_richness - pol_deficit)'},
        }
    },
    'Riesgo_Climatico': {
        'description': 'Exposicion a amenazas climaticas',
        'variables': {
            'flooding_risks': {'label': 'Riesgo Inundacion', 'source': 'CEMADEN', 'unit': '0-1'},
            'flooding_exposure': {'label': 'Exposicion Inundacion', 'source': 'CEMADEN', 'unit': '0-1'},
            'fire_risk_index': {'label': 'Riesgo Fuego', 'source': 'INPE Queimadas', 'unit': '0-100'},
            'fire_incidence_mean': {'label': 'Incidencia Fuego', 'source': 'INPE Queimadas', 'unit': 'focos/ano'},
            'hydric_stress_risk': {'label': 'Estres Hidrico', 'source': 'ANA', 'unit': '0-1'},
            'idx_clima': {'label': 'Indice Riesgo Clima', 'source': 'Calculado', 'unit': '0-100',
                         'formula': 'normalized(flooding_risks + fire_risk_index + hydric_stress_risk)'},
        }
    },
    'Riesgo_Salud': {
        'description': 'Carga de enfermedad y morbimortalidad',
        'variables': {
            'incidence_mean_dengue': {'label': 'Incidencia Dengue', 'source': 'DATASUS SINAN', 'unit': 'casos/100k/ano'},
            'incidence_mean_malaria': {'label': 'Incidencia Malaria', 'source': 'DATASUS SINAN', 'unit': 'casos/100k/ano'},
            'incidence_mean_leishmaniose': {'label': 'Incidencia Leishmaniasis', 'source': 'DATASUS SINAN', 'unit': 'casos/100k/ano'},
            'incidence_mean_leptospirose': {'label': 'Incidencia Leptospirosis', 'source': 'DATASUS SINAN', 'unit': 'casos/100k/ano'},
            'incidence_diarrhea_mean': {'label': 'Incidencia Diarrea', 'source': 'DATASUS SIH', 'unit': 'casos/100k/ano'},
            'health_death_circ_mean': {'label': 'Mortalidad Cardiovascular', 'source': 'DATASUS SIM', 'unit': 'muertes/100k/ano'},
            'health_hosp_resp_mean': {'label': 'Hospitalizacion Respiratoria', 'source': 'DATASUS SIH', 'unit': 'hosp/100k/ano'},
            'idx_carga_enfermedad': {'label': 'Indice Carga Enfermedad', 'source': 'Calculado', 'unit': '0-100'},
        }
    },
    'Vulnerabilidad_Social': {
        'description': 'Sensibilidad y capacidad adaptativa social',
        'variables': {
            'pct_pobreza': {'label': '% Pobreza', 'source': 'IBGE Censo', 'unit': '%'},
            'pct_rural': {'label': '% Rural', 'source': 'IBGE Censo', 'unit': '%'},
            'pct_preta': {'label': '% Poblacion Negra', 'source': 'IBGE Censo', 'unit': '%'},
            'pct_indigena': {'label': '% Poblacion Indigena', 'source': 'IBGE Censo', 'unit': '%'},
            'idx_vulnerabilidad': {'label': 'Indice Vulnerabilidad', 'source': 'Calculado', 'unit': '0-100',
                                  'formula': 'normalized(pct_pobreza + pct_rural + pct_preta + pct_indigena)'},
        }
    }
}

# Diagrama 2: 3 Componentes de Riesgo (IPCC AR5/6)
RISK_COMPONENTS = {
    'HAZARD': {
        'definition': 'Evento fisico peligroso o tendencia climatica',
        'variables': {
            'flooding_exposure': 'Exposicion a inundaciones',
            'fire_incidence_mean': 'Incidencia de incendios',
            'hydric_stress_exp': 'Exposicion a estres hidrico',
            'fire_risk_index': 'Indice riesgo fuego',
        }
    },
    'EXPOSURE': {
        'definition': 'Poblacion, activos o ecosistemas en zona de riesgo',
        'variables': {
            'population': 'Poblacion total',
            'pct_rural': 'Proporcion rural',
            'pct_urbana': 'Proporcion urbana',
        }
    },
    'VULNERABILITY': {
        'definition': 'Propension a ser afectado adversamente',
        'subcomponents': {
            'Sensitivity': {
                'description': 'Grado de afectacion por exposicion',
                'variables': ['pct_pobreza', 'pct_preta', 'pct_indigena']
            },
            'Adaptive_Capacity_Natural': {
                'description': 'Capacidad natural de mitigacion',
                'variables': ['forest_cover', 'mean_species_richness']
            },
            'Adaptive_Capacity_Institutional': {
                'description': 'Capacidad institucional de adaptacion',
                'variables': ['UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk']
            }
        }
    }
}


# ============================================================
# SYNTHESIS FUNCTIONS
# ============================================================

def load_h1_h5_results():
    """Load results from H1-H5 analyses"""
    results = {}

    result_files = {
        'h1_best': os.path.join(BASE_DIR, 'outputs/h1_gobernanza/h1_best_by_dimension.csv'),
        'h2_interactions': os.path.join(BASE_DIR, 'outputs/h2_vulnerabilidad/h2_interactions.csv'),
        'h3_interactions': os.path.join(BASE_DIR, 'outputs/h3_clima_salud/h3_interactions.csv'),
        'h4_best': os.path.join(BASE_DIR, 'outputs/h4_salud/h4_best_predictors.csv'),
        'h5_best': os.path.join(BASE_DIR, 'outputs/h5_clima/h5_best_predictors.csv'),
    }

    for key, path in result_files.items():
        if os.path.exists(path):
            results[key] = pd.read_csv(path)
            print(f"  Loaded {key}: {len(results[key])} rows")
        else:
            print(f"  [SKIP] {key} not found at {path}")

    return results


def compute_predictor_frequency(results):
    """Count how often each variable appears as best predictor"""
    all_predictors = []

    if 'h1_best' in results:
        all_predictors.extend(results['h1_best']['best_predictor'].tolist())
    if 'h4_best' in results:
        all_predictors.extend(results['h4_best']['best_predictor'].tolist())
    if 'h5_best' in results:
        all_predictors.extend(results['h5_best']['best_predictor'].tolist())

    freq = Counter(all_predictors)
    freq_df = pd.DataFrame([
        {'variable': var, 'frequency': count}
        for var, count in freq.most_common()
    ])

    return freq_df


def generate_variable_table():
    """Generate comprehensive variable table"""
    rows = []

    for dim_key, dim_data in NEXUS_DIMENSIONS.items():
        for var, var_data in dim_data['variables'].items():
            row = {
                'variable': var,
                'label': var_data['label'],
                'dimension_nexus': dim_key,
                'source': var_data['source'],
                'unit': var_data['unit'],
                'formula': var_data.get('formula', ''),
            }

            # Map to risk component
            for comp_key, comp_data in RISK_COMPONENTS.items():
                if comp_key in ['HAZARD', 'EXPOSURE']:
                    if var in comp_data['variables']:
                        row['risk_component'] = comp_key
                        break
                elif comp_key == 'VULNERABILITY':
                    for subcomp, subdata in comp_data['subcomponents'].items():
                        if var in subdata['variables']:
                            row['risk_component'] = f'VULNERABILITY/{subcomp}'
                            break

            if 'risk_component' not in row:
                row['risk_component'] = ''

            rows.append(row)

    return pd.DataFrame(rows)


def generate_metadata_markdown(var_table, freq_df):
    """Generate updated DATA_METHODOLOGY.md content"""

    md = """# Datos y Metodologia - Science Team

> Este archivo documenta las fuentes de datos, procesamiento y metodologia.
> Para contexto actual: `SCIENCE_TEAM_CONTEXT.md`
> **Actualizado automaticamente por H6 - {date}**

---

## Marco Conceptual

### Diagrama 1: 5 Dimensiones del Nexus (Levers et al. 2025)

```
         Gobernanza <---> Biodiversidad
              |               |
              v               v
        Riesgo Salud <---> Riesgo Climatico
                  \\       /
                   \\     /
                    \\   /
             Vulnerabilidad Social
                  (central)
```

### Diagrama 2: 3 Componentes de Riesgo (IPCC AR5/AR6)

| Componente | Definicion | Ejemplos |
|------------|------------|----------|
| **HAZARD** | Evento fisico peligroso | flooding_exposure, fire_incidence |
| **EXPOSURE** | Poblacion en zona de riesgo | population, pct_rural |
| **VULNERABILITY** | Propension a dano | Sensibilidad + Capacidad Adaptativa |

**Subcomponentes de Vulnerabilidad:**
- Sensibilidad: pct_pobreza, pct_preta, pct_indigena
- Capacidad Adaptativa Natural: forest_cover, biodiversity
- Capacidad Adaptativa Institucional: UAI components

---

## Catalogo de Variables

""".format(date=datetime.now().strftime('%Y-%m-%d'))

    # Add variables by dimension
    for dim_key, dim_data in NEXUS_DIMENSIONS.items():
        md += f"\n### {dim_key.replace('_', ' ')}\n\n"
        md += f"*{dim_data['description']}*\n\n"
        md += "| Variable | Label | Fuente | Unidad |\n"
        md += "|----------|-------|--------|--------|\n"

        for var, var_data in dim_data['variables'].items():
            md += f"| `{var}` | {var_data['label']} | {var_data['source']} | {var_data['unit']} |\n"

    # Add frequency table
    md += """
---

## Mejores Predictores (Frecuencia H1-H5)

| Variable | Frecuencia como Mejor Predictor |
|----------|--------------------------------|
"""
    for _, row in freq_df.head(15).iterrows():
        md += f"| `{row['variable']}` | {row['frequency']} |\n"

    # Add data sources
    md += """
---

## Fuentes de Datos

### DATASUS
- **SINAN**: Enfermedades de notificacion obligatoria (dengue, malaria, etc.)
- **SIH**: Sistema de Informaciones Hospitalarias
- **SIM**: Sistema de Informacion sobre Mortalidad

### IBGE
- **Censo**: Datos demograficos y socioeconomicos
- **SIDRA**: API para series temporales

### Otros
- **INPE Queimadas**: Focos de calor e incendios
- **CEMADEN**: Riesgos hidrologicos
- **MapBiomas**: Cobertura del suelo

---

## Estructura Jerarquica

```
Municipio (n=645) --> Microrregiao (n=63) --> Mesorregiao (n=15)
```

Efectos aleatorios: `(1|cod_microrregiao)` obligatorio en modelos mixtos.

---

*Generado por sintesis_h6_metadata.py*
"""

    return md


# ============================================================
# VISUALIZATIONS
# ============================================================

def plot_nexus_diagram(filename):
    """Create nexus dimension diagram"""
    print(f"\n  Generating nexus diagram...")

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Positions for 5 dimensions
    positions = {
        'Gobernanza': (2, 8),
        'Biodiversidad': (8, 8),
        'Riesgo_Salud': (2, 4),
        'Riesgo_Climatico': (8, 4),
        'Vulnerabilidad_Social': (5, 1.5)
    }

    colors = {
        'Gobernanza': '#4a86e8',
        'Biodiversidad': '#1a9850',
        'Riesgo_Salud': '#d73027',
        'Riesgo_Climatico': '#fc8d59',
        'Vulnerabilidad_Social': '#756bb1'
    }

    # Draw nodes
    for dim, (x, y) in positions.items():
        circle = plt.Circle((x, y), 1.2, color=colors[dim], alpha=0.7)
        ax.add_patch(circle)
        ax.text(x, y, dim.replace('_', '\n'), ha='center', va='center',
               fontsize=10, fontweight='bold', color='white')

    # Draw edges (bidirectional)
    edges = [
        ('Gobernanza', 'Biodiversidad'),
        ('Gobernanza', 'Riesgo_Salud'),
        ('Biodiversidad', 'Riesgo_Climatico'),
        ('Riesgo_Salud', 'Riesgo_Climatico'),
        ('Riesgo_Salud', 'Vulnerabilidad_Social'),
        ('Riesgo_Climatico', 'Vulnerabilidad_Social'),
        ('Gobernanza', 'Vulnerabilidad_Social'),
        ('Biodiversidad', 'Vulnerabilidad_Social'),
    ]

    for dim1, dim2 in edges:
        x1, y1 = positions[dim1]
        x2, y2 = positions[dim2]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='<->', color='gray', lw=2,
                                  connectionstyle='arc3,rad=0.1'))

    ax.set_title('Diagrama 1: 5 Dimensiones del Nexus\n(Levers et al. 2025 adaptado)',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_risk_components(filename):
    """Create IPCC risk components diagram"""
    print(f"\n  Generating risk components diagram...")

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Draw three main components
    from matplotlib.patches import Rectangle, FancyBboxPatch

    # HAZARD
    hazard = FancyBboxPatch((1, 5), 3.5, 2.5, boxstyle='round,pad=0.1',
                           facecolor='#fc8d59', edgecolor='black', linewidth=2)
    ax.add_patch(hazard)
    ax.text(2.75, 6.5, 'HAZARD', ha='center', va='center',
           fontsize=12, fontweight='bold')
    ax.text(2.75, 5.7, 'Evento fisico\npeligroso', ha='center', va='center',
           fontsize=9)

    # EXPOSURE
    exposure = FancyBboxPatch((5.25, 5), 3.5, 2.5, boxstyle='round,pad=0.1',
                             facecolor='#91bfdb', edgecolor='black', linewidth=2)
    ax.add_patch(exposure)
    ax.text(7, 6.5, 'EXPOSURE', ha='center', va='center',
           fontsize=12, fontweight='bold')
    ax.text(7, 5.7, 'Poblacion/activos\nen riesgo', ha='center', va='center',
           fontsize=9)

    # VULNERABILITY (larger)
    vuln = FancyBboxPatch((9.5, 2), 4, 5.5, boxstyle='round,pad=0.1',
                         facecolor='#d73027', edgecolor='black', linewidth=2, alpha=0.3)
    ax.add_patch(vuln)
    ax.text(11.5, 7, 'VULNERABILITY', ha='center', va='center',
           fontsize=12, fontweight='bold')

    # Sub-components
    sens = FancyBboxPatch((9.7, 5.5), 3.6, 1.2, boxstyle='round,pad=0.05',
                         facecolor='#d73027', edgecolor='black', linewidth=1)
    ax.add_patch(sens)
    ax.text(11.5, 6.1, 'Sensibilidad', ha='center', va='center', fontsize=10, fontweight='bold')

    adapt_nat = FancyBboxPatch((9.7, 3.8), 3.6, 1.4, boxstyle='round,pad=0.05',
                               facecolor='#1a9850', edgecolor='black', linewidth=1)
    ax.add_patch(adapt_nat)
    ax.text(11.5, 4.5, 'Capacidad Adaptativa\n(Natural)', ha='center', va='center', fontsize=9)

    adapt_inst = FancyBboxPatch((9.7, 2.2), 3.6, 1.4, boxstyle='round,pad=0.05',
                                facecolor='#4a86e8', edgecolor='black', linewidth=1)
    ax.add_patch(adapt_inst)
    ax.text(11.5, 2.9, 'Capacidad Adaptativa\n(Institucional)', ha='center', va='center', fontsize=9)

    # RISK (result)
    risk = FancyBboxPatch((4, 0.5), 6, 1.5, boxstyle='round,pad=0.1',
                         facecolor='#756bb1', edgecolor='black', linewidth=3)
    ax.add_patch(risk)
    ax.text(7, 1.25, 'RIESGO = f(Hazard, Exposure, Vulnerability)', ha='center', va='center',
           fontsize=11, fontweight='bold', color='white')

    # Arrows to risk
    ax.annotate('', xy=(5, 1.25), xytext=(2.75, 5),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.annotate('', xy=(7, 2), xytext=(7, 5),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    ax.annotate('', xy=(9, 1.25), xytext=(11.5, 2.2),
               arrowprops=dict(arrowstyle='->', color='gray', lw=2))

    ax.set_title('Diagrama 2: 3 Componentes de Riesgo (IPCC AR5/AR6)',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


def plot_predictor_frequency(freq_df, filename):
    """Bar plot of predictor frequency"""
    print(f"\n  Generating predictor frequency plot...")

    fig, ax = plt.subplots(figsize=(12, 8))

    top_20 = freq_df.head(20)

    colors = []
    for var in top_20['variable']:
        if 'UAI' in var or 'gobernanza' in var:
            colors.append('#4a86e8')
        elif 'forest' in var or 'species' in var or 'biodiv' in var or 'pol_' in var:
            colors.append('#1a9850')
        elif 'flood' in var or 'fire' in var or 'hydric' in var or 'clima' in var:
            colors.append('#fc8d59')
        elif 'incidence' in var or 'health' in var or 'death' in var or 'hosp' in var:
            colors.append('#d73027')
        elif 'pct_' in var or 'vuln' in var:
            colors.append('#756bb1')
        else:
            colors.append('gray')

    ax.barh(range(len(top_20)), top_20['frequency'], color=colors, edgecolor='white')
    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels(top_20['variable'], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Frecuencia como Mejor Predictor', fontsize=11)
    ax.set_title('H6: Variables mas Frecuentes como Mejores Predictores (H1-H5)\n'
                 'Azul=Gobernanza, Verde=Biodiv, Naranja=Clima, Rojo=Salud, Morado=Vuln',
                 fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename), dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  [SAVED] {filename}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("ANALISIS H6 - SINTESIS Y METADATA")
    print("Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)")
    print("=" * 70)

    # Load previous results
    print("\n" + "=" * 70)
    print("CARGANDO RESULTADOS H1-H5")
    print("=" * 70)
    results = load_h1_h5_results()

    # Generate variable table
    print("\n" + "=" * 70)
    print("GENERANDO TABLA DE VARIABLES")
    print("=" * 70)
    var_table = generate_variable_table()
    var_table.to_csv(os.path.join(OUTPUT_DIR, 'variables_catalogo.csv'), index=False)
    print(f"  [SAVED] variables_catalogo.csv ({len(var_table)} variables)")

    # Compute predictor frequency
    freq_df = compute_predictor_frequency(results)
    freq_df.to_csv(os.path.join(OUTPUT_DIR, 'predictor_frequency.csv'), index=False)
    print(f"  [SAVED] predictor_frequency.csv")

    # Generate variable by dimension tables
    print("\n  Variables por Dimension Nexus:")
    for dim_key in NEXUS_DIMENSIONS.keys():
        dim_vars = var_table[var_table['dimension_nexus'] == dim_key]
        print(f"    {dim_key}: {len(dim_vars)} variables")

    # Generate variable by risk component tables
    print("\n  Variables por Componente de Riesgo:")
    for comp in ['HAZARD', 'EXPOSURE', 'VULNERABILITY']:
        comp_vars = var_table[var_table['risk_component'].str.startswith(comp)]
        print(f"    {comp}: {len(comp_vars)} variables")

    # Save dimension tables
    for dim_key in NEXUS_DIMENSIONS.keys():
        dim_vars = var_table[var_table['dimension_nexus'] == dim_key]
        dim_vars.to_csv(os.path.join(OUTPUT_DIR, f'variables_{dim_key.lower()}.csv'), index=False)

    # Visualizations
    print("\n" + "=" * 70)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 70)

    plot_nexus_diagram('h6_nexus_diagram.png')
    plot_risk_components('h6_risk_components.png')
    if len(freq_df) > 0:
        plot_predictor_frequency(freq_df, 'h6_predictor_frequency.png')

    # Generate metadata markdown
    print("\n" + "=" * 70)
    print("ACTUALIZANDO METADATA")
    print("=" * 70)

    md_content = generate_metadata_markdown(var_table, freq_df)

    # Save to outputs first
    md_path_output = os.path.join(OUTPUT_DIR, 'DATA_METHODOLOGY_updated.md')
    with open(md_path_output, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"  [SAVED] {md_path_output}")

    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN H6: SINTESIS")
    print("=" * 70)

    print(f"\n  Total variables catalogadas: {len(var_table)}")
    print(f"  Variables por dimension:")
    for dim_key in NEXUS_DIMENSIONS.keys():
        n = len(var_table[var_table['dimension_nexus'] == dim_key])
        print(f"    {dim_key}: {n}")

    if len(freq_df) > 0:
        print(f"\n  Top 5 predictores mas frecuentes:")
        for i, row in freq_df.head(5).iterrows():
            print(f"    {row['variable']}: {row['frequency']} veces")

    print("\n" + "=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    for f in sorted(os.listdir(OUTPUT_DIR)):
        print(f"  {f}")

    print("\nDone!")


if __name__ == "__main__":
    main()

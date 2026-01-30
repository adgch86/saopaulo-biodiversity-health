"""
Sintesis H6 - Metadata y Clasificacion de Variables
Actualiza DATA_METHODOLOGY.md con todas las variables y las clasifica segun:
1. 5 Dimensiones del Nexus (Governance, Biodiversity, Health risk, Climate hazards, Social vulnerability)
2. 3 Componentes de Riesgo IPCC (Hazard, Exposure, Vulnerability)

Solicitud: Dr. Adrian David Gonzalez Chaves (29/01/2026)
Autor: Science Team / AP Digital
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
import os

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = r"C:\Users\arlex\Documents\Adrian David"
CSV_PATH = os.path.join(BASE_DIR, "outputs/municipios_integrado_v8.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/h6_sintesis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# VARIABLE CLASSIFICATION
# ============================================================

# Clasificacion por las 5 Dimensiones del Nexus
NEXUS_DIMENSIONS = {
    'Identificadores': [
        'cod_ibge', 'Municipio', 'cod_microrregiao', 'nome_microrregiao',
        'cod_mesorregiao', 'nome_mesorregiao'
    ],
    'Gobernanza': [
        'UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk',
        'idx_gobernanza', 'idx_gobernanza_100', 'esgoto_tratado',
        'IDESP_ensino_medio'
    ],
    'Biodiversidad': [
        'mean_species_richness', 'max_species_richness', 'Vert_rich_risk',
        'forest_cover', 'pol_deficit', 'idx_biodiv', 'tercil_biodiv'
    ],
    'Riesgo_Climatico': [
        'flooding_exposure', 'flooding_risks', 'hydric_stress_exp',
        'hydric_stress_risk', 'idx_clima', 'tercil_clima',
        'fire_incidence_mean', 'fire_incidence_max', 'fire_frp_mean',
        'fire_frp_max', 'fire_total_foci', 'fire_frp_total',
        'fire_years_with_fire', 'fire_recurrence', 'fire_cv',
        'fire_dry_season_pct', 'fire_max_consecutive_years', 'fire_risk_index'
    ],
    'Riesgo_Salud': [
        'persist_dengue', 'persist_leishmaniose', 'persist_leptospirose',
        'persist_malaria', 'persist_diarrhea',
        'incidence_mean_dengue', 'incidence_mean_leishmaniose',
        'incidence_mean_leptospirose', 'incidence_mean_malaria',
        'incidence_diarrhea_mean',
        'incidence_max_dengue', 'incidence_max_leishmaniose',
        'incidence_max_leptospirose', 'incidence_max_malaria',
        'incidence_diarrhea_max',
        'total_cases_dengue', 'total_cases_leishmaniose',
        'total_cases_leptospirose', 'total_cases_malaria',
        'total_cases_diarrhea',
        'copresence_years', 'copresence_3plus', 'copresence_all4',
        'dengue_leptospirose', 'dengue_malaria', 'dengue_leishmaniose',
        'leptospirose_malaria', 'leptospirose_leishmaniose', 'malaria_leishmaniose',
        'health_hosp_circ_mean', 'health_hosp_resp_mean', 'health_hosp_heat_mean',
        'health_hosp_circ_max', 'health_hosp_resp_max', 'health_hosp_heat_max',
        'health_total_hosp_circ', 'health_total_hosp_resp', 'health_total_hosp_heat',
        'health_death_circ_mean', 'health_death_resp_mean', 'health_death_heat_mean',
        'health_death_circ_max', 'health_death_resp_max', 'health_death_heat_max',
        'health_total_death_circ', 'health_total_death_resp', 'health_total_death_heat',
        'idx_carga_enfermedad', 'mort_infantil'
    ],
    'Vulnerabilidad_Social': [
        'population', 'pct_rural', 'pct_urbana',
        'population_preta', 'population_branca', 'population_indigena',
        'pct_pobreza', 'pct_preta', 'pct_indigena',
        'n_personas_pobreza', 'n_familias_rua',
        'idx_vulnerabilidad', 'tercil_vuln'
    ],
    'Clasificaciones': [
        'grupo_clima_biodiv', 'cuadrante'
    ]
}

# Clasificacion por 3 Componentes de Riesgo (IPCC)
RISK_COMPONENTS = {
    'HAZARD': {
        'description': 'Evento fisico peligroso (amenaza)',
        'variables': [
            'flooding_exposure', 'hydric_stress_exp',
            'fire_incidence_mean', 'fire_incidence_max', 'fire_frp_mean',
            'fire_frp_max', 'fire_total_foci', 'fire_frp_total',
            'fire_years_with_fire', 'fire_recurrence', 'fire_cv',
            'fire_dry_season_pct', 'fire_max_consecutive_years',
            'incidence_mean_dengue', 'incidence_mean_malaria',
            'incidence_mean_leishmaniose', 'incidence_mean_leptospirose',
            'incidence_diarrhea_mean',
            'incidence_max_dengue', 'incidence_max_malaria',
            'incidence_max_leishmaniose', 'incidence_max_leptospirose',
            'incidence_diarrhea_max',
            'persist_dengue', 'persist_malaria', 'persist_leishmaniose',
            'persist_leptospirose', 'persist_diarrhea',
            'copresence_years', 'copresence_3plus', 'copresence_all4'
        ]
    },
    'EXPOSURE': {
        'description': 'Poblacion/activos en zona de riesgo',
        'variables': [
            'population', 'pct_rural', 'pct_urbana',
            'population_preta', 'population_branca', 'population_indigena',
            'pct_preta', 'pct_indigena',
            'health_hosp_circ_mean', 'health_hosp_resp_mean', 'health_hosp_heat_mean',
            'health_hosp_circ_max', 'health_hosp_resp_max', 'health_hosp_heat_max',
            'health_total_hosp_circ', 'health_total_hosp_resp', 'health_total_hosp_heat',
            'health_death_circ_mean', 'health_death_resp_mean', 'health_death_heat_mean',
            'health_death_circ_max', 'health_death_resp_max', 'health_death_heat_max',
            'health_total_death_circ', 'health_total_death_resp', 'health_total_death_heat',
            'total_cases_dengue', 'total_cases_malaria',
            'total_cases_leishmaniose', 'total_cases_leptospirose',
            'total_cases_diarrhea', 'mort_infantil'
        ]
    },
    'VULNERABILITY_SENSITIVITY': {
        'description': 'Sensibilidad (aumenta vulnerabilidad)',
        'variables': [
            'pct_pobreza', 'n_personas_pobreza', 'n_familias_rua',
            'idx_vulnerabilidad', 'Vert_rich_risk', 'pol_deficit'
        ]
    },
    'VULNERABILITY_NATURAL': {
        'description': 'Capacidad Adaptativa Natural (reduce vulnerabilidad)',
        'variables': [
            'forest_cover', 'mean_species_richness', 'max_species_richness',
            'idx_biodiv'
        ]
    },
    'VULNERABILITY_INSTITUTIONAL': {
        'description': 'Capacidad Adaptativa Institucional (reduce vulnerabilidad)',
        'variables': [
            'UAI_housing', 'UAI_env', 'UAI_food', 'UAI_mob', 'UAI_Crisk',
            'idx_gobernanza', 'idx_gobernanza_100',
            'esgoto_tratado', 'IDESP_ensino_medio'
        ]
    },
    'RISK_INDICES': {
        'description': 'Indices compuestos de riesgo (combinan HxExV)',
        'variables': [
            'flooding_risks', 'hydric_stress_risk', 'fire_risk_index',
            'idx_clima', 'idx_carga_enfermedad'
        ]
    }
}

# Descripcion detallada de cada variable
VARIABLE_DESCRIPTIONS = {
    'cod_ibge': {'desc': 'Codigo IBGE del municipio (7 digitos)', 'source': 'IBGE', 'type': 'ID'},
    'Municipio': {'desc': 'Nombre del municipio', 'source': 'IBGE', 'type': 'ID'},
    'cod_microrregiao': {'desc': 'Codigo de la microrregion', 'source': 'IBGE', 'type': 'ID'},
    'nome_microrregiao': {'desc': 'Nombre de la microrregion', 'source': 'IBGE', 'type': 'ID'},
    'cod_mesorregiao': {'desc': 'Codigo de la mesorregion', 'source': 'IBGE', 'type': 'ID'},
    'nome_mesorregiao': {'desc': 'Nombre de la mesorregion', 'source': 'IBGE', 'type': 'ID'},
    'population': {'desc': 'Poblacion total del municipio (promedio 2010-2019)', 'source': 'IBGE SIDRA', 'type': 'count'},
    'pct_rural': {'desc': 'Porcentaje de poblacion rural', 'source': 'IBGE Censo', 'type': '%'},
    'pct_urbana': {'desc': 'Porcentaje de poblacion urbana', 'source': 'IBGE Censo', 'type': '%'},
    'population_preta': {'desc': 'Poblacion que se autodeclara negra', 'source': 'IBGE Censo', 'type': 'count'},
    'population_branca': {'desc': 'Poblacion que se autodeclara blanca', 'source': 'IBGE Censo', 'type': 'count'},
    'population_indigena': {'desc': 'Poblacion que se autodeclara indigena', 'source': 'IBGE Censo', 'type': 'count'},
    'pct_pobreza': {'desc': 'Porcentaje de poblacion en situacion de pobreza', 'source': 'IBGE/CadUnico', 'type': '%'},
    'pct_preta': {'desc': 'Porcentaje de poblacion negra', 'source': 'IBGE Censo', 'type': '%'},
    'pct_indigena': {'desc': 'Porcentaje de poblacion indigena', 'source': 'IBGE Censo', 'type': '%'},
    'n_personas_pobreza': {'desc': 'Numero de personas en pobreza', 'source': 'CadUnico', 'type': 'count'},
    'n_familias_rua': {'desc': 'Numero de familias en situacion de calle', 'source': 'CadUnico', 'type': 'count'},
    'mort_infantil': {'desc': 'Tasa de mortalidad infantil (por 1000 nacidos vivos)', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'IDESP_ensino_medio': {'desc': 'Indice de Desarrollo de la Educacion (ensenanza media)', 'source': 'SEADE', 'type': 'index'},
    'esgoto_tratado': {'desc': 'Porcentaje de esgoto tratado', 'source': 'SNIS', 'type': '%'},
    'UAI_housing': {'desc': 'Indice de Adaptacion Urbana - Vivienda (0-1)', 'source': 'Neder et al. 2021', 'type': 'index'},
    'UAI_env': {'desc': 'Indice de Adaptacion Urbana - Ambiental (0-1)', 'source': 'Neder et al. 2021', 'type': 'index'},
    'UAI_food': {'desc': 'Indice de Adaptacion Urbana - Alimentacion (0-1)', 'source': 'Neder et al. 2021', 'type': 'index'},
    'UAI_mob': {'desc': 'Indice de Adaptacion Urbana - Movilidad (0-1)', 'source': 'Neder et al. 2021', 'type': 'index'},
    'UAI_Crisk': {'desc': 'Indice de Adaptacion Urbana - Riesgo Climatico (0-1)', 'source': 'Neder et al. 2021', 'type': 'index'},
    'idx_gobernanza': {'desc': 'Indice compuesto de gobernanza = mean(UAI_*) (0-1)', 'source': 'Calculado', 'type': 'index'},
    'idx_gobernanza_100': {'desc': 'Indice de gobernanza escalado 0-100', 'source': 'Calculado', 'type': 'index'},
    'mean_species_richness': {'desc': 'Riqueza media de especies de vertebrados', 'source': 'Datos pre-procesados', 'type': 'count'},
    'max_species_richness': {'desc': 'Riqueza maxima de especies de vertebrados', 'source': 'Datos pre-procesados', 'type': 'count'},
    'Vert_rich_risk': {'desc': 'Riesgo por perdida de riqueza de vertebrados', 'source': 'Calculado', 'type': 'index'},
    'forest_cover': {'desc': 'Porcentaje de cobertura forestal', 'source': 'MapBiomas', 'type': '%'},
    'pol_deficit': {'desc': 'Deficit de polinizacion (indicador de degradacion)', 'source': 'Datos pre-procesados', 'type': 'index'},
    'idx_biodiv': {'desc': 'Indice compuesto de biodiversidad (0-100)', 'source': 'Calculado', 'type': 'index'},
    'tercil_biodiv': {'desc': 'Tercil de biodiversidad (1=bajo, 2=medio, 3=alto)', 'source': 'Calculado', 'type': 'category'},
    'flooding_exposure': {'desc': 'Exposicion a inundaciones (area inundable)', 'source': 'MapBiomas/INPE', 'type': 'index'},
    'flooding_risks': {'desc': 'Indice de riesgo de inundacion', 'source': 'Calculado', 'type': 'index'},
    'hydric_stress_exp': {'desc': 'Exposicion a estres hidrico', 'source': 'ANA', 'type': 'index'},
    'hydric_stress_risk': {'desc': 'Indice de riesgo de estres hidrico', 'source': 'Calculado', 'type': 'index'},
    'idx_clima': {'desc': 'Indice compuesto de riesgo climatico (0-100)', 'source': 'Calculado', 'type': 'index'},
    'tercil_clima': {'desc': 'Tercil de riesgo climatico (1=bajo, 2=medio, 3=alto)', 'source': 'Calculado', 'type': 'category'},
    'fire_incidence_mean': {'desc': 'Incidencia media anual de focos de fuego', 'source': 'INPE Queimadas', 'type': 'rate'},
    'fire_incidence_max': {'desc': 'Incidencia maxima anual de focos de fuego', 'source': 'INPE Queimadas', 'type': 'rate'},
    'fire_frp_mean': {'desc': 'Potencia radiativa del fuego (FRP) media', 'source': 'INPE Queimadas', 'type': 'value'},
    'fire_frp_max': {'desc': 'FRP maxima registrada', 'source': 'INPE Queimadas', 'type': 'value'},
    'fire_total_foci': {'desc': 'Total de focos de fuego 2010-2019', 'source': 'INPE Queimadas', 'type': 'count'},
    'fire_frp_total': {'desc': 'FRP total acumulada', 'source': 'INPE Queimadas', 'type': 'value'},
    'fire_years_with_fire': {'desc': 'Anos con registro de fuego (0-10)', 'source': 'INPE Queimadas', 'type': 'count'},
    'fire_recurrence': {'desc': 'Recurrencia de fuego (proporcion de anos)', 'source': 'Calculado', 'type': 'proportion'},
    'fire_cv': {'desc': 'Coeficiente de variacion de incidencia de fuego', 'source': 'Calculado', 'type': 'value'},
    'fire_dry_season_pct': {'desc': 'Porcentaje de focos en epoca seca', 'source': 'INPE Queimadas', 'type': '%'},
    'fire_max_consecutive_years': {'desc': 'Anos consecutivos maximos con fuego', 'source': 'Calculado', 'type': 'count'},
    'fire_risk_index': {'desc': 'Indice compuesto de riesgo de fuego', 'source': 'Calculado', 'type': 'index'},
    'persist_dengue': {'desc': 'Anos con casos de dengue (0-10)', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'persist_leishmaniose': {'desc': 'Anos con casos de leishmaniasis (0-10)', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'persist_leptospirose': {'desc': 'Anos con casos de leptospirosis (0-10)', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'persist_malaria': {'desc': 'Anos con casos de malaria (0-10)', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'persist_diarrhea': {'desc': 'Anos con casos de diarrea (0-10)', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'incidence_mean_dengue': {'desc': 'Incidencia media de dengue (por 100k hab/ano)', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_mean_leishmaniose': {'desc': 'Incidencia media de leishmaniasis (por 100k hab/ano)', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_mean_leptospirose': {'desc': 'Incidencia media de leptospirosis (por 100k hab/ano)', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_mean_malaria': {'desc': 'Incidencia media de malaria (por 100k hab/ano)', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_diarrhea_mean': {'desc': 'Incidencia media de diarrea (por 100k hab/ano)', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_max_dengue': {'desc': 'Incidencia maxima de dengue en un ano', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_max_leishmaniose': {'desc': 'Incidencia maxima de leishmaniasis en un ano', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_max_leptospirose': {'desc': 'Incidencia maxima de leptospirosis en un ano', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_max_malaria': {'desc': 'Incidencia maxima de malaria en un ano', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'incidence_diarrhea_max': {'desc': 'Incidencia maxima de diarrea en un ano', 'source': 'DATASUS/SINAN', 'type': 'rate'},
    'total_cases_dengue': {'desc': 'Total casos de dengue 2010-2019', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'total_cases_leishmaniose': {'desc': 'Total casos de leishmaniasis 2010-2019', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'total_cases_leptospirose': {'desc': 'Total casos de leptospirosis 2010-2019', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'total_cases_malaria': {'desc': 'Total casos de malaria 2010-2019', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'total_cases_diarrhea': {'desc': 'Total casos de diarrea 2010-2019', 'source': 'DATASUS/SINAN', 'type': 'count'},
    'copresence_years': {'desc': 'Anos con 2+ enfermedades vectoriales simultaneas', 'source': 'Calculado', 'type': 'count'},
    'copresence_3plus': {'desc': 'Anos con 3+ enfermedades vectoriales', 'source': 'Calculado', 'type': 'count'},
    'copresence_all4': {'desc': 'Anos con las 4 enfermedades vectoriales', 'source': 'Calculado', 'type': 'count'},
    'dengue_leptospirose': {'desc': 'Co-ocurrencia dengue-leptospirosis', 'source': 'Calculado', 'type': 'binary'},
    'dengue_malaria': {'desc': 'Co-ocurrencia dengue-malaria', 'source': 'Calculado', 'type': 'binary'},
    'dengue_leishmaniose': {'desc': 'Co-ocurrencia dengue-leishmaniasis', 'source': 'Calculado', 'type': 'binary'},
    'leptospirose_malaria': {'desc': 'Co-ocurrencia leptospirosis-malaria', 'source': 'Calculado', 'type': 'binary'},
    'leptospirose_leishmaniose': {'desc': 'Co-ocurrencia leptospirosis-leishmaniasis', 'source': 'Calculado', 'type': 'binary'},
    'malaria_leishmaniose': {'desc': 'Co-ocurrencia malaria-leishmaniasis', 'source': 'Calculado', 'type': 'binary'},
    'health_hosp_circ_mean': {'desc': 'Tasa media de hospitalizacion por enf. circulatorias', 'source': 'DATASUS/SIH', 'type': 'rate'},
    'health_hosp_resp_mean': {'desc': 'Tasa media de hospitalizacion por enf. respiratorias', 'source': 'DATASUS/SIH', 'type': 'rate'},
    'health_hosp_heat_mean': {'desc': 'Tasa media de hospitalizacion por efectos del calor', 'source': 'DATASUS/SIH', 'type': 'rate'},
    'health_hosp_circ_max': {'desc': 'Tasa maxima de hospitalizacion circulatoria', 'source': 'DATASUS/SIH', 'type': 'rate'},
    'health_hosp_resp_max': {'desc': 'Tasa maxima de hospitalizacion respiratoria', 'source': 'DATASUS/SIH', 'type': 'rate'},
    'health_hosp_heat_max': {'desc': 'Tasa maxima de hospitalizacion por calor', 'source': 'DATASUS/SIH', 'type': 'rate'},
    'health_total_hosp_circ': {'desc': 'Total hospitalizaciones circulatorias 2010-2019', 'source': 'DATASUS/SIH', 'type': 'count'},
    'health_total_hosp_resp': {'desc': 'Total hospitalizaciones respiratorias 2010-2019', 'source': 'DATASUS/SIH', 'type': 'count'},
    'health_total_hosp_heat': {'desc': 'Total hospitalizaciones por calor 2010-2019', 'source': 'DATASUS/SIH', 'type': 'count'},
    'health_death_circ_mean': {'desc': 'Tasa media de mortalidad por enf. circulatorias', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'health_death_resp_mean': {'desc': 'Tasa media de mortalidad por enf. respiratorias', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'health_death_heat_mean': {'desc': 'Tasa media de mortalidad por efectos del calor', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'health_death_circ_max': {'desc': 'Tasa maxima de mortalidad circulatoria', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'health_death_resp_max': {'desc': 'Tasa maxima de mortalidad respiratoria', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'health_death_heat_max': {'desc': 'Tasa maxima de mortalidad por calor', 'source': 'DATASUS/SIM', 'type': 'rate'},
    'health_total_death_circ': {'desc': 'Total obitos circulatorios 2010-2019', 'source': 'DATASUS/SIM', 'type': 'count'},
    'health_total_death_resp': {'desc': 'Total obitos respiratorios 2010-2019', 'source': 'DATASUS/SIM', 'type': 'count'},
    'health_total_death_heat': {'desc': 'Total obitos por calor 2010-2019', 'source': 'DATASUS/SIM', 'type': 'count'},
    'idx_vulnerabilidad': {'desc': 'Indice de vulnerabilidad socioeconomica (0-100)', 'source': 'Calculado', 'type': 'index'},
    'idx_carga_enfermedad': {'desc': 'Indice de carga de enfermedad (0-100)', 'source': 'Calculado', 'type': 'index'},
    'tercil_vuln': {'desc': 'Tercil de vulnerabilidad (1=bajo, 2=medio, 3=alto)', 'source': 'Calculado', 'type': 'category'},
    'grupo_clima_biodiv': {'desc': 'Grupo combinado clima-biodiversidad', 'source': 'Calculado', 'type': 'category'},
    'cuadrante': {'desc': 'Cuadrante gobernanza-vulnerabilidad', 'source': 'Calculado', 'type': 'category'},
}


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def count_variables_by_dimension():
    """Count variables per Nexus dimension"""
    counts = {}
    total = 0
    for dim, vars_list in NEXUS_DIMENSIONS.items():
        counts[dim] = len(vars_list)
        total += len(vars_list)
    counts['TOTAL'] = total
    return counts


def count_variables_by_risk_component():
    """Count variables per IPCC risk component"""
    counts = {}
    for comp, data in RISK_COMPONENTS.items():
        counts[comp] = len(data['variables'])
    return counts


def create_variable_table(df):
    """Create comprehensive variable table"""
    rows = []

    for col in df.columns:
        dimension = 'Sin clasificar'
        for dim, vars_list in NEXUS_DIMENSIONS.items():
            if col in vars_list:
                dimension = dim
                break

        if col in VARIABLE_DESCRIPTIONS:
            desc = VARIABLE_DESCRIPTIONS[col]['desc']
            source = VARIABLE_DESCRIPTIONS[col]['source']
            var_type = VARIABLE_DESCRIPTIONS[col]['type']
        else:
            desc = ''
            source = ''
            var_type = ''

        if df[col].dtype in ['float64', 'int64']:
            mean_val = df[col].mean()
            min_val = df[col].min()
            max_val = df[col].max()
            na_count = df[col].isna().sum()
        else:
            mean_val = np.nan
            min_val = np.nan
            max_val = np.nan
            na_count = df[col].isna().sum()

        rows.append({
            'variable': col,
            'dimension_nexus': dimension,
            'descripcion': desc,
            'fuente': source,
            'tipo': var_type,
            'min': min_val,
            'max': max_val,
            'mean': mean_val,
            'na_count': na_count
        })

    return pd.DataFrame(rows)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("H6: SINTESIS Y METADATA DE VARIABLES")
    print("=" * 70)

    print("\n  Cargando datos...")
    df = pd.read_csv(CSV_PATH)
    print(f"  Dataset: {len(df)} municipios, {len(df.columns)} variables")

    print("\n  Contando variables por dimension Nexus...")
    nexus_counts = count_variables_by_dimension()
    for dim, count in nexus_counts.items():
        print(f"    {dim}: {count}")

    print("\n  Contando variables por componente IPCC...")
    risk_counts = count_variables_by_risk_component()
    for comp, count in risk_counts.items():
        print(f"    {comp}: {count}")

    print("\n  Creando tabla de variables...")
    var_table = create_variable_table(df)

    var_table.to_csv(os.path.join(OUTPUT_DIR, 'h6_variable_table.csv'), index=False)
    print(f"  [SAVED] h6_variable_table.csv")

    pd.DataFrame([nexus_counts]).T.reset_index().rename(
        columns={'index': 'dimension', 0: 'count'}
    ).to_csv(os.path.join(OUTPUT_DIR, 'h6_nexus_counts.csv'), index=False)
    print(f"  [SAVED] h6_nexus_counts.csv")

    pd.DataFrame([risk_counts]).T.reset_index().rename(
        columns={'index': 'component', 0: 'count'}
    ).to_csv(os.path.join(OUTPUT_DIR, 'h6_risk_counts.csv'), index=False)
    print(f"  [SAVED] h6_risk_counts.csv")

    print("\n" + "=" * 70)
    print("RESUMEN H6")
    print("=" * 70)
    print(f"\n  Total variables: {len(df.columns)}")
    print(f"  Total municipios: {len(df)}")
    print(f"\n  Por dimension Nexus:")
    for dim, count in nexus_counts.items():
        if dim != 'TOTAL':
            print(f"    - {dim}: {count}")
    print(f"\n  Por componente IPCC:")
    for comp, count in risk_counts.items():
        print(f"    - {comp}: {count}")

    print("\nDone!")


if __name__ == "__main__":
    main()

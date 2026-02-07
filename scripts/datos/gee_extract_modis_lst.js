// =============================================================================
// SCRIPT GEE: Extracción de MODIS LST para islas de calor urbano
// Proyecto: Resilient Landscapes - São Paulo
// Período: 2010-2019
// Unidad: 645 municipios del estado de São Paulo
// =============================================================================
//
// MÉTRICAS CALCULADAS:
//   1. lst_day_mean: LST diurna media anual (°C, promedio decadal)
//   2. lst_night_mean: LST nocturna media anual (°C, promedio decadal)
//   3. lst_day_max_p95: Percentil 95 de LST diurna (extremos)
//
// FUENTE: MODIS/061/MOD11A2 (Terra) + MODIS/061/MYD11A2 (Aqua)
//   - Resolución: 1 km
//   - Temporal: Compuesto 8 días
//   - Referencia: Monteiro et al. (2021), Wu et al. (2019)
//
// NOTA: LST es temperatura de SUPERFICIE, no del aire. Es la métrica directa
// para detectar islas de calor urbano (SUHI). SP tiene SUHI diurna de 6.60°C
// (3ra más alta de Sudamérica) y la mayor SUHI nocturna de Brasil.
// =============================================================================

// --- CONFIGURACIÓN ---
var START_DATE = '2010-01-01';
var END_DATE = '2019-12-31';
var SCALE_FACTOR = 0.02;  // Factor de escala LST MODIS (DN a Kelvin)
var KELVIN_OFFSET = -273.15;  // Kelvin a Celsius

// --- CARGAR MUNICIPIOS DE SÃO PAULO ---
var municipios_brasil = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/municipios-2022');
var municipios = municipios_brasil.filter(ee.Filter.eq('sigla_uf', 'SP'));
print('Municipios SP:', municipios.size());

// --- CARGAR MODIS LST ---
// Terra (paso matutino ~10:30 local, nocturno ~22:30)
var modis_terra = ee.ImageCollection('MODIS/061/MOD11A2')
  .filterDate(START_DATE, END_DATE)
  .filterBounds(municipios);

// Aqua (paso vespertino ~13:30 local, madrugada ~01:30)
var modis_aqua = ee.ImageCollection('MODIS/061/MYD11A2')
  .filterDate(START_DATE, END_DATE)
  .filterBounds(municipios);

print('Imágenes Terra:', modis_terra.size());
print('Imágenes Aqua:', modis_aqua.size());

// --- FUNCIÓN: Convertir DN a °C y aplicar QC ---
var processLST = function(img) {
  // Aplicar máscara de calidad (QC_Day y QC_Night)
  var qcDay = img.select('QC_Day');
  var qcNight = img.select('QC_Night');

  // Bits 0-1: LST error flag (00 = good, 01 = average, 10 = below average)
  var goodDay = qcDay.bitwiseAnd(3).lte(1);  // acepta 00 y 01
  var goodNight = qcNight.bitwiseAnd(3).lte(1);

  // Convertir a °C
  var lstDay = img.select('LST_Day_1km')
    .multiply(SCALE_FACTOR)
    .add(KELVIN_OFFSET)
    .updateMask(goodDay)
    .rename('LST_Day_C');

  var lstNight = img.select('LST_Night_1km')
    .multiply(SCALE_FACTOR)
    .add(KELVIN_OFFSET)
    .updateMask(goodNight)
    .rename('LST_Night_C');

  return lstDay.addBands(lstNight)
    .copyProperties(img, ['system:time_start']);
};

// --- PROCESAR COLECCIONES ---
var terra_processed = modis_terra.map(processLST);
var aqua_processed = modis_aqua.map(processLST);

// Combinar Terra y Aqua para mejor cobertura temporal
var combined = terra_processed.merge(aqua_processed);

// --- CALCULAR ESTADÍSTICAS DECADALES ---

// Media de LST diurna (todas las observaciones 2010-2019)
var lstDayMean = combined.select('LST_Day_C').mean().rename('lst_day_mean');

// Media de LST nocturna
var lstNightMean = combined.select('LST_Night_C').mean().rename('lst_night_mean');

// Percentil 95 de LST diurna (extremos de calor superficial)
var lstDayP95 = combined.select('LST_Day_C')
  .reduce(ee.Reducer.percentile([95]))
  .rename('lst_day_p95');

// Desviación estándar de LST diurna
var lstDaySD = combined.select('LST_Day_C')
  .reduce(ee.Reducer.stdDev())
  .rename('lst_day_sd');

// Amplitud térmica diurna-nocturna media
var lstAmplitude = lstDayMean.subtract(lstNightMean).rename('lst_amplitude');

// Imagen con todas las métricas
var allLST = lstDayMean
  .addBands(lstNightMean)
  .addBands(lstDayP95)
  .addBands(lstDaySD)
  .addBands(lstAmplitude);

// --- REDUCIR POR MUNICIPIO ---
var municipalLST = allLST.reduceRegions({
  collection: municipios,
  reducer: ee.Reducer.mean(),
  scale: 1000,  // 1 km (resolución nativa MODIS)
  crs: 'EPSG:4326'
});

// Seleccionar columnas
var output = municipalLST.select(
  ['cd_mun', 'nm_mun',
   'lst_day_mean', 'lst_night_mean',
   'lst_day_p95', 'lst_day_sd', 'lst_amplitude'],
  ['cd_mun', 'nm_mun',
   'lst_day_mean', 'lst_night_mean',
   'lst_day_p95', 'lst_day_sd', 'lst_amplitude']
);

print('Resultado:', output.first());

// --- EXPORTAR A GOOGLE DRIVE ---
Export.table.toDrive({
  collection: output,
  description: 'modis_lst_sp_2010_2019',
  folder: 'Adrian_David_Data',
  fileNamePrefix: 'modis_lst_sp_2010_2019',
  fileFormat: 'CSV'
});

// --- VISUALIZACIÓN ---
var vis_day = {min: 20, max: 40, palette: ['blue', 'cyan', 'yellow', 'orange', 'red']};
var vis_night = {min: 10, max: 25, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange']};
var vis_amp = {min: 5, max: 20, palette: ['green', 'yellow', 'red']};

Map.centerObject(municipios, 7);
Map.addLayer(lstDayMean, vis_day, 'LST Diurna Media (°C)');
Map.addLayer(lstNightMean, vis_night, 'LST Nocturna Media (°C)');
Map.addLayer(lstAmplitude, vis_amp, 'Amplitud Térmica (°C)');
Map.addLayer(municipios.style({color: '000000', fillColor: '00000000', width: 0.5}), {}, 'Municipios SP');

// =============================================================================
// NOTAS METODOLÓGICAS:
//
// 1. LST vs TEMPERATURA DEL AIRE:
//    - LST mide temperatura de SUPERFICIE (suelo, techo, pavimento)
//    - La temperatura del aire (Ta) se mide a 2m de altura
//    - LST > Ta en superficies expuestas al sol; LST ≈ Ta en áreas vegetadas
//    - La diferencia LST - Ta es mayor en islas de calor urbano
//    - Para vincular con biodiversidad: LST es más directa que Ta
//
// 2. TERRA vs AQUA:
//    - Terra pasa ~10:30 (día) y ~22:30 (noche) hora local
//    - Aqua pasa ~13:30 (día, más caliente) y ~01:30 (noche)
//    - Combinamos ambas para maximizar cobertura (reducir gaps por nubes)
//
// 3. FILTRO DE CALIDAD:
//    - Se excluyen píxeles con error LST > 2K (QC bits 0-1)
//    - Esto elimina observaciones contaminadas por nubes finas
//
// 4. MÉTRICAS:
//    - lst_day_mean: Promedio de temperatura superficial diurna
//    - lst_night_mean: Promedio nocturno (relevante para mortalidad)
//    - lst_day_p95: Percentil 95 diurno (extremos de calor)
//    - lst_amplitude: Diferencia día-noche (mayor en áreas impermeabilizadas)
//
// REFERENCIAS:
// - Monteiro et al. (2021). UHI in 21 Brazilian metropolitan areas. Urban Climate.
// - Wu et al. (2019). Surface UHI in 44 South American cities. Remote Sensing.
// - Wan (2014). New refinements and validation of MODIS LST. Remote Sensing Env.
// =============================================================================

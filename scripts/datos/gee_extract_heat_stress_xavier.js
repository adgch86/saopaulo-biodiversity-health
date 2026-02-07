// =============================================================================
// SCRIPT GEE: Extracción de métricas de estrés térmico - Xavier/BR-DWGD v3
// Proyecto: Resilient Landscapes - São Paulo
// Período: 2010-2019
// Unidad: 645 municipios del estado de São Paulo
// =============================================================================
//
// MÉTRICAS CALCULADAS:
//   1. heat_persistence: Días/año con Tmax > 34.7°C (promedio decadal)
//   2. heat_HAAT: Grados-día acumulados sobre 34.7°C (promedio anual)
//   3. mmt_days: Días/año con Tmedia > 22.3°C (promedio decadal)
//
// FUENTE: Xavier/BR-DWGD v3 (Brazilian Daily Weather Gridded Data)
//   - Resolución: 0.1° x 0.1° (~11 km) para Tmax/Tmin
//   - Temporal: Diaria (1961-2024)
//   - Referencia: Xavier et al. (2022), Int J Climatol
//   - GEE: https://gee-community-catalog.org/projects/br_dwgd/
//
// INSTRUCCIONES:
//   1. Abrir Google Earth Engine Code Editor (code.earthengine.google.com)
//   2. Pegar este script
//   3. Cargar el shapefile de municipios de SP como asset (IBGE 2022)
//      - Alternativa: usar el asset público 'projects/mapbiomas-workspace/AUXILIAR/municipios-2022'
//   4. Ejecutar y exportar resultado a Google Drive
// =============================================================================

// --- CONFIGURACIÓN ---
var THRESHOLD_TMAX = 34.7;   // °C - umbral persistencia (Valverde 2023: media ondas de calor SP = 34.9°C)
var THRESHOLD_TMEAN = 22.3;  // °C - umbral MMT (Nascimento et al. 2019: MMT IAM región SE)
var START_YEAR = 2010;
var END_YEAR = 2019;

// --- CARGAR MUNICIPIOS DE SÃO PAULO ---
// Opción 1: Asset propio (recomendado - subir shapefile IBGE 2022)
// var municipios = ee.FeatureCollection('users/TU_USUARIO/sp_municipios_ibge2022');

// Opción 2: Asset MapBiomas (disponible públicamente)
var municipios_brasil = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/municipios-2022');

// Filtrar São Paulo (código UF = 35)
var municipios = municipios_brasil.filter(ee.Filter.eq('sigla_uf', 'SP'));
print('Municipios SP:', municipios.size());

// --- CARGAR DATOS XAVIER/BR-DWGD ---
// Tmax - Temperatura máxima diaria (0.1° resolución)
var tmax_collection = ee.ImageCollection('projects/br-dwgd/assets/tmax')
  .filterDate(START_YEAR + '-01-01', END_YEAR + '-12-31');

// Tmin - Temperatura mínima diaria (0.1° resolución)
var tmin_collection = ee.ImageCollection('projects/br-dwgd/assets/tmin')
  .filterDate(START_YEAR + '-01-01', END_YEAR + '-12-31');

print('Imágenes Tmax:', tmax_collection.size());
print('Imágenes Tmin:', tmin_collection.size());

// --- FUNCIÓN: Calcular métricas por año ---
var calculateYearlyMetrics = function(year) {
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = ee.Date.fromYMD(year, 12, 31);

  // Filtrar colecciones por año
  var tmax_year = tmax_collection.filterDate(startDate, endDate);
  var tmin_year = tmin_collection.filterDate(startDate, endDate);

  // --- Métrica 1: Persistencia (días con Tmax > 34.7°C) ---
  var hotDays = tmax_year.map(function(img) {
    return img.gt(THRESHOLD_TMAX).rename('hot_day');
  });
  var persistence = hotDays.sum().rename('heat_persistence');

  // --- Métrica 2: HAAT (grados-día acumulados sobre 34.7°C) ---
  var haat = tmax_year.map(function(img) {
    var excess = img.subtract(THRESHOLD_TMAX).max(0);
    return excess.rename('haat');
  });
  var haat_sum = haat.sum().rename('heat_HAAT');

  // --- Métrica 3: Días MMT (Tmedia > 22.3°C) ---
  // Tmedia = (Tmax + Tmin) / 2
  // Necesitamos emparejar Tmax y Tmin por fecha
  var dates = tmax_year.aggregate_array('system:time_start');

  var mmtDays = tmax_year.map(function(tmax_img) {
    var date = tmax_img.date();
    var tmin_img = tmin_year.filterDate(date, date.advance(1, 'day')).first();
    // Si no hay Tmin para esa fecha, retornar 0
    var tmean = ee.Algorithms.If(
      tmin_img,
      tmax_img.add(ee.Image(tmin_img)).divide(2),
      tmax_img  // fallback
    );
    return ee.Image(tmean).gt(THRESHOLD_TMEAN).rename('mmt_day').copyProperties(tmax_img, ['system:time_start']);
  });
  var mmt_days = mmtDays.sum().rename('mmt_days');

  // Combinar métricas en una imagen
  var metrics = persistence
    .addBands(haat_sum)
    .addBands(mmt_days)
    .set('year', year);

  return metrics;
};

// --- CALCULAR PARA CADA AÑO ---
var years = ee.List.sequence(START_YEAR, END_YEAR);
var yearlyMetrics = ee.ImageCollection(years.map(calculateYearlyMetrics));

print('Métricas anuales:', yearlyMetrics);

// --- CALCULAR PROMEDIOS DECADALES ---
var meanPersistence = yearlyMetrics.select('heat_persistence').mean().rename('heat_persistence_mean');
var meanHAAT = yearlyMetrics.select('heat_HAAT').mean().rename('heat_HAAT_mean');
var meanMMT = yearlyMetrics.select('mmt_days').mean().rename('mmt_days_mean');

// También calcular desviación estándar
var sdPersistence = yearlyMetrics.select('heat_persistence').reduce(ee.Reducer.stdDev()).rename('heat_persistence_sd');
var sdHAAT = yearlyMetrics.select('heat_HAAT').reduce(ee.Reducer.stdDev()).rename('heat_HAAT_sd');
var sdMMT = yearlyMetrics.select('mmt_days').reduce(ee.Reducer.stdDev()).rename('mmt_days_sd');

// Imagen con todas las métricas
var allMetrics = meanPersistence
  .addBands(sdPersistence)
  .addBands(meanHAAT)
  .addBands(sdHAAT)
  .addBands(meanMMT)
  .addBands(sdMMT);

// --- REDUCIR POR MUNICIPIO ---
var municipalMetrics = allMetrics.reduceRegions({
  collection: municipios,
  reducer: ee.Reducer.mean(),
  scale: 11132,  // ~0.1° en metros
  crs: 'EPSG:4326'
});

// Seleccionar columnas relevantes
var output = municipalMetrics.select(
  ['cd_mun', 'nm_mun',
   'heat_persistence_mean', 'heat_persistence_sd',
   'heat_HAAT_mean', 'heat_HAAT_sd',
   'mmt_days_mean', 'mmt_days_sd'],
  ['cd_mun', 'nm_mun',
   'heat_persistence_mean', 'heat_persistence_sd',
   'heat_HAAT_mean', 'heat_HAAT_sd',
   'mmt_days_mean', 'mmt_days_sd']
);

print('Resultado:', output.first());

// --- EXPORTAR A GOOGLE DRIVE ---
Export.table.toDrive({
  collection: output,
  description: 'heat_stress_xavier_sp_2010_2019',
  folder: 'Adrian_David_Data',
  fileNamePrefix: 'heat_stress_xavier_sp_2010_2019',
  fileFormat: 'CSV'
});

// --- VISUALIZACIÓN (opcional) ---
var vis_persistence = {min: 0, max: 30, palette: ['blue', 'yellow', 'red']};
var vis_mmt = {min: 100, max: 300, palette: ['green', 'yellow', 'orange', 'red']};

Map.centerObject(municipios, 7);
Map.addLayer(meanPersistence, vis_persistence, 'Persistencia (días Tmax > 34.7°C)');
Map.addLayer(meanMMT, vis_mmt, 'Días MMT (Tmedia > 22.3°C)');
Map.addLayer(municipios.style({color: '000000', fillColor: '00000000', width: 0.5}), {}, 'Municipios SP');

// =============================================================================
// NOTAS METODOLÓGICAS:
//
// 1. PERSISTENCIA (heat_persistence):
//    - Cuenta días por año donde Tmax > 34.7°C
//    - Umbral basado en Valverde (2023): temp. media de ondas de calor en SP = 34.9°C
//    - El promedio decadal suaviza variabilidad interanual
//
// 2. HAAT (Heat Area Above Threshold):
//    - Suma de (Tmax - 34.7) para días con Tmax > 34.7°C
//    - Captura tanto intensidad como frecuencia
//    - Basado en metodología de medRxiv 2025 (Río de Janeiro)
//    - Unidades: grados-día/año
//
// 3. MMT DAYS (Minimum Mortality Temperature):
//    - Cuenta días con temperatura media > 22.3°C
//    - Tmedia = (Tmax + Tmin) / 2
//    - Umbral basado en Nascimento et al. (2019): MMT para IAM en SE Brasil
//    - Captura exposición crónica al calor, no solo extremos
//
// REFERENCIAS:
// - Xavier et al. (2022). New improved Brazilian daily weather gridded data.
//   Int J Climatol. DOI: 10.1002/joc.7731
// - Valverde (2023). Heat waves in São Paulo State.
//   Int J Climatol. DOI: 10.1002/joc.8058
// - Nascimento et al. (2019). Ambient temperature and mortality due to AMI in Brazil.
//   Scientific Reports. DOI: 10.1038/s41598-019-50235-8
// =============================================================================

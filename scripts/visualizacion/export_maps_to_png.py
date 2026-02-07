"""
Script para exportar mapas HTML a PNG usando Selenium
Workshop SEMIL-USP

Autor: Adrian David / AP Digital
Fecha: 2026-01-23
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Rutas
INPUT_DIR = r"G:\My Drive\Adrian David\Forthe_worshop\mapas_workshop"
OUTPUT_DIR = r"G:\My Drive\Adrian David\Forthe_worshop\mapas_workshop\png"

# Archivos HTML a convertir
MAPAS = [
    "01_riesgo_inundacion",
    "02_riqueza_vertebrados",
    "03_vulnerabilidad_social",
    "04_incidencia_dengue",
    "05_gobernanza_UAI",
    "06_deficit_polinizacion"
]

def setup_driver():
    """Configura el driver de Chrome en modo headless"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Usar webdriver-manager para obtener el driver automáticamente
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def capture_map(driver, html_path, png_path, wait_time=5):
    """
    Captura un mapa HTML como PNG

    Args:
        driver: Selenium WebDriver
        html_path: Ruta al archivo HTML
        png_path: Ruta de salida para el PNG
        wait_time: Segundos a esperar para que cargue el mapa
    """
    # Cargar el HTML
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    driver.get(file_url)

    # Esperar a que cargue el mapa (los tiles de fondo)
    time.sleep(wait_time)

    # Tomar screenshot
    driver.save_screenshot(png_path)

    return png_path


def main():
    """Función principal"""
    print("=" * 60)
    print("EXPORTADOR DE MAPAS A PNG")
    print("=" * 60)

    # Crear carpeta de salida
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"\nCarpeta de salida: {OUTPUT_DIR}")

    # Configurar driver
    print("\nConfigurando Chrome WebDriver...")
    driver = setup_driver()
    print("[OK] Driver configurado")

    # Procesar cada mapa
    print("\nGenerando imagenes PNG...")
    imagenes_generadas = []

    try:
        for nombre in MAPAS:
            html_path = os.path.join(INPUT_DIR, f"{nombre}.html")
            png_path = os.path.join(OUTPUT_DIR, f"{nombre}.png")

            if not os.path.exists(html_path):
                print(f"  [WARN] No encontrado: {html_path}")
                continue

            print(f"  Procesando: {nombre}...", end=" ", flush=True)
            capture_map(driver, html_path, png_path)
            print("[OK]")
            imagenes_generadas.append(png_path)

    finally:
        # Cerrar driver
        driver.quit()

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Imagenes generadas: {len(imagenes_generadas)}/{len(MAPAS)}")
    print(f"Ubicacion: {OUTPUT_DIR}")
    print("\nArchivos creados:")
    for img in imagenes_generadas:
        nombre = os.path.basename(img)
        size_mb = os.path.getsize(img) / (1024 * 1024)
        print(f"  - {nombre} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

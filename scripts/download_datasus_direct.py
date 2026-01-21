# -*- coding: utf-8 -*-
"""
Script para descargar datos de salud del DATASUS - Metodo Directo
=================================================================

Este script descarga datos directamente del FTP de DATASUS sin depender de PySUS.
Usa la API de TabNet para obtener datos agregados por municipio.

Enfermedades:
- Dengue, Leptospirose, Malaria, Leishmaniose Visceral, Leishmaniose Tegumentar

Periodo: 2010-2019
Estado: Sao Paulo (SP)

Autor: Science Team / Data Engineer
Fecha: 2026-01-20
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from io import StringIO
import time

# Forzar encoding UTF-8 para output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Configuracion de paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "datasus"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

# Crear directorios si no existen
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

# URLs base de TabNet DATASUS
TABNET_BASE = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe"

# Configuracion de enfermedades con sus definiciones de TabNet
DISEASES_CONFIG = {
    "dengue": {
        "name": "Dengue",
        "def_file": "sinannet/cnv/denguebbr.def",
        "content": "Casos_confirmados"
    },
    "leptospirose": {
        "name": "Leptospirose",
        "def_file": "sinannet/cnv/leptobr.def",
        "content": "Casos_confirmados"
    },
    "malaria": {
        "name": "Malaria",
        "def_file": "sinannet/cnv/malabr.def",
        "content": "Exames_positivos"
    },
    "leish_visceral": {
        "name": "Leishmaniose Visceral",
        "def_file": "sinannet/cnv/leishvbr.def",
        "content": "Casos_confirmados"
    },
    "leish_tegumentar": {
        "name": "Leishmaniose Tegumentar",
        "def_file": "sinannet/cnv/ltabr.def",
        "content": "Casos_confirmados"
    }
}

YEARS = list(range(2010, 2020))
UF_SP_CODE = "35"  # Sao Paulo


def get_ftp_files_list():
    """
    Obtiene la lista de archivos disponibles en el FTP de DATASUS
    """
    import ftplib

    ftp_host = "ftp.datasus.gov.br"
    sinan_path = "/dissemin/publicos/SINAN/DADOS/FINAIS"

    print(f"\nConectando a {ftp_host}...")

    try:
        ftp = ftplib.FTP(ftp_host, timeout=30)
        ftp.login()  # Login anonimo
        ftp.cwd(sinan_path)

        files = ftp.nlst()
        print(f"  [OK] Encontrados {len(files)} archivos")

        # Filtrar archivos de Sao Paulo
        sp_files = [f for f in files if 'SP' in f.upper() or f.startswith('DENG') or f.startswith('LEPT')]
        print(f"  [OK] Archivos relevantes: {len(sp_files)}")

        ftp.quit()
        return sp_files

    except Exception as e:
        print(f"  [ERROR] FTP: {e}")
        return []


def download_sinan_file(disease_code: str, year: int, uf: str = "SP"):
    """
    Descarga un archivo especifico del SINAN via FTP

    Args:
        disease_code: DENG, LEPT, MALA, LEIV, LTAN
        year: Ano (4 digitos)
        uf: Unidad Federativa (SP)
    """
    import ftplib
    from io import BytesIO

    ftp_host = "ftp.datasus.gov.br"

    # Rutas segun tipo de enfermedad
    paths = {
        "DENG": "/dissemin/publicos/SINAN/DADOS/FINAIS",
        "LEPT": "/dissemin/publicos/SINAN/DADOS/FINAIS",
        "MALA": "/dissemin/publicos/SINAN/DADOS/FINAIS",
        "LEIV": "/dissemin/publicos/SINAN/DADOS/FINAIS",
        "LTAN": "/dissemin/publicos/SINAN/DADOS/FINAIS"
    }

    # Formato del nombre de archivo: DENGSP10.dbc (DENG + UF + ano 2 digitos)
    year_2d = str(year)[-2:]
    filename = f"{disease_code}{uf}{year_2d}.dbc"

    ftp_path = paths.get(disease_code, paths["DENG"])

    print(f"  Buscando {filename}...", end=" ", flush=True)

    try:
        ftp = ftplib.FTP(ftp_host, timeout=30)
        ftp.login()
        ftp.cwd(ftp_path)

        # Verificar si existe el archivo
        files = ftp.nlst()

        if filename in files:
            # Descargar archivo
            buffer = BytesIO()
            ftp.retrbinary(f"RETR {filename}", buffer.write)
            buffer.seek(0)

            # Guardar localmente
            output_path = DATA_RAW / filename
            with open(output_path, 'wb') as f:
                f.write(buffer.read())

            size_kb = output_path.stat().st_size / 1024
            print(f"[OK] Descargado ({size_kb:.1f} KB)")
            ftp.quit()
            return output_path
        else:
            print(f"[NO] No encontrado")
            ftp.quit()
            return None

    except Exception as e:
        print(f"[ERROR] {str(e)[:40]}")
        return None


def create_aggregated_dataset_from_existing():
    """
    Crea dataset agregado usando los datos existentes que ya tenemos
    """
    print("\n" + "="*60)
    print("Procesando datos existentes...")
    print("="*60)

    # Cargar datos existentes
    existing_file = PROJECT_ROOT / "data" / "raw" / "187_con_salud.csv"

    if existing_file.exists():
        try:
            df = pd.read_csv(existing_file, on_bad_lines='skip')
            print(f"  [OK] Cargados {len(df)} municipios con datos de salud")
        except Exception as e:
            print(f"  [ERROR] No se pudo leer: {e}")
            return pd.DataFrame()

        # Columnas de salud disponibles
        health_cols = [c for c in df.columns if 'persist_' in c or 'incidence_' in c]
        print(f"  [OK] Variables de salud: {health_cols}")

        return df
    else:
        print(f"  [NO] Archivo no encontrado: {existing_file}")
        return pd.DataFrame()


def download_via_alternative_api():
    """
    Intenta descargar usando APIs alternativas o web scraping de TabNet
    """
    print("\n" + "="*60)
    print("Metodo alternativo: Extraccion de TabNet")
    print("="*60)

    # TabNet URLs para cada enfermedad
    tabnet_urls = {
        "dengue": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def",
        "leptospirose": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/leptobr.def",
        "malaria": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/malabr.def",
        "leish_visc": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/leishvbr.def",
        "leish_teg": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/ltabr.def"
    }

    print("\nPara descargar manualmente desde TabNet:")
    print("-" * 50)

    for disease, url in tabnet_urls.items():
        print(f"\n{disease.upper()}:")
        print(f"  URL: {url}")
        print(f"  Configuracion:")
        print(f"    - Linha: Munic Resid")
        print(f"    - Coluna: Ano 1o Sintoma")
        print(f"    - Periodos: 2010-2019")
        print(f"    - UF Residencia: Sao Paulo")


def main():
    """Funcion principal"""
    print("="*70)
    print("DATASUS Health Data Downloader - Direct Method")
    print("Science Team - Sao Paulo Biodiversity & Health Project")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*70)

    # Metodo 1: Intentar FTP directo
    print("\n[1/4] Verificando acceso FTP de DATASUS...")
    files = []
    try:
        files = get_ftp_files_list()
        if files:
            print(f"  Archivos encontrados (muestra): {files[:10]}")
    except Exception as e:
        print(f"  Error FTP: {e}")

    # Metodo 2: Descargar archivos especificos
    print("\n[2/4] Intentando descarga de archivos SINAN...")
    downloaded_files = []

    # Los archivos SINAN estan consolidados a nivel Brasil (BR), no por UF
    for disease_code in ["DENG", "LEPT", "MALA", "LEIV", "LTAN"]:
        for year in [2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010]:
            result = download_sinan_file(disease_code, year, "BR")  # BR = Brasil nacional
            if result:
                downloaded_files.append(result)
            time.sleep(0.5)  # Pausa entre requests

    # Metodo 3: Usar datos existentes
    print("\n[3/4] Verificando datos existentes en el proyecto...")
    existing_data = create_aggregated_dataset_from_existing()

    # Metodo 4: Instrucciones manuales
    print("\n[4/4] Generando instrucciones para descarga manual...")
    download_via_alternative_api()

    # Resumen
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Archivos descargados: {len(downloaded_files)}")
    if downloaded_files:
        print("Archivos guardados en:", DATA_RAW)
        for f in downloaded_files:
            print(f"  - {f.name}")
    if not existing_data.empty:
        print(f"Datos existentes: {len(existing_data)} municipios")

    print("\n[!] NOTA IMPORTANTE:")
    print("Los archivos .DBC de DATASUS requieren decodificacion especial.")
    print("Opciones recomendadas:")
    print("  1. Usar TabNet manualmente (URLs proporcionadas arriba)")
    print("  2. Instalar PySUS en un ambiente con Visual C++ Build Tools")
    print("  3. Usar R con el paquete 'microdatasus'")

    # Guardar instrucciones en archivo
    instructions_file = DATA_RAW / "INSTRUCCIONES_DESCARGA.txt"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write("INSTRUCCIONES PARA DESCARGA MANUAL DE DATOS DATASUS\n")
        f.write("="*50 + "\n\n")
        f.write("Fecha: " + datetime.now().strftime('%Y-%m-%d') + "\n\n")
        f.write("OPCION 1: TabNet (Recomendado)\n")
        f.write("-"*30 + "\n")
        for disease, url in {
            "Dengue": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/denguebbr.def",
            "Leptospirose": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/leptobr.def",
            "Malaria": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/malabr.def",
            "Leishmaniose Visceral": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/leishvbr.def",
            "Leishmaniose Tegumentar": "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinannet/cnv/ltabr.def"
        }.items():
            f.write(f"\n{disease}:\n  {url}\n")
        f.write("\nConfiguracion en TabNet:\n")
        f.write("  - Linha: Munic Resid\n")
        f.write("  - Coluna: Ano 1o Sintoma\n")
        f.write("  - Conteudo: Casos confirmados\n")
        f.write("  - Periodos: 2010 a 2019\n")
        f.write("  - UF Residencia: Sao Paulo\n")
        f.write("\nExportar como CSV y guardar en esta carpeta.\n")

    print(f"\n[OK] Instrucciones guardadas en: {instructions_file}")

    return downloaded_files


if __name__ == "__main__":
    downloaded = main()

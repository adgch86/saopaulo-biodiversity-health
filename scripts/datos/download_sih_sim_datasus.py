# -*- coding: utf-8 -*-
"""
Script para descargar datos de SIH (Hospitalizaciones) y SIM (Mortalidade) de DATASUS
=====================================================================================

Este script descarga archivos DBC del FTP de DATASUS para análisis de:
- Hospitalizaciones por doenças circulatórias (CID-10: I00-I99)
- Hospitalizaciones por doenças respiratórias (CID-10: J00-J99)
- Hospitalizaciones por efeitos do calor (CID-10: T67.0-T67.9)
- Óbitos por las mismas causas

Período: 2010-2019
Estado: São Paulo (SP)

Autor: Science Team / Data Engineer - Ing. Roberto Silva
Fecha: 2026-01-23
"""

import os
import sys
import ftplib
from pathlib import Path
from datetime import datetime
import time

# Forzar encoding UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Configuración de paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_SIH = PROJECT_ROOT / "data" / "raw" / "datasus" / "sih"
DATA_RAW_SIM = PROJECT_ROOT / "data" / "raw" / "datasus" / "sim"

# Crear directorios si no existen
DATA_RAW_SIH.mkdir(parents=True, exist_ok=True)
DATA_RAW_SIM.mkdir(parents=True, exist_ok=True)

# Configuración FTP DATASUS
FTP_HOST = "ftp.datasus.gov.br"
FTP_TIMEOUT = 60

# Rutas FTP para cada sistema
FTP_PATHS = {
    "SIH": "/dissemin/publicos/SIHSUS/200801_/Dados/",
    "SIM": "/dissemin/publicos/SIM/CID10/DORES/"
}

# Años de interés
YEARS = list(range(2010, 2020))

# UF de São Paulo
UF = "SP"


def connect_ftp():
    """Conecta al FTP de DATASUS"""
    print(f"Conectando a {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST, timeout=FTP_TIMEOUT)
        ftp.login()  # Login anónimo
        print(f"  [OK] Conectado exitosamente")
        return ftp
    except Exception as e:
        print(f"  [ERROR] No se pudo conectar: {e}")
        return None


def list_files_in_path(ftp, path, pattern=None):
    """Lista archivos en un directorio FTP"""
    try:
        ftp.cwd(path)
        files = ftp.nlst()
        if pattern:
            files = [f for f in files if pattern in f.upper()]
        return files
    except Exception as e:
        print(f"  [ERROR] No se pudo listar {path}: {e}")
        return []


def download_file(ftp, remote_path, local_path):
    """Descarga un archivo del FTP"""
    try:
        with open(local_path, 'wb') as f:
            ftp.retrbinary(f'RETR {remote_path}', f.write)
        size_mb = local_path.stat().st_size / (1024 * 1024)
        print(f"    [OK] {local_path.name} ({size_mb:.2f} MB)")
        return True
    except Exception as e:
        print(f"    [ERROR] {remote_path}: {e}")
        return False


def download_sih_files():
    """
    Descarga archivos de SIH (Sistema de Informações Hospitalares)

    Estructura de archivos SIH:
    - RD{UF}{AAMM}.dbc - Datos reducidos de AIH (Autorização de Internação Hospitalar)
    - Ejemplo: RDSP1001.dbc = São Paulo, Enero 2010
    """
    print("\n" + "=" * 70)
    print("DESCARGA DE DATOS SIH (Hospitalizaciones)")
    print("=" * 70)

    ftp = connect_ftp()
    if not ftp:
        return []

    downloaded = []

    try:
        ftp.cwd(FTP_PATHS["SIH"])
        print(f"Directorio: {FTP_PATHS['SIH']}")

        # Listar todos los archivos disponibles
        all_files = ftp.nlst()
        print(f"Total archivos en directorio: {len(all_files)}")

        # Filtrar archivos de SP para los años de interés
        # Formato: RDSP{AAMM}.dbc donde AA = año (2 dígitos), MM = mes
        files_to_download = []
        for year in YEARS:
            year_2d = str(year)[-2:]
            for month in range(1, 13):
                filename = f"RD{UF}{year_2d}{month:02d}.dbc"
                if filename in all_files:
                    files_to_download.append(filename)
                else:
                    # Verificar si existe con mayúsculas/minúsculas diferentes
                    for f in all_files:
                        if f.upper() == filename.upper():
                            files_to_download.append(f)
                            break

        print(f"\nArchivos de SP (2010-2019) encontrados: {len(files_to_download)}")

        # Verificar cuáles ya existen localmente
        files_to_download_new = []
        for f in files_to_download:
            local_file = DATA_RAW_SIH / f
            if not local_file.exists():
                files_to_download_new.append(f)
            else:
                print(f"  [SKIP] {f} ya existe")
                downloaded.append(local_file)

        print(f"Archivos a descargar: {len(files_to_download_new)}")

        # Descargar archivos nuevos
        for i, filename in enumerate(files_to_download_new, 1):
            print(f"\n  [{i}/{len(files_to_download_new)}] Descargando {filename}...", end="")
            local_path = DATA_RAW_SIH / filename
            if download_file(ftp, filename, local_path):
                downloaded.append(local_path)
            time.sleep(0.5)  # Pausa entre descargas

    except Exception as e:
        print(f"[ERROR] Error durante descarga SIH: {e}")
    finally:
        ftp.quit()

    print(f"\n[RESUMEN SIH] Archivos descargados: {len(downloaded)}")
    return downloaded


def download_sim_files():
    """
    Descarga archivos de SIM (Sistema de Informação sobre Mortalidade)

    Estructura de archivos SIM:
    - DO{UF}{AAAA}.dbc - Declarações de Óbito por UF y año
    - Ejemplo: DOSP2010.dbc = São Paulo, 2010
    """
    print("\n" + "=" * 70)
    print("DESCARGA DE DATOS SIM (Mortalidade)")
    print("=" * 70)

    ftp = connect_ftp()
    if not ftp:
        return []

    downloaded = []

    try:
        ftp.cwd(FTP_PATHS["SIM"])
        print(f"Directorio: {FTP_PATHS['SIM']}")

        # Listar todos los archivos disponibles
        all_files = ftp.nlst()
        print(f"Total archivos en directorio: {len(all_files)}")

        # Filtrar archivos de SP para los años de interés
        # Formato: DO{UF}{AAAA}.dbc donde AAAA = año completo
        files_to_download = []
        for year in YEARS:
            filename = f"DO{UF}{year}.dbc"
            if filename in all_files:
                files_to_download.append(filename)
            else:
                # Buscar variaciones
                for f in all_files:
                    if f.upper() == filename.upper():
                        files_to_download.append(f)
                        break

        print(f"\nArchivos de SP (2010-2019) encontrados: {len(files_to_download)}")

        # Verificar cuáles ya existen localmente
        files_to_download_new = []
        for f in files_to_download:
            local_file = DATA_RAW_SIM / f
            if not local_file.exists():
                files_to_download_new.append(f)
            else:
                print(f"  [SKIP] {f} ya existe")
                downloaded.append(local_file)

        print(f"Archivos a descargar: {len(files_to_download_new)}")

        # Descargar archivos nuevos
        for i, filename in enumerate(files_to_download_new, 1):
            print(f"\n  [{i}/{len(files_to_download_new)}] Descargando {filename}...", end="")
            local_path = DATA_RAW_SIM / filename
            if download_file(ftp, filename, local_path):
                downloaded.append(local_path)
            time.sleep(0.5)

    except Exception as e:
        print(f"[ERROR] Error durante descarga SIM: {e}")
    finally:
        ftp.quit()

    print(f"\n[RESUMEN SIM] Archivos descargados: {len(downloaded)}")
    return downloaded


def main():
    """Función principal"""
    print("=" * 70)
    print("DATASUS - Descarga de datos SIH y SIM")
    print("Science Team - São Paulo Biodiversity & Health Project")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    print("\nObjetivo: Descargar datos de hospitalizaciones (SIH) y óbitos (SIM)")
    print("para análisis de impactos del calor en salud cardiovascular y respiratoria")
    print(f"\nPeríodo: 2010-2019")
    print(f"Estado: São Paulo (UF={UF})")
    print(f"\nCID-10 de interés:")
    print("  - I00-I99: Doenças do aparelho circulatório")
    print("  - J00-J99: Doenças do aparelho respiratório")
    print("  - T67.0-T67.9: Efeitos do calor e da luz")

    # Descargar SIH
    sih_files = download_sih_files()

    # Descargar SIM
    sim_files = download_sim_files()

    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"Archivos SIH descargados: {len(sih_files)}")
    print(f"Archivos SIM descargados: {len(sim_files)}")
    print(f"\nDirectorios de datos:")
    print(f"  SIH: {DATA_RAW_SIH}")
    print(f"  SIM: {DATA_RAW_SIM}")

    if sih_files or sim_files:
        print("\n[!] PRÓXIMO PASO:")
        print("Ejecutar el script R 'process_sih_sim_data.R' para procesar los archivos DBC")
        print("y extraer las hospitalizaciones y óbitos por CID-10 específicos.")

    return sih_files, sim_files


if __name__ == "__main__":
    sih, sim = main()

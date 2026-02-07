#!/usr/bin/env python3
"""
=============================================================================
Watch Papers Daily - Conversión automática de PDFs a Markdown
=============================================================================

Este script revisa diariamente la carpeta de Papers y convierte
automáticamente los PDFs nuevos a Markdown.

Uso:
    python scripts/watch_papers_daily.py

Para programar ejecucion diaria en Windows:
    1. Abrir Task Scheduler (Programador de tareas)
    2. Crear tarea basica
    3. Trigger: Diariamente a las 8:00 AM (o la hora preferida)
    4. Accion: Iniciar programa
       - Programa: python
       - Argumentos: scripts/watch_papers_daily.py
       - Iniciar en: C:/Users/arlex/Documents/Adrian David

Autor: Science Team
Fecha: 2026-01-21
=============================================================================
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Directorios
PAPERS_DIR = Path(r"G:\My Drive\Adrian David\Papers")
OUTPUT_DIR = Path(r"G:\My Drive\Adrian David\Papers\markdown")
LOG_DIR = Path(r"C:\Users\arlex\Documents\Adrian David\logs")

# Crear directorio de logs si no existe
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configurar logging
log_file = LOG_DIR / f"papers_conversion_{datetime.now().strftime('%Y%m')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTAR LIBRERÍAS DE CONVERSIÓN
# =============================================================================

try:
    import fitz  # PyMuPDF
except ImportError:
    logger.error("PyMuPDF no está instalado. Instalar con: pip install pymupdf")
    sys.exit(1)

try:
    import pymupdf4llm
    USE_ADVANCED = True
except ImportError:
    logger.warning("pymupdf4llm no instalado. Usando extracción básica.")
    pymupdf4llm = None
    USE_ADVANCED = False


# =============================================================================
# FUNCIONES DE CONVERSIÓN (copiadas de convert_papers_to_md.py)
# =============================================================================

def sanitize_filename(filename: str) -> str:
    """Limpia el nombre del archivo para usarlo como título."""
    import re
    name = Path(filename).stem
    name = re.sub(r'[^\w\s\-_]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def extract_text_basic(pdf_path: str, show_progress: bool = False) -> str:
    """Extracción básica de texto con PyMuPDF."""
    doc = fitz.open(pdf_path)
    text_parts = []
    total_pages = len(doc)

    for page_num, page in enumerate(doc, 1):
        if show_progress and page_num % 50 == 0:
            logger.info(f"    Página {page_num}/{total_pages}...")
        text = page.get_text("text")
        if text.strip():
            text_parts.append(f"\n## Página {page_num}\n\n{text}")

    doc.close()
    return "\n".join(text_parts)


def extract_text_advanced(pdf_path: str) -> str:
    """Extracción avanzada con pymupdf4llm."""
    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        return md_text
    except Exception as e:
        logger.warning(f"Error con pymupdf4llm, usando método básico: {e}")
        return extract_text_basic(pdf_path, show_progress=True)


def convert_pdf_to_md(pdf_path: Path, output_dir: Path) -> tuple:
    """Convierte un PDF a Markdown."""
    output_name = sanitize_filename(pdf_path.name) + ".md"
    output_path = output_dir / output_name

    try:
        # Verificar tamaño del archivo
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        is_large = file_size_mb > 10

        if is_large:
            logger.info(f"  Archivo grande ({file_size_mb:.1f} MB), usando método básico...")
            md_content = extract_text_basic(str(pdf_path), show_progress=True)
        elif USE_ADVANCED:
            md_content = extract_text_advanced(str(pdf_path))
        else:
            md_content = extract_text_basic(str(pdf_path))

        if not md_content.strip():
            return False, "PDF vacío o sin texto extraíble"

        # Crear encabezado
        header = f"""# {sanitize_filename(pdf_path.name)}

> **Archivo original**: `{pdf_path.name}`
> **Convertido**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **Science Team** - Dr. Adrian David González Chaves

---

"""

        output_path.write_text(header + md_content, encoding="utf-8")
        return True, output_path

    except Exception as e:
        return False, str(e)


def create_index(output_dir: Path):
    """Crea un archivo índice con todos los papers convertidos."""
    md_files = sorted(output_dir.glob("*.md"))
    md_files = [f for f in md_files if f.name != "_INDEX.md"]

    if not md_files:
        return

    index_content = f"""# Índice de Papers - Science Team

> Generado automáticamente
> Dr. Adrian David González Chaves
> Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Papers Disponibles ({len(md_files)} archivos)

| # | Paper | Archivo |
|---|-------|---------|
"""

    for i, md_file in enumerate(md_files, 1):
        name = md_file.stem
        index_content += f"| {i} | {name[:60]}{'...' if len(name) > 60 else ''} | [{md_file.name}]({md_file.name}) |\n"

    index_content += """

---

*Generado por `watch_papers_daily.py`*
"""

    index_path = output_dir / "_INDEX.md"
    index_path.write_text(index_content, encoding="utf-8")


# =============================================================================
# FUNCIÓN PRINCIPAL: DETECTAR Y CONVERTIR NUEVOS PAPERS
# =============================================================================

def get_converted_papers(output_dir: Path) -> set:
    """Obtiene el conjunto de papers ya convertidos."""
    if not output_dir.exists():
        return set()

    converted = set()
    for md_file in output_dir.glob("*.md"):
        if md_file.name != "_INDEX.md":
            # El nombre del MD es el nombre sanitizado del PDF
            converted.add(md_file.stem.lower())

    return converted


def get_pdf_papers(papers_dir: Path) -> list:
    """Obtiene la lista de PDFs en el directorio."""
    if not papers_dir.exists():
        return []
    return list(papers_dir.glob("*.pdf"))


def find_new_papers(papers_dir: Path, output_dir: Path) -> list:
    """Encuentra PDFs que aún no han sido convertidos."""
    converted = get_converted_papers(output_dir)
    pdfs = get_pdf_papers(papers_dir)

    new_papers = []
    for pdf in pdfs:
        sanitized_name = sanitize_filename(pdf.name).lower()
        if sanitized_name not in converted:
            new_papers.append(pdf)

    return new_papers


def run_daily_check():
    """Ejecuta la revisión diaria y convierte papers nuevos."""
    logger.info("=" * 60)
    logger.info("WATCH PAPERS DAILY - Inicio de revisión")
    logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Verificar que el directorio de Papers existe
    if not PAPERS_DIR.exists():
        logger.error(f"Directorio no encontrado: {PAPERS_DIR}")
        logger.error("Verificar que Google Drive está sincronizado.")
        return False

    # Crear directorio de salida si no existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Buscar papers nuevos
    new_papers = find_new_papers(PAPERS_DIR, OUTPUT_DIR)
    total_pdfs = len(list(PAPERS_DIR.glob("*.pdf")))

    logger.info(f"PDFs en carpeta: {total_pdfs}")
    logger.info(f"Papers nuevos detectados: {len(new_papers)}")

    if not new_papers:
        logger.info("No hay papers nuevos para convertir.")
        logger.info("=" * 60)
        return True

    # Convertir papers nuevos
    logger.info(f"\nConvirtiendo {len(new_papers)} papers nuevos...")
    logger.info("-" * 60)

    success_count = 0
    error_count = 0
    errors = []

    for i, pdf in enumerate(new_papers, 1):
        logger.info(f"\n[{i}/{len(new_papers)}] {pdf.name[:50]}...")

        success, result = convert_pdf_to_md(pdf, OUTPUT_DIR)

        if success:
            success_count += 1
            logger.info(f"  OK: {Path(result).name}")
        else:
            error_count += 1
            errors.append(f"{pdf.name}: {result}")
            logger.error(f"  ERROR: {result}")

    # Actualizar índice
    create_index(OUTPUT_DIR)

    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DE CONVERSIÓN")
    logger.info("=" * 60)
    logger.info(f"Papers nuevos: {len(new_papers)}")
    logger.info(f"Convertidos exitosamente: {success_count}")
    logger.info(f"Errores: {error_count}")

    if errors:
        logger.info("\nErrores encontrados:")
        for error in errors:
            logger.info(f"  - {error}")

    logger.info(f"\nArchivos en: {OUTPUT_DIR}")
    logger.info(f"Log guardado en: {log_file}")
    logger.info("=" * 60)

    return error_count == 0


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    try:
        success = run_daily_check()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.exception(f"Error inesperado: {e}")
        sys.exit(1)

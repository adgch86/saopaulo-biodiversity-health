#!/usr/bin/env python3
"""
Script para convertir PDFs de papers científicos a Markdown
Science Team - Dr. Adrian David González Chaves

Uso:
    # Convertir todos los PDFs
    python scripts/convert_papers_to_md.py

    # Convertir un archivo específico
    python scripts/convert_papers_to_md.py --file "nombre_archivo.pdf"

    # Usar método básico (más rápido para libros grandes)
    python scripts/convert_papers_to_md.py --basic

    # Saltar archivos ya convertidos
    python scripts/convert_papers_to_md.py --skip-existing

Dependencias:
    pip install pymupdf pymupdf4llm
"""

import os
import sys
from pathlib import Path
import re
import argparse

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Intentar importar las librerías necesarias
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF no está instalado.")
    print("Instalar con: pip install pymupdf")
    sys.exit(1)

try:
    import pymupdf4llm
except ImportError:
    print("Advertencia: pymupdf4llm no está instalado. Usando extracción básica.")
    print("Para mejor formato: pip install pymupdf4llm")
    pymupdf4llm = None


# Configuración de rutas por defecto
DEFAULT_PAPERS_DIR = Path(r"G:\My Drive\Adrian David\Papers")
DEFAULT_OUTPUT_DIR = Path(r"G:\My Drive\Adrian David\Papers\markdown")


def sanitize_filename(filename: str) -> str:
    """Limpia el nombre del archivo para usarlo como título."""
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
            print(f"    Página {page_num}/{total_pages}...")
        text = page.get_text("text")
        if text.strip():
            text_parts.append(f"\n## Página {page_num}\n\n{text}")

    doc.close()
    return "\n".join(text_parts)


def extract_text_advanced(pdf_path: str) -> str:
    """Extracción avanzada con pymupdf4llm (mejor formato Markdown)."""
    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        return md_text
    except Exception as e:
        print(f"  Advertencia: Error con pymupdf4llm, usando método básico: {e}")
        return extract_text_basic(pdf_path, show_progress=True)


def get_output_filename(pdf_path: Path) -> str:
    """Genera el nombre del archivo de salida."""
    return sanitize_filename(pdf_path.name) + ".md"


def convert_pdf_to_md(
    pdf_path: str,
    output_dir: str,
    use_advanced: bool = True,
    skip_existing: bool = False
) -> tuple[bool, str]:
    """
    Convierte un PDF a Markdown.

    Returns:
        (success: bool, message: str)
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    output_name = get_output_filename(pdf_path)
    output_path = output_dir / output_name

    # Verificar si ya existe
    if skip_existing and output_path.exists():
        return True, f"SKIP (ya existe): {output_name}"

    try:
        # Verificar tamaño del archivo para decidir método
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        is_large = file_size_mb > 10  # Más de 10MB = archivo grande

        if is_large:
            print(f"  Archivo grande ({file_size_mb:.1f} MB), usando método básico...")
            md_content = extract_text_basic(str(pdf_path), show_progress=True)
        elif use_advanced and pymupdf4llm:
            md_content = extract_text_advanced(str(pdf_path))
        else:
            md_content = extract_text_basic(str(pdf_path))

        if not md_content.strip():
            return False, f"PDF vacío o sin texto extraíble: {pdf_path.name}"

        # Crear encabezado con metadata
        header = f"""# {sanitize_filename(pdf_path.name)}

> **Archivo original**: `{pdf_path.name}`
> **Convertido automáticamente** por Science Team

---

"""

        output_path.write_text(header + md_content, encoding="utf-8")
        return True, str(output_path)

    except Exception as e:
        return False, f"Error procesando {pdf_path.name}: {str(e)}"


def create_index(output_dir: Path):
    """Crea un archivo índice con todos los papers convertidos."""
    md_files = sorted(output_dir.glob("*.md"))
    md_files = [f for f in md_files if f.name != "_INDEX.md"]

    if not md_files:
        return

    index_content = """# Índice de Papers - Science Team

> Generado automáticamente por el script de conversión
> Dr. Adrian David González Chaves

## Papers Disponibles ({count} archivos)

| # | Paper | Archivo |
|---|-------|---------|
""".format(count=len(md_files))

    for i, md_file in enumerate(md_files, 1):
        name = md_file.stem
        index_content += f"| {i} | {name[:60]}{'...' if len(name) > 60 else ''} | [{md_file.name}]({md_file.name}) |\n"

    index_content += """

---

*Última actualización: generado por `convert_papers_to_md.py`*
"""

    index_path = output_dir / "_INDEX.md"
    index_path.write_text(index_content, encoding="utf-8")
    print(f"\nÍndice creado: {index_path}")


def convert_single_file(filename: str, use_advanced: bool = True):
    """Convierte un único archivo PDF."""
    papers_dir = DEFAULT_PAPERS_DIR
    output_dir = DEFAULT_OUTPUT_DIR

    # Buscar el archivo
    pdf_path = papers_dir / filename
    if not pdf_path.exists():
        # Buscar por coincidencia parcial
        matches = list(papers_dir.glob(f"*{filename}*"))
        if matches:
            pdf_path = matches[0]
            print(f"Encontrado: {pdf_path.name}")
        else:
            print(f"Error: No se encontró el archivo: {filename}")
            return

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Convirtiendo: {pdf_path.name}")
    success, message = convert_pdf_to_md(str(pdf_path), str(output_dir), use_advanced)

    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")

    # Actualizar índice
    create_index(output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Convertir PDFs de papers científicos a Markdown"
    )
    parser.add_argument(
        "--file", "-f",
        help="Convertir un archivo específico (nombre o parte del nombre)"
    )
    parser.add_argument(
        "--basic", "-b",
        action="store_true",
        help="Usar método básico (más rápido, menos formato)"
    )
    parser.add_argument(
        "--skip-existing", "-s",
        action="store_true",
        help="Saltar archivos ya convertidos"
    )
    parser.add_argument(
        "--input-dir", "-i",
        default=str(DEFAULT_PAPERS_DIR),
        help="Directorio de entrada con PDFs"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directorio de salida para archivos MD"
    )

    args = parser.parse_args()

    use_advanced = not args.basic and pymupdf4llm is not None

    # Modo archivo único
    if args.file:
        convert_single_file(args.file, use_advanced)
        return

    # Modo batch
    papers_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not papers_dir.exists():
        print(f"Error: No se encuentra el directorio: {papers_dir}")
        print("Verificar que Google Drive está sincronizado.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(papers_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No se encontraron PDFs en: {papers_dir}")
        sys.exit(1)

    print("=" * 60)
    print("CONVERSIÓN DE PAPERS A MARKDOWN")
    print("Science Team - Dr. Adrian David González Chaves")
    print("=" * 60)
    print(f"\nDirectorio de entrada: {papers_dir}")
    print(f"Directorio de salida: {output_dir}")
    print(f"PDFs encontrados: {len(pdf_files)}")
    print(f"Método: {'pymupdf4llm (avanzado)' if use_advanced else 'PyMuPDF (básico)'}")
    print(f"Saltar existentes: {'Sí' if args.skip_existing else 'No'}")
    print("\n" + "-" * 60)

    success_count = 0
    skip_count = 0
    error_count = 0
    errors = []

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Procesando: {pdf_file.name[:50]}...")

        success, message = convert_pdf_to_md(
            str(pdf_file),
            str(output_dir),
            use_advanced=use_advanced,
            skip_existing=args.skip_existing
        )

        if success:
            if "SKIP" in message:
                skip_count += 1
                print(f"  → {message}")
            else:
                success_count += 1
                print(f"  ✓ Guardado: {Path(message).name}")
        else:
            error_count += 1
            errors.append(message)
            print(f"  ✗ {message}")

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Total procesados: {len(pdf_files)}")
    print(f"Convertidos: {success_count}")
    print(f"Saltados (ya existían): {skip_count}")
    print(f"Errores: {error_count}")
    print(f"\nArchivos guardados en: {output_dir}")

    if errors:
        print(f"\nErrores encontrados:")
        for error in errors:
            print(f"  - {error}")

    create_index(output_dir)


if __name__ == "__main__":
    main()

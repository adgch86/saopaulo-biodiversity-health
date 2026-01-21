#!/usr/bin/env python
"""
Transcriptor de Audio para Science Team
========================================
Utiliza OpenAI Whisper para transcribir notas de voz y audios.

Uso desde línea de comandos:
    python transcribe_audio.py "ruta/al/audio.ogg"
    python transcribe_audio.py "ruta/al/audio.mp3" --model medium
    python transcribe_audio.py "ruta/al/audio.wav" --language en

Uso como módulo:
    from transcribe_audio import transcribe_audio
    texto = transcribe_audio("audio.ogg")

Modelos disponibles (de menor a mayor precisión/tiempo):
    - tiny: Más rápido, menor precisión (~1GB RAM)
    - base: Balance básico (~1GB RAM)
    - small: Recomendado para español (~2GB RAM) [default]
    - medium: Mayor precisión (~5GB RAM)
    - large: Máxima precisión (~10GB RAM)

Requisitos:
    pip install openai-whisper
    # También necesita ffmpeg instalado en el sistema
"""

import argparse
import os
import sys
from pathlib import Path

# Agregar ffmpeg al PATH (configuración específica para esta máquina)
ffmpeg_path = r"C:\Users\arlex\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")


def transcribe_audio(audio_path: str, model_name: str = "small", language: str = "es",
                     output_dir: str = None) -> str:
    """
    Transcribe un archivo de audio usando Whisper.

    Args:
        audio_path: Ruta al archivo de audio
        model_name: Nombre del modelo Whisper (tiny, base, small, medium, large)
        language: Código de idioma (es, en, pt, etc.)
        output_dir: Directorio para guardar la transcripción (opcional)

    Returns:
        Texto transcrito
    """
    try:
        import whisper
    except ImportError:
        print("Error: Whisper no está instalado.")
        print("Instala con: pip install openai-whisper")
        sys.exit(1)

    # Verificar que el archivo existe
    if not os.path.exists(audio_path):
        print(f"Error: No se encontró el archivo: {audio_path}")
        sys.exit(1)

    print(f"Cargando modelo '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribiendo: {audio_path}")
    print(f"Idioma: {language}")

    result = model.transcribe(audio_path, language=language)
    text = result["text"]

    # Guardar transcripción si se especificó directorio
    if output_dir:
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Transcripción guardada en: {output_path}")

    return text


def save_transcription(text: str, output_path: str) -> None:
    """Guarda la transcripción en un archivo de texto."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Transcripción guardada en: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe archivos de audio usando Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
    python transcribe_audio.py "audio.ogg"                    # Transcribir con modelo small
    python transcribe_audio.py "audio.mp3" -m medium          # Usar modelo medium
    python transcribe_audio.py "audio.wav" -l en              # Transcribir en inglés
    python transcribe_audio.py "audio.ogg" -o salida.txt      # Guardar en archivo específico
    python transcribe_audio.py "audio.ogg" -p                 # Solo mostrar, no guardar
        """
    )

    parser.add_argument(
        "audio_file",
        nargs="?",  # Hacer opcional para modo batch
        help="Ruta al archivo de audio a transcribir"
    )

    parser.add_argument(
        "--model", "-m",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Modelo Whisper a usar (default: small)"
    )

    parser.add_argument(
        "--language", "-l",
        default="es",
        help="Código de idioma (default: es para español)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Ruta para guardar la transcripción (default: mismo nombre con .txt)"
    )

    parser.add_argument(
        "--output-dir", "-d",
        help="Directorio para guardar las transcripciones"
    )

    parser.add_argument(
        "--print-only", "-p",
        action="store_true",
        help="Solo imprimir, no guardar archivo"
    )

    args = parser.parse_args()

    # Si no se proporciona archivo, mostrar ayuda
    if not args.audio_file:
        parser.print_help()
        sys.exit(0)

    # Determinar directorio de salida
    output_dir = args.output_dir if args.output_dir else (
        os.path.dirname(args.audio_file) if not args.print_only else None
    )

    # Transcribir
    text = transcribe_audio(
        args.audio_file,
        args.model,
        args.language,
        output_dir=None  # Manejamos el guardado aquí
    )

    # Mostrar resultado
    print("\n" + "="*60)
    print("TRANSCRIPCIÓN:")
    print("="*60)
    print(text)
    print("="*60 + "\n")

    # Guardar si no es print-only
    if not args.print_only:
        if args.output:
            output_path = args.output
        else:
            audio_path = Path(args.audio_file)
            if args.output_dir:
                output_path = os.path.join(args.output_dir, audio_path.stem + ".txt")
            else:
                output_path = str(audio_path.with_suffix(".txt"))

        save_transcription(text, output_path)

    return text


if __name__ == "__main__":
    main()

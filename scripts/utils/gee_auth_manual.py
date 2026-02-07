"""
Autenticación manual de Google Earth Engine
"""
import ee
import webbrowser

print("=" * 60)
print("AUTENTICACION MANUAL DE GOOGLE EARTH ENGINE")
print("=" * 60)
print()

# Generar URL de autenticación
auth_url = "https://code.earthengine.google.com/register"

print("PASO 1: Abre esta URL en tu navegador:")
print()
print(auth_url)
print()

# Intentar abrir el navegador
try:
    webbrowser.open(auth_url)
    print("(Intentando abrir navegador automaticamente...)")
except:
    print("(No se pudo abrir automaticamente, copia la URL)")

print()
print("PASO 2: En la pagina de Earth Engine:")
print("   - Inicia sesion con tu cuenta Google")
print("   - Registra un proyecto (puede ser 'earthengine-legacy')")
print("   - O crea uno nuevo en Google Cloud Console")
print()
print("PASO 3: Cuando termines, escribe el nombre del proyecto aqui")
print("   (ejemplo: earthengine-legacy, ee-miproyecto, etc.)")
print()

project = input("Nombre del proyecto GCP: ").strip()

if not project:
    project = "earthengine-legacy"
    print(f"Usando proyecto por defecto: {project}")

print()
print("Intentando autenticar...")

try:
    ee.Authenticate(force=True)
    ee.Initialize(project=project)

    # Test rapido
    test = ee.Number(1).add(1).getInfo()
    print()
    print("=" * 60)
    print("EXITO! Earth Engine esta listo.")
    print(f"Proyecto: {project}")
    print("Test: 1 + 1 =", test)
    print("=" * 60)

    # Guardar proyecto para uso futuro
    with open("gee_project.txt", "w") as f:
        f.write(project)
    print(f"\nProyecto guardado en gee_project.txt")

except Exception as e:
    print()
    print("ERROR:", e)
    print()
    print("Posibles soluciones:")
    print("1. Verifica que completaste el registro en Earth Engine")
    print("2. Intenta con proyecto 'earthengine-legacy'")
    print("3. Crea un proyecto en https://console.cloud.google.com/")

input("\nPresiona Enter para cerrar...")

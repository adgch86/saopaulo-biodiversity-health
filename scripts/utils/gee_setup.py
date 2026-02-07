"""
Setup completo de Google Earth Engine
"""
import ee
import sys

print("=" * 60)
print("SETUP DE GOOGLE EARTH ENGINE")
print("=" * 60)
print()

# Paso 1: Autenticar
print("PASO 1: Autenticacion")
print("-" * 40)
print("Se abrira el navegador. Completa el login y copia el codigo.")
print()

try:
    ee.Authenticate(force=True)
    print("Autenticacion guardada.")
except Exception as e:
    print(f"Error: {e}")
    input("Presiona Enter para salir...")
    sys.exit(1)

# Paso 2: Probar proyectos
print()
print("PASO 2: Probando proyectos...")
print("-" * 40)

proyectos_a_probar = [
    'earthengine-legacy',
    'earthengine-public',
    'ee-defaults',
]

proyecto_ok = None

for proj in proyectos_a_probar:
    try:
        ee.Initialize(project=proj)
        test = ee.Number(1).add(1).getInfo()
        if test == 2:
            proyecto_ok = proj
            print(f"  {proj}: OK")
            break
    except Exception as e:
        print(f"  {proj}: No disponible")

if not proyecto_ok:
    print()
    print("Ninguno de los proyectos por defecto funciona.")
    print("Necesitas crear tu propio proyecto en Google Cloud.")
    print()
    print("1. Ve a: https://console.cloud.google.com/projectcreate")
    print("2. Crea un proyecto (ej: mi-proyecto-gee)")
    print("3. Ve a: https://code.earthengine.google.com/register")
    print("4. Registra ese proyecto para Earth Engine")
    print()
    proyecto = input("Escribe el ID del proyecto que creaste: ").strip()

    if proyecto:
        try:
            ee.Initialize(project=proyecto)
            test = ee.Number(1).add(1).getInfo()
            if test == 2:
                proyecto_ok = proyecto
                print(f"Proyecto {proyecto}: OK")
        except Exception as e:
            print(f"Error: {e}")

if proyecto_ok:
    print()
    print("=" * 60)
    print(f"EXITO! Earth Engine listo con proyecto: {proyecto_ok}")
    print("=" * 60)

    # Guardar para uso futuro
    with open("gee_project.txt", "w") as f:
        f.write(proyecto_ok)
    print(f"Proyecto guardado en gee_project.txt")
else:
    print()
    print("No se pudo configurar Earth Engine.")
    print("Contacta a Adrian para obtener acceso a un proyecto GCP.")

print()
input("Presiona Enter para cerrar...")

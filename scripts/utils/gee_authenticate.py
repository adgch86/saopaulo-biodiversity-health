"""
Script para autenticar Google Earth Engine
Ejecutar directamente: python gee_authenticate.py
"""
import ee

print("=" * 50)
print("AUTENTICACION DE GOOGLE EARTH ENGINE")
print("=" * 50)
print()
print("Se abrira el navegador para autenticar.")
print("Sigue las instrucciones en el navegador.")
print()

try:
    ee.Authenticate(force=True)
    print()
    print("Autenticacion completada!")
    print()

    # Intentar inicializar con proyecto por defecto
    try:
        ee.Initialize(project='earthengine-legacy')
        print("Inicializado con proyecto: earthengine-legacy")
    except:
        try:
            ee.Initialize(project='ee-defaults')
            print("Inicializado con proyecto: ee-defaults")
        except Exception as e:
            print(f"Necesitas especificar un proyecto GCP.")
            print(f"Error: {e}")
            print()
            print("Opciones:")
            print("1. Crear proyecto en: https://console.cloud.google.com/")
            print("2. Registrar proyecto en: https://code.earthengine.google.com/register")

except Exception as e:
    print(f"Error en autenticacion: {e}")

input("\nPresiona Enter para cerrar...")

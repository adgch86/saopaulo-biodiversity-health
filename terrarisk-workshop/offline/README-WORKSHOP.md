# TerraRisk Workshop - Instalacion Offline

## Requisitos

- **Docker Desktop** instalado y corriendo
  - Windows: https://www.docker.com/products/docker-desktop/
  - Mac: https://www.docker.com/products/docker-desktop/
  - Linux: `sudo apt install docker.io docker-compose-plugin`
- **4 GB de RAM** disponible (Docker usa ~2GB)
- **2 GB de disco** libre

## Instalacion (5 minutos)

### Windows
1. Abrir Docker Desktop y esperar a que inicie (icono verde)
2. Doble clic en `install.bat`
3. Esperar a que termine (~2-3 minutos)
4. Abrir navegador en **http://localhost:4001**

### Mac / Linux
1. Abrir Docker Desktop (o iniciar servicio Docker)
2. Abrir terminal en esta carpeta
3. Ejecutar: `chmod +x install.sh && ./install.sh`
4. Abrir navegador en **http://localhost:4001**

## Uso durante el Workshop

- **URL:** http://localhost:4001
- El mapa funciona sin internet (tiles pre-descargados)
- Los datos de municipios estan incluidos
- Cada grupo puede comprar capas y generar mapas bivariados

## Detener TerraRisk

### Windows
Doble clic en `stop.bat`

### Mac / Linux
```bash
./stop.sh
```

## Problemas comunes

| Problema | Solucion |
|----------|----------|
| "Docker no esta corriendo" | Abrir Docker Desktop y esperar 1-2 minutos |
| Pagina no carga | Esperar 30 segundos despues de install, el backend necesita iniciar |
| Mapa sin fondo | Los tiles deberian estar incluidos. Si falla, funciona con internet |
| Puerto 4001 ocupado | Cerrar otra app que use ese puerto, o editar docker-compose.offline.yml |

## Contacto

Si hay problemas durante el workshop:
- Arlex Peralta: [contacto]
- Adrian David: [contacto]

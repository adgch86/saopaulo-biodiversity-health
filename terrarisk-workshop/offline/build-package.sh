#!/bin/bash
# ================================================
# TerraRisk Offline Package Builder
# Run this on the SERVER (Contabo) to create the
# downloadable package for Adrian's workshop.
# ================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PACKAGE_DIR="$SCRIPT_DIR/terrarisk-offline"

echo "=== TerraRisk Offline Package Builder ==="
echo "Project: $PROJECT_DIR"
echo "Output:  $PACKAGE_DIR"
echo ""

# Clean previous build
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/images"
mkdir -p "$PACKAGE_DIR/data"

# Step 1: Build Docker images with offline config
echo "[1/5] Building Docker images..."

# Build API
docker build -t terrarisk-api:offline "$PROJECT_DIR/backend"

# Build Frontend with offline tile URL
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://api:8000 \
  --build-arg NEXT_PUBLIC_TILE_URL=http://localhost:8080 \
  -t terrarisk-frontend:offline \
  "$PROJECT_DIR/frontend"

# Pull nginx for tile server
docker pull nginx:alpine

echo "[OK] All images ready"

# Step 2: Export images as tar
echo "[2/5] Exporting Docker images..."
docker save terrarisk-api:offline -o "$PACKAGE_DIR/images/terrarisk-api.tar"
docker save terrarisk-frontend:offline -o "$PACKAGE_DIR/images/terrarisk-frontend.tar"
docker save nginx:alpine -o "$PACKAGE_DIR/images/nginx-alpine.tar"
echo "[OK] Images exported"

# Step 3: Download tiles (if not already done)
echo "[3/5] Downloading map tiles for Sao Paulo..."
if [ -d "$SCRIPT_DIR/tiles/light_nolabels" ]; then
    echo "  Tiles already downloaded, copying..."
else
    cd "$SCRIPT_DIR"
    python3 download-tiles.py
fi
cp -r "$SCRIPT_DIR/tiles" "$PACKAGE_DIR/tiles"
echo "[OK] Tiles ready"

# Step 4: Copy config files and data
echo "[4/5] Copying configuration and data..."
cp "$SCRIPT_DIR/docker-compose.offline.yml" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/tiles-nginx.conf" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/install.bat" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/install.sh" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/stop.bat" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/stop.sh" "$PACKAGE_DIR/"
cp "$SCRIPT_DIR/README-WORKSHOP.md" "$PACKAGE_DIR/"

# Copy backend data (municipalities, maps, etc.)
cp -r "$PROJECT_DIR/backend/data/"* "$PACKAGE_DIR/data/" 2>/dev/null || true

# Fresh database for workshop (no previous groups)
rm -f "$PACKAGE_DIR/data/groups.db"

echo "[OK] Files copied"

# Step 5: Create ZIP
echo "[5/5] Creating ZIP package..."
cd "$SCRIPT_DIR"
tar -czf terrarisk-offline.tar.gz -C "$SCRIPT_DIR" terrarisk-offline/

PACKAGE_SIZE=$(du -sh "$PACKAGE_DIR" | cut -f1)
ZIP_SIZE=$(du -sh "$SCRIPT_DIR/terrarisk-offline.tar.gz" | cut -f1)

echo ""
echo "=== Package Ready! ==="
echo "Directory: $PACKAGE_DIR ($PACKAGE_SIZE)"
echo "Archive:   $SCRIPT_DIR/terrarisk-offline.tar.gz ($ZIP_SIZE)"
echo ""
echo "Next steps:"
echo "1. Upload terrarisk-offline.tar.gz to Google Drive or similar"
echo "2. Adrian downloads on each computer"
echo "3. Extract and run install.bat (Windows) or install.sh (Mac/Linux)"

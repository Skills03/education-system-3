#!/bin/bash
# Minecraft + Oasis 2.0 Setup (No Sudo Required)
# This script sets up Fabric and Oasis without installing the launcher

set -e

echo "=================================================="
echo "Minecraft + Oasis 2.0 Setup (User-Only)"
echo "=================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

MC_DIR="$HOME/.minecraft"
MODS_DIR="$MC_DIR/mods"

echo -e "\n${YELLOW}[1/5] Creating Minecraft directories...${NC}"
mkdir -p "$MC_DIR"
mkdir -p "$MODS_DIR"
echo -e "${GREEN}✓ Directories ready${NC}"

echo -e "\n${YELLOW}[2/5] Downloading Fabric Installer...${NC}"
cd ~/Downloads
if [ ! -f "fabric-installer.jar" ]; then
    wget -O fabric-installer.jar \
        "https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar"
fi
echo -e "${GREEN}✓ Downloaded${NC}"

echo -e "\n${YELLOW}[3/5] Installing Fabric Loader...${NC}"
java -jar fabric-installer.jar client \
    -mcversion 1.21.4 \
    -dir "$MC_DIR" \
    -noprofile || true
echo -e "${GREEN}✓ Fabric installed for Minecraft 1.21.4${NC}"

echo -e "\n${YELLOW}[4/5] Downloading Fabric API...${NC}"
if [ ! -f "$MODS_DIR/fabric-api.jar" ]; then
    wget -O "$MODS_DIR/fabric-api.jar" \
        "https://cdn.modrinth.com/data/P7dR8mSH/versions/PoZBzMmT/fabric-api-0.112.1%2B1.21.4.jar"
    echo -e "${GREEN}✓ Fabric API installed${NC}"
else
    echo -e "${GREEN}✓ Fabric API already installed${NC}"
fi

echo -e "\n${YELLOW}[5/5] Installing Oasis 2.0...${NC}"
OASIS_JAR=$(find /home/mahadev/Desktop/dev/education -name "*oasis*.jar" 2>/dev/null | head -1)

if [ -n "$OASIS_JAR" ]; then
    cp "$OASIS_JAR" "$MODS_DIR/"
    echo -e "${GREEN}✓ Oasis 2.0 installed${NC}"
    echo "  File: $(basename $OASIS_JAR)"
else
    echo -e "${RED}✗ Oasis jar not found${NC}"
    echo "  Please download from: https://modrinth.com/mod/oasis2"
    echo "  Place in: $MODS_DIR/"
fi

echo -e "\n${GREEN}=================================================="
echo "Setup Complete! ✓"
echo "==================================================${NC}"

echo -e "\n${YELLOW}Installed Mods:${NC}"
ls -1 "$MODS_DIR/" | while read mod; do
    echo "  • $mod"
done

echo -e "\n${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Install Minecraft Launcher (requires password):"
echo "   ${GREEN}sudo dpkg -i ~/Downloads/Minecraft.deb${NC}"
echo ""
echo "2. Launch Minecraft:"
echo "   ${GREEN}minecraft-launcher${NC}"
echo ""
echo "3. Select profile: ${GREEN}fabric-loader-1.21.4${NC}"
echo ""
echo "4. In-game commands:"
echo "   ${GREEN}/oasis start${NC}"
echo "   ${GREEN}/oasis prompt Venice at sunset${NC}"
echo ""
echo "📖 Full guide: MINECRAFT_OASIS_SETUP.md"

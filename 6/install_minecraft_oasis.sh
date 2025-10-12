#!/bin/bash
# Minecraft + Oasis 2.0 Installation Script
# Automated setup for Ubuntu/Debian

set -e

echo "=================================================="
echo "Minecraft + Oasis 2.0 Installer"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Minecraft directories
MC_DIR="$HOME/.minecraft"
MODS_DIR="$MC_DIR/mods"
VERSIONS_DIR="$MC_DIR/versions"

echo -e "\n${YELLOW}Step 1: Checking Java...${NC}"
if ! command -v java &> /dev/null; then
    echo -e "${RED}Java not found. Installing OpenJDK 21...${NC}"
    sudo apt update
    sudo apt install -y openjdk-21-jre
else
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo -e "${GREEN}✓ Java found: $JAVA_VERSION${NC}"
fi

echo -e "\n${YELLOW}Step 2: Installing Minecraft Launcher...${NC}"
if [ ! -f "$HOME/Downloads/Minecraft.deb" ]; then
    echo "Downloading Minecraft launcher..."
    wget -O "$HOME/Downloads/Minecraft.deb" \
        "https://launcher.mojang.com/download/Minecraft.deb"

    echo "Installing launcher..."
    sudo dpkg -i "$HOME/Downloads/Minecraft.deb" || \
    sudo apt-get install -f -y

    echo -e "${GREEN}✓ Minecraft launcher installed${NC}"
else
    echo -e "${GREEN}✓ Minecraft installer already downloaded${NC}"
fi

echo -e "\n${YELLOW}Step 3: Setting up Minecraft directories...${NC}"
mkdir -p "$MC_DIR"
mkdir -p "$MODS_DIR"
mkdir -p "$VERSIONS_DIR"
echo -e "${GREEN}✓ Directories created${NC}"

echo -e "\n${YELLOW}Step 4: Downloading Fabric Loader...${NC}"
FABRIC_VERSION="1.21.4"  # Compatible with Oasis 2.0
FABRIC_INSTALLER="fabric-installer-1.0.1.jar"

if [ ! -f "$HOME/Downloads/$FABRIC_INSTALLER" ]; then
    wget -O "$HOME/Downloads/$FABRIC_INSTALLER" \
        "https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar"
fi

echo "Installing Fabric loader..."
java -jar "$HOME/Downloads/$FABRIC_INSTALLER" client \
    -mcversion "$FABRIC_VERSION" \
    -dir "$MC_DIR" \
    -noprofile

echo -e "${GREEN}✓ Fabric loader installed for Minecraft $FABRIC_VERSION${NC}"

echo -e "\n${YELLOW}Step 5: Installing Fabric API...${NC}"
FABRIC_API_URL="https://cdn.modrinth.com/data/P7dR8mSH/versions/PoZBzMmT/fabric-api-0.112.1%2B1.21.4.jar"
FABRIC_API_FILE="fabric-api-0.112.1+1.21.4.jar"

if [ ! -f "$MODS_DIR/$FABRIC_API_FILE" ]; then
    wget -O "$MODS_DIR/$FABRIC_API_FILE" "$FABRIC_API_URL"
    echo -e "${GREEN}✓ Fabric API installed${NC}"
else
    echo -e "${GREEN}✓ Fabric API already installed${NC}"
fi

echo -e "\n${YELLOW}Step 6: Installing Oasis 2.0 mod...${NC}"
# Find Oasis jar
OASIS_JAR=$(find /home/mahadev/Desktop/dev/education -name "*oasis*.jar" 2>/dev/null | head -1)

if [ -n "$OASIS_JAR" ]; then
    cp "$OASIS_JAR" "$MODS_DIR/"
    echo -e "${GREEN}✓ Oasis 2.0 copied to mods folder${NC}"
    echo "  From: $OASIS_JAR"
    echo "  To: $MODS_DIR/$(basename $OASIS_JAR)"
else
    echo -e "${RED}✗ Oasis jar not found${NC}"
    echo "Please download from: https://modrinth.com/mod/oasis2"
    echo "Place it in: $MODS_DIR/"
fi

echo -e "\n${GREEN}=================================================="
echo "Installation Complete!"
echo "==================================================${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Launch Minecraft:"
echo "   minecraft-launcher"
echo ""
echo "2. In the launcher, select the Fabric profile:"
echo "   'fabric-loader-$FABRIC_VERSION'"
echo ""
echo "3. Click 'Play' to start Minecraft"
echo ""
echo "4. Once in-game, use these commands:"
echo "   /oasis start"
echo "   /oasis prompt <your world style>"
echo ""
echo "${YELLOW}Example prompts:${NC}"
echo "   /oasis prompt Venice in the summer"
echo "   /oasis prompt Candy land with chocolate rivers"
echo "   /oasis prompt Cyberpunk city at night"
echo "   /oasis prompt Medieval castle"
echo ""
echo "${YELLOW}Controls:${NC}"
echo "   Hold R    - Temporarily hide effect"
echo "   Press V   - Toggle effect"
echo "   [ and ]   - Cycle through preset prompts"
echo "   /oasis stop - Stop transformation"
echo ""
echo "Enjoy Oasis 2.0! 🌍✨"

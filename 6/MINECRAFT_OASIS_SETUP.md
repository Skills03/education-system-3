# Minecraft + Oasis 2.0 Setup Guide

**Quick Install Instructions for Ubuntu**

---

## Prerequisites

✅ **Java 21** - Already installed!
```bash
java -version  # OpenJDK 21.0.8
```

---

## Installation Steps

### Step 1: Install Minecraft Launcher

```bash
# Download (already done)
cd ~/Downloads

# Install (requires sudo password)
sudo dpkg -i Minecraft.deb
sudo apt-get install -f -y  # Fix dependencies if needed
```

**Alternative:** Download from [minecraft.net/download](https://www.minecraft.net/download)

---

### Step 2: Run Automated Setup (Without Sudo)

```bash
cd /home/mahadev/Desktop/dev/education/6

# Run the setup script
./install_minecraft_oasis_nosudo.sh
```

---

### Step 3: Launch Minecraft

```bash
# Start the launcher
minecraft-launcher
```

**In the launcher:**
1. Sign in with your Microsoft account
2. Select profile: **`fabric-loader-1.21.4`**
3. Click **PLAY**

---

### Step 4: Use Oasis 2.0 in Game

**Start transformation:**
```
/oasis start
```

**Change world style:**
```
/oasis prompt <your description>
```

**Examples:**
```
/oasis prompt Venice in the summer with gondolas
/oasis prompt Cyberpunk city with neon lights
/oasis prompt Medieval castle surrounded by forest
/oasis prompt Candy land with chocolate rivers
/oasis prompt Wild West desert town
/oasis prompt Anime style cherry blossom garden
```

**Controls:**
- **Hold R** - Temporarily hide effect (see normal Minecraft)
- **Press V** - Toggle effect on/off
- **[ and ]** - Cycle through preset prompts
- **Stop:** `/oasis stop`

---

## Manual Setup (If Script Fails)

### 1. Download Fabric Installer
```bash
wget https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar \
  -O ~/Downloads/fabric-installer.jar
```

### 2. Install Fabric
```bash
java -jar ~/Downloads/fabric-installer.jar client \
  -mcversion 1.21.4 \
  -dir ~/.minecraft
```

### 3. Create Mods Folder
```bash
mkdir -p ~/.minecraft/mods
```

### 4. Download Fabric API
```bash
wget -O ~/.minecraft/mods/fabric-api.jar \
  "https://cdn.modrinth.com/data/P7dR8mSH/versions/PoZBzMmT/fabric-api-0.112.1%2B1.21.4.jar"
```

### 5. Copy Oasis Mod
```bash
# Find your Oasis jar
find ~/Desktop -name "*oasis*.jar"

# Copy to mods folder
cp /path/to/decart-oasis-*.jar ~/.minecraft/mods/
```

---

## Troubleshooting

### Issue: "Minecraft not installed"
**Solution:** Install launcher with:
```bash
sudo dpkg -i ~/Downloads/Minecraft.deb
```

### Issue: "Fabric profile not showing"
**Solution:**
1. Close Minecraft launcher
2. Re-run Fabric installer
3. Restart launcher

### Issue: "Oasis mod not working"
**Check:**
```bash
ls ~/.minecraft/mods/
# Should see: fabric-api.jar and decart-oasis-*.jar
```

### Issue: "Low FPS with Oasis"
**Expected:** Oasis is GPU-intensive
- Press R to temporarily disable
- Lower Minecraft graphics settings
- Use `/oasis stop` when not needed

---

## Installed Locations

| Component | Path |
|-----------|------|
| Minecraft | `~/.minecraft/` |
| Mods | `~/.minecraft/mods/` |
| Fabric Profile | `~/.minecraft/versions/fabric-loader-1.21.4/` |
| Launcher | `/usr/bin/minecraft-launcher` |

---

## Quick Commands Reference

```bash
# In Minecraft chat:
/oasis start                          # Begin transformation
/oasis prompt <description>           # Change world style
/oasis stop                          # End transformation

# Keyboard shortcuts:
R (hold)    # Temporarily show normal Minecraft
V           # Toggle Oasis on/off
[ or ]      # Cycle preset prompts
```

---

## What Oasis Does

Oasis 2.0 uses **MirageLSD** (real-time video-to-video AI) to transform Minecraft visuals:

- Changes entire world appearance based on text prompts
- Runs in real-time as you play
- No map editing or texture packs needed
- Infinite possibilities

**Behind the scenes:**
- Your Minecraft video → Decart servers
- AI transformation → Real-time streaming back
- ~30 FPS (may drop with complex scenes)

---

## Next Steps

After installation:

1. **Test basic Minecraft** (without Oasis first)
2. **Try Oasis with simple prompt** (e.g., "Venice")
3. **Experiment with creative prompts**
4. **Share screenshots!**

Enjoy exploring infinite worlds! 🌍✨

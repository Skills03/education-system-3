# Modrinth vs CurseForge: API Comparison for Programmatic Control

**Date:** October 12, 2025
**Comparison Focus:** Developer Flexibility & Programmatic Control

---

## Executive Summary

**Winner: 🏆 MODRINTH**

Modrinth provides superior programmatic flexibility with:
- Open, well-documented API (no approval required)
- Better rate limits (300 req/min vs undisclosed)
- Multiple Python SDKs available
- OAuth2 + PAT authentication
- Open-source ecosystem
- No mandatory commercial licensing

---

## Detailed Comparison

| Feature | Modrinth | CurseForge |
|---------|----------|------------|
| **API Access** | ✅ Immediate, no approval | ❌ Application + approval required |
| **Authentication** | ✅ PAT or OAuth2 | ⚠️ API key only (x-api-key header) |
| **Rate Limits** | ✅ **300 requests/min** (documented) | ❌ Undisclosed, lower limits reported |
| **Documentation** | ✅ Excellent (docs.modrinth.com) | ⚠️ Good but restrictive |
| **Python SDKs** | ✅ Multiple (modrinth, modrinth.py) | ❌ No official SDK |
| **API Reliability** | ✅ Stable | ❌ Frequent outages reported |
| **Commercial Use** | ✅ Free, open terms | ⚠️ May require licensing agreement |
| **Open Source** | ✅ Open API spec | ❌ Proprietary |

---

## Authentication Comparison

### Modrinth (More Flexible)

**Option 1: Personal Access Token (PAT)**
```python
import requests

headers = {
    'Authorization': 'mrp_YOUR_TOKEN_HERE',
    'User-Agent': 'MyApp/1.0'  # Required
}

response = requests.get(
    'https://api.modrinth.com/v2/project/oasis2',
    headers=headers
)
```

**Option 2: OAuth2** (for user delegation)
```python
# OAuth flow
auth_url = 'https://api.modrinth.com/_internal/oauth/token'
# Full OAuth implementation for user auth
```

### CurseForge (Restrictive)

**API Key Only** (requires approval first)
```python
import requests

headers = {
    'x-api-key': 'YOUR_API_KEY_HERE'
}

response = requests.get(
    'https://api.curseforge.com/v1/mods/search',
    headers=headers,
    params={'gameId': 432, 'searchFilter': 'oasis'}
)
```

---

## Python SDK Examples

### Modrinth (Easy Integration)

**Install:**
```bash
pip install modrinth
```

**Usage:**
```python
import modrinth

# Search for mods
projects = modrinth.Projects.Search('oasis')
for hit in projects.hits:
    print(f"Found: {hit.name} - {hit.description}")

# Get specific project
project = modrinth.Projects.ModrinthProject('oasis2')
versions = project.getVersions()

# Download latest version
latest = versions[0]
primary_file = latest.getPrimaryFile()
download_url = latest.getDownload(primary_file)
print(f"Download: {download_url}")

# Authentication (for write operations)
authed_user = modrinth.Users.AuthenticatedUser('mrp_YOUR_TOKEN')
project.follow(authed_user)
```

### CurseForge (Manual Implementation)

**No Official SDK - Manual REST calls:**
```python
import requests

API_KEY = 'YOUR_CF_API_KEY'
BASE_URL = 'https://api.curseforge.com/v1'

def search_mods(query):
    response = requests.get(
        f'{BASE_URL}/mods/search',
        headers={'x-api-key': API_KEY},
        params={
            'gameId': 432,  # Minecraft
            'searchFilter': query
        }
    )
    return response.json()

def get_mod_files(mod_id):
    response = requests.get(
        f'{BASE_URL}/mods/{mod_id}/files',
        headers={'x-api-key': API_KEY}
    )
    return response.json()

# Usage
mods = search_mods('oasis')
for mod in mods['data']:
    print(f"Found: {mod['name']}")
    files = get_mod_files(mod['id'])
    latest = files['data'][0]
    print(f"Download: {latest['downloadUrl']}")
```

---

## Rate Limits & Reliability

### Modrinth
- **Limit:** 300 requests/minute (clearly documented)
- **Enforcement:** 429 status code when exceeded
- **Reset:** Every minute
- **Reliability:** ✅ Stable, minimal outages
- **Monitoring:** Clear error messages

### CurseForge
- **Limit:** ❌ Undisclosed (varies by usage)
- **Enforcement:** 403 Forbidden when exceeded
- **Issues Reported:**
  - "Concurrent outages"
  - Mods disappear from API during high load
  - Inconsistent rate limit resets
  - Commercial quotas may trigger licensing requirements

---

## API Feature Comparison

### Modrinth API Capabilities

**Search & Discovery:**
- ✅ Full-text search
- ✅ Faceted filtering (game version, mod loader, categories)
- ✅ Pagination support
- ✅ Sorting options

**Project Management:**
- ✅ Create/update projects via API
- ✅ Version management
- ✅ File uploads (automated CI/CD)
- ✅ Dependency management
- ✅ Gallery/image uploads

**User Operations:**
- ✅ Follow/unfollow projects
- ✅ User profiles
- ✅ OAuth user delegation

**Analytics:**
- ✅ Download counts
- ✅ View statistics

### CurseForge API Capabilities

**Search & Discovery:**
- ✅ Mod search
- ⚠️ Limited filtering options
- ✅ Category browsing

**Project Management:**
- ✅ Upload API (separate, requires approval)
- ⚠️ Less flexible than Modrinth
- ⚠️ License management per-project (manual)

**Restrictions:**
- ❌ Commercial use may require licensing
- ❌ API key non-transferable
- ❌ Quota limits undisclosed
- ❌ Third-party sharing prohibited

---

## Integration Examples

### Example 1: Auto-Download Latest Mod Version

**Modrinth:**
```python
import modrinth
import requests

def download_latest_oasis():
    # Get project
    project = modrinth.Projects.ModrinthProject('oasis2')

    # Get latest version
    versions = project.getVersions()
    latest = versions[0]

    # Get download URL
    primary_file = latest.getPrimaryFile()
    url = latest.getDownload(primary_file)

    # Download
    response = requests.get(url)
    with open(f'oasis-{latest.version_number}.jar', 'wb') as f:
        f.write(response.content)

    print(f"Downloaded Oasis {latest.version_number}")

download_latest_oasis()
```

**CurseForge:**
```python
import requests

API_KEY = 'YOUR_API_KEY'

def download_latest_oasis():
    # Search for Oasis
    search = requests.get(
        'https://api.curseforge.com/v1/mods/search',
        headers={'x-api-key': API_KEY},
        params={'gameId': 432, 'searchFilter': 'oasis 2'}
    ).json()

    mod_id = search['data'][0]['id']

    # Get files
    files = requests.get(
        f'https://api.curseforge.com/v1/mods/{mod_id}/files',
        headers={'x-api-key': API_KEY}
    ).json()

    latest = files['data'][0]

    # Download
    response = requests.get(latest['downloadUrl'])
    with open(latest['fileName'], 'wb') as f:
        f.write(response.content)

    print(f"Downloaded {latest['fileName']}")

download_latest_oasis()
```

---

## Example 2: Monitor New Versions

**Modrinth (Webhook Support):**
```python
import modrinth
import time

def monitor_updates():
    project = modrinth.Projects.ModrinthProject('oasis2')
    last_version = None

    while True:
        versions = project.getVersions()
        current = versions[0]

        if last_version and current.id != last_version.id:
            print(f"🆕 New version: {current.version_number}")
            print(f"Changelog: {current.changelog}")
            # Trigger your automation here

        last_version = current
        time.sleep(300)  # Check every 5 minutes

monitor_updates()
```

---

## Example 3: Automated Mod Pack Creator

**Modrinth (Full Automation):**
```python
import modrinth
import json

def create_modpack(mod_slugs, output_file):
    modpack = {
        'formatVersion': 1,
        'game': 'minecraft',
        'versionId': '1.21.4',
        'name': 'My Auto Pack',
        'files': []
    }

    for slug in mod_slugs:
        project = modrinth.Projects.ModrinthProject(slug)
        versions = project.getVersions()

        # Filter for correct game version
        compatible = [v for v in versions
                     if '1.21.4' in v.game_versions]

        if compatible:
            latest = compatible[0]
            file = latest.getPrimaryFile()

            modpack['files'].append({
                'path': f'mods/{file.filename}',
                'downloads': [latest.getDownload(file)],
                'hashes': {'sha512': file.hashes.sha512}
            })

    with open(output_file, 'w') as f:
        json.dump(modpack, f, indent=2)

    print(f"Created modpack with {len(modpack['files'])} mods")

# Auto-create pack
create_modpack(['oasis2', 'fabric-api', 'sodium'], 'modpack.mrpack')
```

---

## Recommendation for Your Education Project

### ✅ Use Modrinth for Oasis 2.0 Integration

**Reasons:**

1. **Immediate Access** - No approval wait time
2. **Better Documentation** - Easy to integrate
3. **Python SDK** - Ready-to-use libraries
4. **Rate Limits** - 300/min is generous
5. **Open Source** - Transparent, community-driven
6. **Reliability** - Fewer outages than CurseForge

### Implementation Steps:

```bash
# 1. Install SDK
pip install modrinth requests

# 2. Get Oasis 2.0
python3 << 'EOF'
import modrinth
import requests

# Download Oasis 2.0
project = modrinth.Projects.ModrinthProject('oasis2')
versions = project.getVersions()
latest = versions[0]
primary_file = latest.getPrimaryFile()
url = latest.getDownload(primary_file)

response = requests.get(url)
with open('oasis-2.0.jar', 'wb') as f:
    f.write(response.content)

print(f"✅ Downloaded Oasis {latest.version_number}")
EOF
```

---

## Alternative: Decart Platform API

For **direct Oasis model control** (not the Minecraft mod), consider:

**Decart Platform API** (platform.decart.ai)
- Real-time AI video/world generation
- Direct model access
- Different from mod distribution

**Open Oasis** (github.com/etched-ai/open-oasis)
- 500M parameter model
- Inference code included
- Run locally

---

## Conclusion

**For Programmatic Flexibility: MODRINTH WINS**

| Criterion | Modrinth | CurseForge |
|-----------|----------|------------|
| Ease of Setup | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| API Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Documentation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Rate Limits | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| SDK Support | ⭐⭐⭐⭐⭐ | ⭐ |
| Reliability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Open Source | ⭐⭐⭐⭐⭐ | ⭐ |

**Modrinth Overall: 5/5**
**CurseForge Overall: 2.5/5**

Use **Modrinth** unless you specifically need CurseForge exclusives.

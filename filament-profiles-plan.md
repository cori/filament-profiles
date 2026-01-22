# FilamentProfiles: Print Settings Management for Spoolman

## Overview

FilamentProfiles is a companion service to Spoolman that adds print profile management — the missing layer between filament inventory and slicer configuration. It tracks the actual print settings (temperatures, pressure advance, flow rates, speeds) that make filaments print well, with support for per-machine and per-plate variants.

## Problem Statement

Current tools handle inventory (Spoolman) or color data (3dfilamentprofiles.com), but neither tracks **print profiles** — the tuned settings that determine print quality. This knowledge lives in:
- Slicer config files (not portable across slicers or machines)
- Chat logs with Claude/Gemini
- The user's head

Information is lost across prints, plates, profiles, and conversations. There's no single source of truth for "what settings work for this filament on this machine with this plate?"

## Goals

1. **Track print profiles** with proper structure (not ad-hoc extra fields)
2. **Support variants** by machine and plate type
3. **Pull community defaults** from SpoolmanDB as starting points
4. **Export to slicer formats** — specifically QIDI Studio (OrcaSlicer JSON format)
5. **Integrate with Spoolman** for filament/spool inventory (don't duplicate that)
6. **Single-user, self-hosted** — runs alongside Spoolman, no auth needed initially

## Non-Goals (for v1)

- Print history / learnings tracking (future consideration)
- Multi-user / authentication
- Bidirectional slicer sync (import from slicer)
- Support for PrusaSlicer INI format (can add later)

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   SpoolmanDB    │────▶│   FilamentProfiles   │────▶│  QIDI Studio    │
│ (community data)│     │    (this project)    │     │  (JSON export)  │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
                               │      ▲
                               │      │
                               ▼      │
                        ┌─────────────────┐
                        │    Spoolman     │
                        │  (inventory)    │
                        └─────────────────┘
```

### Components

1. **PostgreSQL database** — stores profiles, machines, plates, links to Spoolman
2. **Python/FastAPI backend** — REST API, SpoolmanDB sync, slicer export
3. **Web UI** — profile management, export interface
4. **CLI** (optional) — for scripted exports

---

## Data Model

### Entities

#### Machine
Represents a specific printer.
```
id: int (PK)
name: str                    # e.g., "Voron 2.4", "QIDI Plus4"
slug: str                    # e.g., "voron-2.4", "qidi-plus4"
description: str?
nozzle_diameter: float       # e.g., 0.4
created_at: datetime
updated_at: datetime
```

#### Plate
Represents a build plate type.
```
id: int (PK)
name: str                    # e.g., "Textured PEI", "Smooth PEI", "G10"
slug: str
description: str?
created_at: datetime
updated_at: datetime
```

#### Filament
Reference to a Spoolman filament. We cache some fields for convenience but Spoolman is source of truth for inventory.
```
id: int (PK)
spoolman_filament_id: int?   # Link to Spoolman (nullable for standalone use)
vendor: str                  # e.g., "Bambu Lab"
material: str                # e.g., "PLA"
name: str                    # e.g., "Matte"
color_name: str?             # e.g., "Bone White"
color_hex: str?              # e.g., "E8E0D5"
density: float?              # g/cm³
diameter: float              # 1.75 or 2.85
created_at: datetime
updated_at: datetime
```

#### Profile
The core entity — print settings for a filament + machine + plate combination.
```
id: int (PK)
filament_id: int (FK)
machine_id: int (FK)
plate_id: int (FK)

# Temperature settings
nozzle_temp: int             # e.g., 200
nozzle_temp_first_layer: int? # e.g., 205 (if different)
bed_temp: int                # e.g., 35
bed_temp_first_layer: int?   # e.g., 40 (if different)
chamber_temp: int?           # for enclosed printers

# Flow and extrusion
flow_ratio: float            # e.g., 0.95
pressure_advance: float?     # e.g., 0.04 (Klipper PA / linear advance)
max_volumetric_speed: float? # mm³/s

# Retraction
retraction_length: float?    # mm
retraction_speed: float?     # mm/s

# Speeds (optional overrides - slicer has defaults)
print_speed: float?          # mm/s
first_layer_speed: float?
outer_wall_speed: float?
inner_wall_speed: float?
infill_speed: float?
travel_speed: float?

# Cooling
fan_min_speed: int?          # 0-100%
fan_max_speed: int?
disable_fan_first_layers: int?

# Metadata
is_default: bool             # Is this the preferred profile for this filament+machine?
notes: str?                  # Free-form notes
source: str?                 # "manual", "spoolmandb", "imported"
source_profile: str?         # Original profile name if imported

created_at: datetime
updated_at: datetime
```

#### Unique constraint
`(filament_id, machine_id, plate_id)` should be unique — one profile per combination.

---

## SpoolmanDB Integration

SpoolmanDB is a GitHub-hosted JSON file with community filament data:
- URL: https://donkie.github.io/SpoolmanDB/filaments.json
- Contains: manufacturers, filaments, colors, basic temps (settings_extruder_temp, settings_bed_temp)
- No print profiles (PA, flow, speeds) — just starting points

### Sync Strategy

1. **On-demand fetch** — when user creates a new filament, offer to pull SpoolmanDB defaults
2. **Cache locally** — store fetched SpoolmanDB data to reduce requests
3. **No hosting required** — we consume the public JSON, don't need to host it

### Default Profile Creation

When creating a profile from SpoolmanDB defaults:
```python
profile = Profile(
    nozzle_temp=spoolmandb_filament.settings_extruder_temp or 200,
    bed_temp=spoolmandb_filament.settings_bed_temp or 60,
    flow_ratio=1.0,  # User will tune
    pressure_advance=None,  # User must calibrate
    source="spoolmandb",
    source_profile=spoolmandb_filament.name
)
```

---

## Spoolman Integration

### Connection

- FilamentProfiles connects to Spoolman via REST API
- Spoolman URL configured via environment variable
- Optional — FilamentProfiles can work standalone without Spoolman

### Data Flow

1. **Read-only from Spoolman** — we don't write to Spoolman
2. **Filament linking** — when creating a Filament in FilamentProfiles, user can link to a Spoolman filament ID
3. **Inventory display** — UI can show current spool inventory from Spoolman alongside profiles

### API Calls

- `GET /api/v1/filament` — list Spoolman filaments for linking
- `GET /api/v1/filament/{id}` — get filament details
- `GET /api/v1/spool` — list spools (for inventory view)

---

## Slicer Export

### Target Format

QIDI Studio uses OrcaSlicer's JSON format for filament profiles.

Location: `~/.config/QIDIStudio/user/default/filament/` (Linux)
         `%AppData%\QIDIStudio\user\default\filament\` (Windows)

### JSON Structure

```json
{
    "type": "filament",
    "name": "Bambu Lab PLA Matte @QIDI Plus4",
    "inherits": "Generic PLA",
    "from": "User",
    "filament_id": "user_bambu_lab_pla_matte",
    "filament_vendor": "Bambu Lab",
    "filament_type": "PLA",
    "filament_colour": "#E8E0D5",
    "filament_density": "1.24",
    "filament_diameter": "1.75",
    "nozzle_temperature": ["200"],
    "nozzle_temperature_initial_layer": ["205"],
    "bed_temperature": ["35"],
    "bed_temperature_initial_layer": ["40"],
    "filament_flow_ratio": ["0.95"],
    "pressure_advance": ["0.04"],
    "filament_max_volumetric_speed": ["15"],
    "fan_min_speed": ["35"],
    "fan_max_speed": ["100"],
    "close_fan_the_first_x_layers": ["1"],
    "filament_retraction_length": ["0.8"],
    "filament_retraction_speed": ["30"],
    "compatible_printers": ["QIDI Plus4 0.4 nozzle"],
    "version": "1.9.0.0"
}
```

### Export Options

1. **Single profile** — export one profile as JSON file
2. **Batch export** — export all profiles for a machine
3. **Direct install** — write to slicer config directory (with path config)

### Naming Convention

Profile names follow: `{Vendor} {Material} {Name} @{Machine} {Plate}`
Example: `Bambu Lab PLA Matte @QIDI Plus4 Textured PEI`

---

## API Design

### Endpoints

#### Machines
```
GET    /api/machines              # List all machines
POST   /api/machines              # Create machine
GET    /api/machines/{id}         # Get machine
PUT    /api/machines/{id}         # Update machine
DELETE /api/machines/{id}         # Delete machine
```

#### Plates
```
GET    /api/plates                # List all plates
POST   /api/plates                # Create plate
GET    /api/plates/{id}           # Get plate
PUT    /api/plates/{id}           # Update plate
DELETE /api/plates/{id}           # Delete plate
```

#### Filaments
```
GET    /api/filaments             # List all filaments
POST   /api/filaments             # Create filament
GET    /api/filaments/{id}        # Get filament
PUT    /api/filaments/{id}        # Update filament
DELETE /api/filaments/{id}        # Delete filament
GET    /api/filaments/search      # Search SpoolmanDB for filament defaults
```

#### Profiles
```
GET    /api/profiles              # List profiles (filterable by filament, machine, plate)
POST   /api/profiles              # Create profile
GET    /api/profiles/{id}         # Get profile
PUT    /api/profiles/{id}         # Update profile
DELETE /api/profiles/{id}         # Delete profile
POST   /api/profiles/{id}/clone   # Clone profile (for new machine/plate variant)
```

#### Export
```
GET    /api/export/profile/{id}                    # Export single profile as JSON
GET    /api/export/machine/{id}                    # Export all profiles for a machine
POST   /api/export/install                         # Install profiles to slicer directory
        Body: { profile_ids: [...], target_path: "..." }
```

#### Spoolman Integration
```
GET    /api/spoolman/filaments    # Proxy to Spoolman filaments
GET    /api/spoolman/spools       # Proxy to Spoolman spools
GET    /api/spoolman/status       # Check Spoolman connection
```

#### SpoolmanDB
```
GET    /api/spoolmandb/search     # Search SpoolmanDB for filament data
        Query: ?vendor=bambu&material=pla&name=matte
GET    /api/spoolmandb/sync       # Refresh local SpoolmanDB cache
```

---

## Web UI

### Pages

1. **Dashboard** — overview of filaments, profiles, quick stats
2. **Filaments** — list/create/edit filaments, link to Spoolman
3. **Profiles** — list/create/edit profiles, filter by filament/machine/plate
4. **Machines** — manage printers
5. **Plates** — manage build plate types
6. **Export** — batch export interface, slicer path configuration
7. **Settings** — Spoolman URL, slicer paths, SpoolmanDB sync

### Tech Stack

- React or Vue (TBD — match Spoolman for consistency?)
- Tailwind CSS
- Vite for build

---

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  filamentprofiles:
    image: ghcr.io/USER/filamentprofiles:latest
    restart: unless-stopped
    ports:
      - "7920:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/filamentprofiles
      - SPOOLMAN_URL=http://spoolman:8000
      - TZ=America/Chicago
    volumes:
      - ./data:/app/data
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_USER=filamentprofiles
      - POSTGRES_PASSWORD=changeme
      - POSTGRES_DB=filamentprofiles
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Runtipi App Config

Create runtipi app configuration for both Spoolman and FilamentProfiles as part of this project.

### Environment Variables

```
DATABASE_URL          # PostgreSQL connection string
SPOOLMAN_URL          # Spoolman instance URL (optional)
SLICER_PROFILE_PATH   # Default path for slicer profile export
SPOOLMANDB_CACHE_TTL  # How long to cache SpoolmanDB data (default: 24h)
```

---

## Implementation Plan

### Phase 1: Core Backend
1. Set up FastAPI project structure
2. Database models with SQLAlchemy
3. Alembic migrations
4. Core CRUD endpoints for machines, plates, filaments, profiles
5. Basic profile export to OrcaSlicer JSON

### Phase 2: SpoolmanDB Integration
1. SpoolmanDB fetcher/parser
2. Local caching
3. Search endpoint
4. "Create from SpoolmanDB" flow

### Phase 3: Spoolman Integration
1. Spoolman API client
2. Filament linking
3. Inventory display proxy

### Phase 4: Web UI
1. Project setup (React/Vue + Vite)
2. Filament management pages
3. Profile management pages
4. Export interface

### Phase 5: Deployment
1. Dockerfile
2. Docker Compose config
3. Runtipi app configs (Spoolman + FilamentProfiles)
4. Documentation

---

## Open Questions

1. **UI framework** — React (like Spoolman) or Vue? Leaning React for consistency.

2. **Profile inheritance** — Should profiles support inheritance? e.g., "Bambu PLA Matte base" that machine-specific profiles inherit from? Adds complexity but reduces duplication.

3. **Spool-level profiles** — Should profiles be linkable to specific spools (for batch-to-batch variation)? Probably overkill for v1.

4. **Print history** — Deferred, but worth designing the schema to accommodate later.

---

## References

- Spoolman: https://github.com/Donkie/Spoolman
- SpoolmanDB: https://github.com/Donkie/SpoolmanDB
- spoolman2slicer: https://github.com/bofh69/spoolman2slicer
- OrcaSlicer profile format: JSON files in user config directory
- QIDI Studio: OrcaSlicer-based, uses same JSON format

# FilamentProfiles

Print settings management companion for [Spoolman](https://github.com/Donkie/Spoolman).

## Overview

FilamentProfiles tracks the actual print settings (temperatures, pressure advance, flow rates, speeds) that make filaments print well, with support for per-machine and per-plate variants.

## Features

- **Track print profiles** with proper structure (temperatures, PA, flow, speeds, cooling)
- **Support variants** by machine and build plate type
- **Export to slicer formats** — specifically QIDI Studio / OrcaSlicer JSON format
- **Integrate with Spoolman** for filament/spool inventory (optional)
- **Single-user, self-hosted** — runs alongside Spoolman
- **Web UI** for managing machines, plates, filaments, and profiles

## Quick Start

### Using Docker (Recommended)

```bash
# Pull and run with docker-compose
curl -O https://raw.githubusercontent.com/cori/filament-profiles/main/docker-compose.yml
docker-compose up -d
```

The application will be available at http://localhost:7920

### Building Locally

```bash
# Clone the repository
git clone https://github.com/cori/filament-profiles.git
cd filament-profiles

# Build and run with docker-compose
docker-compose -f docker-compose.dev.yml up -d --build
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://filamentprofiles:changeme@localhost:5432/filamentprofiles` |
| `SPOOLMAN_URL` | Spoolman instance URL (optional) | - |
| `TZ` | Timezone | `UTC` |

## API Endpoints

### Machines
- `GET /api/machines` - List all machines
- `POST /api/machines` - Create a machine
- `GET /api/machines/{id}` - Get a machine
- `PUT /api/machines/{id}` - Update a machine
- `DELETE /api/machines/{id}` - Delete a machine

### Plates
- `GET /api/plates` - List all build plates
- `POST /api/plates` - Create a plate
- `GET /api/plates/{id}` - Get a plate
- `PUT /api/plates/{id}` - Update a plate
- `DELETE /api/plates/{id}` - Delete a plate

### Filaments
- `GET /api/filaments` - List all filaments
- `POST /api/filaments` - Create a filament
- `GET /api/filaments/{id}` - Get a filament
- `PUT /api/filaments/{id}` - Update a filament
- `DELETE /api/filaments/{id}` - Delete a filament

### Profiles
- `GET /api/profiles` - List profiles (filterable by filament, machine, plate)
- `POST /api/profiles` - Create a profile
- `GET /api/profiles/{id}` - Get a profile
- `PUT /api/profiles/{id}` - Update a profile
- `DELETE /api/profiles/{id}` - Delete a profile
- `POST /api/profiles/{id}/clone` - Clone to new machine/plate

### Export
- `GET /api/export/profile/{id}` - Export profile as OrcaSlicer JSON
- `GET /api/export/machine/{id}` - Export all profiles for a machine

## Development

### Backend

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Run server (without frontend)
uvicorn filamentprofiles.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server (proxies API to localhost:8000)
npm run dev

# Build for production
npm run build
```

### Full Stack Development

```bash
# Terminal 1: Start database
docker-compose -f docker-compose.dev.yml up db

# Terminal 2: Run backend
DATABASE_URL=postgresql://filamentprofiles:changeme@localhost:5432/filamentprofiles \
  uvicorn filamentprofiles.main:app --reload

# Terminal 3: Run frontend dev server
cd frontend && npm run dev
```

## License

MIT

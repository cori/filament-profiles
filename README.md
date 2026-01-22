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

## Quick Start

```bash
docker-compose up -d
```

The API will be available at http://localhost:7920

## API Endpoints

- `GET/POST /api/machines` - Manage printers
- `GET/POST /api/plates` - Manage build plate types
- `GET/POST /api/filaments` - Manage filaments
- `GET/POST /api/profiles` - Manage print profiles
- `GET /api/export/profile/{id}` - Export profile as OrcaSlicer JSON
- `GET /api/export/machine/{id}` - Export all profiles for a machine

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://filamentprofiles:changeme@localhost:5432/filamentprofiles` |
| `SPOOLMAN_URL` | Spoolman instance URL (optional) | - |

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run server
uvicorn filamentprofiles.main:app --reload
```

## License

MIT

---
name: soundhaven-architecture
description: Master cheatsheet for the SoundHaven project's tech stack, APIs, and core integrations.
---

# SoundHaven Architecture & Development Guidelines

This skill serves as the master cheatsheet for the SoundHaven project (Tidal Media Downloader).

## Tech Stack Overview
- **Frontend**: Vite + React + TypeScript + Tailwind CSS + Zustand + Shadcn UI.
- **Backend**: FastAPI + Python (using local virtual environment `venv`).

## The OrpheusDL Engine
- OrpheusDL is used strictly for downloading lossless audio (FLAC/ALAC) in the background because of its heavy DRM-bypassing operations (which can take 3-10+ seconds).
- Backend initialization requires `TidalTvSession` tokens and syncing with `loginstorage.bin`.

## The "30-Second Preview" Trick
- **Do NOT** use the Tidal API for real-time UI audio previews (it returns DRM/Manifests/Errors).
- **Use** the iTunes Search API (`https://itunes.apple.com/search?term=...`) asynchronously in the frontend (via Zustand store) to fetch instant 30s `.m4a` previews while retaining TIDAL metadata for display.

## Search Results Mapping
- Always parse the `artists` array (not just the singular `artist` object) to properly display multiple collaborators and avoid "Unknown" artist bugs.
- The 'All' tab (Top Results) must use interleaved rendering (Track -> Album -> Playlist -> repeat) to mimic the official TIDAL interface.

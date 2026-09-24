import pathlib

file_path = pathlib.Path('C:/Mek Project/SoundHavenPoject/backend/main.py')
content = file_path.read_text(encoding='utf-8')

missing_artist_code = '''                "id": item.get("id"),
                "title": item.get("title", ""),
                "artist": artist_str,
                "album": item.get("album", {}).get("title", "Unknown Album"),
                "duration": item.get("duration", 0),
                "explicit": item.get("explicit", False),
                "cover_url": f"https://resources.tidal.com/images/{item.get('album', {}).get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("album", {}).get("cover") else None,
            })

        # Format Albums
        albums = []
        seen_album_titles = set()
        for item in albums_raw.get("items", []):
            title = item.get("title", "")
            if title in seen_album_titles:
                continue
            seen_album_titles.add(title)
            albums.append({
                "id": item.get("id"),
                "title": title,
                "artist": artist_info.get("name", "Unknown"),
                "release_date": item.get("releaseDate", "Unknown"),
                "cover_url": f"https://resources.tidal.com/images/{item.get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("cover") else None,
            })

        # Format EPs & Singles
        eps = []
        seen_ep_titles = set()
        for item in eps_raw.get("items", []):
            title = item.get("title", "")
            if title in seen_ep_titles:
                continue
            seen_ep_titles.add(title)
            eps.append({
                "id": item.get("id"),
                "title": title,
                "artist": artist_info.get("name", "Unknown"),
                "release_date": item.get("releaseDate", "Unknown"),
                "cover_url": f"https://resources.tidal.com/images/{item.get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("cover") else None,
            })

        return {
            "artist": {
                "id": artist_info.get("id"),
                "name": artist_info.get("name"),
                "picture_url": f"https://resources.tidal.com/images/{artist_info.get('picture', '').replace('-', '/')}/750x750.jpg" if artist_info.get("picture") else None,
                "popularity": artist_info.get("popularity", 0)
            },
            "top_tracks": tracks,
            "albums": albums,
            "eps_singles": eps'''

content = content.replace('            tracks.append({\n        }', '            tracks.append({\n' + missing_artist_code + '\n        }')

old_download_track = '''@app.get("/api/download/{track_id}")
async def download_track(track_id: int):
    """
    Download a track using OrpheusDL subprocess (for full FLAC pipeline).
    Implements "Stream and Cleanup" â€” sends file to browser, then deletes from server.
    """
    if not tidal_api:
        raise HTTPException(status_code=401, detail="TIDAL not connected.")
    
    # Use subprocess for actual downloading since OrpheusDL's download pipeline
    # involves complex FLAC processing, tagging, etc.
    import subprocess
    
    download_dir = ORPHEUS_DIR / "downloads"
    download_dir.mkdir(exist_ok=True)
    
    track_url = f"https://tidal.com/browse/track/{track_id}"
    
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "orpheus.py", track_url, "-o", str(download_dir)],
            cwd=str(ORPHEUS_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Download timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    
    # Find the downloaded file (newest .flac file in the downloads directory)
    flac_files = sorted(download_dir.rglob("*.flac"), key=os.path.getmtime, reverse=True)
    
    if not flac_files:
        # Try other formats as fallback
        all_audio = sorted(
            [f for f in download_dir.rglob("*") if f.suffix in (".flac", ".m4a", ".mp4", ".ogg")],
            key=os.path.getmtime,
            reverse=True,
        )
        if not all_audio:
            raise HTTPException(status_code=500, detail="Download completed but no audio file found.")
        flac_files = all_audio
    
    file_path = flac_files[0]
    
    # Return the file to the browser
    response = FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="audio/flac",
    )
    
    # Schedule cleanup after response is sent
    # Note: In production, use a background task or middleware for cleanup
    # For now, we leave the file â€” cleanup can be added via a cron or on next download
    
    return response'''

new_download_track = '''@app.get("/api/download/{track_id}")
async def download_track(track_id: int, background_tasks: BackgroundTasks):
    """
    Download a track using OrpheusDL subprocess (for full FLAC pipeline).
    Implements "Stream and Cleanup" — sends file to browser, then deletes from server.
    """
    if not tidal_api:
        raise HTTPException(status_code=401, detail="TIDAL not connected.")
    
    import subprocess
    import uuid
    import shutil
    
    task_id = str(uuid.uuid4())
    download_dir = ORPHEUS_DIR / "downloads" / task_id
    download_dir.mkdir(parents=True, exist_ok=True)
    
    track_url = f"https://tidal.com/browse/track/{track_id}"
    
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "orpheus.py", track_url, "-o", str(download_dir.absolute())],
            cwd=str(ORPHEUS_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        shutil.rmtree(download_dir, ignore_errors=True)
        raise HTTPException(status_code=504, detail="Download timed out.")
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    
    # Find the downloaded file (newest .flac file in the downloads directory)
    flac_files = sorted(download_dir.rglob("*.flac"), key=os.path.getmtime, reverse=True)
    
    if not flac_files:
        # Try other formats as fallback
        all_audio = sorted(
            [f for f in download_dir.rglob("*") if f.suffix in (".flac", ".m4a", ".mp4", ".ogg")],
            key=os.path.getmtime,
            reverse=True,
        )
        if not all_audio:
            shutil.rmtree(download_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail="Download completed but no audio file found.")
        flac_files = all_audio
    
    file_path = flac_files[0]
    
    # Schedule cleanup after response is sent
    background_tasks.add_task(shutil.rmtree, download_dir, ignore_errors=True)
    
    # Return the file to the browser
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="audio/flac",
    )'''

content = content.replace(old_download_track, new_download_track)
file_path.write_text(content, encoding='utf-8')

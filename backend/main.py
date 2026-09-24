"""
SoundHaven Backend - FastAPI Server
====================================
Direct Python integration with OrpheusDL's TidalApi for search, auth, and download.
No subprocess hacks. Clean, reliable, and Windows-compatible.
"""

import os
import sys
import json
import pickle
import asyncio
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Query, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAX_CONCURRENT_DOWNLOADS = 8
download_semaphore_async = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
download_semaphore_thread = threading.Semaphore(MAX_CONCURRENT_DOWNLOADS)

# Add orpheusdl directory to Python path so we can import its modules
ORPHEUS_DIR = Path(__file__).parent / "orpheusdl"
sys.path.insert(0, str(ORPHEUS_DIR))

from modules.tidal.tidal_api import (
    TidalTvSession,
    TidalApi,
    SessionType,
    TidalAuthError,
    TidalError,
)

# â”€â”€â”€ App Setup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

app = FastAPI(title="SoundHaven Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# â”€â”€â”€ Constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CONFIG_DIR = ORPHEUS_DIR / "config"
SETTINGS_PATH = CONFIG_DIR / "settings.json"
SESSION_STORAGE_PATH = CONFIG_DIR / "soundhaven_session.json"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "soundhaven_admin_2026")

DESKTOP_CLIENT_ID = "fX2JxdmntZWK0ixT"
DESKTOP_CLIENT_SECRET = "1Nn9AfDAjxrgJFJbKNWLeAyKGVGmINuXPPLHVXAvxAg="

# â”€â”€â”€ Global State â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

tidal_api: TidalApi | None = None
tv_session: TidalTvSession | None = None

# Background auth state (for the TV OAuth flow polling)
auth_state = {
    "status": "idle",          # idle | pending | success | error
    "user_code": None,         # e.g. "RUTXB"
    "verification_url": None,  # e.g. "https://link.tidal.com/RUTXB"
    "error_message": None,
}

# Background auth state (for Desktop OAuth flow polling)
desktop_auth_state = {
    "status": "idle",
    "user_code": None,
    "verification_url": None,
    "error_message": None,
}

# In-memory storage for desktop token
desktop_session_data = {
    "access_token": None,
    "refresh_token": None,
    "expires": None,
}

# â”€â”€â”€ Pydantic Models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class AdminAuth(BaseModel):
    password: str

class SearchQuery(BaseModel):
    query: str
    search_type: str = "all"  # all, track, album, playlist, artist
    limit: int = 20

# â”€â”€â”€ Helper Functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def load_settings() -> dict:
    """Load OrpheusDL settings.json"""
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    return {}

def save_session_storage(session: TidalTvSession):
    """Save authenticated session to disk for persistence."""
    data = {}
    if SESSION_STORAGE_PATH.exists():
        try:
            with open(SESSION_STORAGE_PATH, "r") as f:
                data = json.load(f)
        except:
            pass

    data.update({
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires": session.expires.isoformat() if session.expires else None,
        "user_id": str(session.user_id) if session.user_id else None,
        "country_code": session.country_code,
    })
    
    with open(SESSION_STORAGE_PATH, "w") as f:
        json.dump(data, f, indent=2)

    # Sync to OrpheusDL's native loginstorage.bin so subprocesses can use it
    try:
        import pickle
        storage_dict = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires": session.expires,
            "user_id": session.user_id,
            "country_code": session.country_code
        }
        login_data = {
            'advancedmode': False,
            'modules': {
                'tidal': {
                    'selected': 'default',
                    'sessions': {
                        'default': {
                            'clear_session': False,
                            'custom_data': {
                                'sessions': {
                                    'TV': storage_dict
                                }
                            }
                        }
                    }
                }
            }
        }
        with open(CONFIG_DIR / "loginstorage.bin", "wb") as f:
            pickle.dump(login_data, f)
    except Exception as e:
        print(f"[SoundHaven] WARN: Failed to sync loginstorage.bin: {e}")

def load_session_storage() -> dict | None:
    """Load saved session from disk."""
    if SESSION_STORAGE_PATH.exists():
        with open(SESSION_STORAGE_PATH, "r") as f:
            data = json.load(f)
        if data.get("access_token"):
            return data
    return None

def init_tidal_api_from_storage():
    """Try to restore a saved session and initialize the TidalApi."""
    global tidal_api, tv_session, desktop_session_data
    
    stored = load_session_storage()
    if not stored:
        return False
        
    # Load Desktop Token if available
    if stored.get("desktop_access_token"):
        desktop_session_data["access_token"] = stored["desktop_access_token"]
        desktop_session_data["refresh_token"] = stored["desktop_refresh_token"]
        if stored.get("desktop_expires"):
            desktop_session_data["expires"] = datetime.fromisoformat(stored["desktop_expires"])
            
    # Check if desktop token needs refresh (optional fallback, but better to refresh)
    import requests as req
    if desktop_session_data.get("expires") and datetime.now() > desktop_session_data["expires"]:
        try:
            r = req.post("https://auth.tidal.com/v1/oauth2/token", data={
                "client_id": DESKTOP_CLIENT_ID,
                "client_secret": DESKTOP_CLIENT_SECRET,
                "refresh_token": desktop_session_data["refresh_token"],
                "grant_type": "refresh_token"
            })
            if r.status_code == 200:
                desktop_session_data["access_token"] = r.json()["access_token"]
                desktop_session_data["refresh_token"] = r.json().get("refresh_token", desktop_session_data["refresh_token"])
                desktop_session_data["expires"] = datetime.now() + timedelta(seconds=r.json()["expires_in"])
                # Save to storage
                stored["desktop_access_token"] = desktop_session_data["access_token"]
                stored["desktop_refresh_token"] = desktop_session_data["refresh_token"]
                stored["desktop_expires"] = desktop_session_data["expires"].isoformat()
                with open(SESSION_STORAGE_PATH, "w") as f:
                    json.dump(stored, f, indent=2)
        except Exception as e:
            print(f"[SoundHaven] WARN: Failed to refresh desktop token: {e}")
    
    settings = load_settings()
    tidal_cfg = settings.get("modules", {}).get("tidal", {})
    
    tv_token = tidal_cfg.get("tv_atmos_token", "")
    tv_secret = tidal_cfg.get("tv_atmos_secret", "")
    
    if not tv_token or not tv_secret:
        return False
    
    session = TidalTvSession(tv_token, tv_secret)
    session.access_token = stored["access_token"]
    session.refresh_token = stored["refresh_token"]
    session.expires = datetime.fromisoformat(stored["expires"]) if stored.get("expires") else None
    session.user_id = stored.get("user_id")
    session.country_code = stored.get("country_code")
    
    # Check if token is expired; if so, try refreshing
    if session.expires and datetime.now() > session.expires:
        try:
            if not session.refresh():
                return False
            save_session_storage(session)
        except Exception:
            return False
    
    tv_session = session
    tidal_api = TidalApi({SessionType.TV.name: session})
    return True

def verify_admin(auth: AdminAuth):
    """Verify admin password."""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    return True

# ——————————————————————————————————————————————————————————————————————————————————————————————————

@app.on_event("startup")
async def startup():
    """Try to restore session on server startup and cleanup temp files."""
    # Clean up temporary downloads
    download_dir = ORPHEUS_DIR / "downloads"
    import shutil
    if download_dir.exists():
        shutil.rmtree(download_dir, ignore_errors=True)
        print("[SoundHaven] OK: Cleaned up temporary downloads directory.")
        
    if init_tidal_api_from_storage():
        print("[SoundHaven] OK: Restored TIDAL session from saved storage.")
    else:
        print("[SoundHaven] WARN: No active TIDAL session. Admin needs to connect via /admin.")

# ——————————————————————————————————————————————————————————————————————————————————————————————————

@app.get("/")
def root():
    return {"status": "ok", "message": "SoundHaven Backend v1.0.0"}

@app.get("/api/auth/status")
def get_auth_status():
    """Check if TIDAL is connected (public endpoint, no sensitive data exposed)."""
    status = {
        "authenticated": False,
        "desktop_authenticated": False
    }
    if tidal_api and tv_session and tv_session.access_token:
        status["authenticated"] = True
    if desktop_session_data.get("access_token"):
        status["desktop_authenticated"] = True
    return status

@app.get("/api/auth/pending")
def get_auth_pending():
    """Check the current state of a pending OAuth login flow."""
    return auth_state
    
@app.get("/api/auth/desktop/pending")
def get_desktop_auth_pending():
    """Check the current state of a pending Desktop OAuth login flow."""
    return desktop_auth_state

# â”€â”€â”€ Admin Endpoints (Password Protected) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/admin/verify")
def admin_verify(auth: AdminAuth):
    """Verify admin password. Frontend uses this to unlock /admin page."""
    verify_admin(auth)
    return {"status": "ok", "message": "Admin access granted."}

@app.post("/api/admin/auth/login")
async def admin_trigger_login(auth: AdminAuth):
    """
    Start the TIDAL TV OAuth Device Code flow.
    Returns a user_code and verification URL for the admin to complete in their browser/phone.
    The backend then polls TIDAL in the background until the user authorizes.
    """
    global auth_state, tidal_api, tv_session
    verify_admin(auth)
    
    settings = load_settings()
    tidal_cfg = settings.get("modules", {}).get("tidal", {})
    tv_token = tidal_cfg.get("tv_atmos_token", "")
    tv_secret = tidal_cfg.get("tv_atmos_secret", "")
    
    if not tv_token or not tv_secret:
        raise HTTPException(status_code=500, detail="TIDAL tokens not found in settings.json")
    
    # Create a new TV session
    session = TidalTvSession(tv_token, tv_secret)
    
    # Step 1: Request device authorization (this is the non-blocking part)
    import requests as req
    r = req.post(
        session.TIDAL_AUTH_BASE + "oauth2/device_authorization",
        data={"client_id": session.client_id, "scope": "r_usr w_usr"},
    )
    
    if r.status_code != 200:
        auth_state = {"status": "error", "user_code": None, "verification_url": None, 
                      "error_message": "Authorization failed. Token might be outdated."}
        raise HTTPException(status_code=500, detail="TIDAL device authorization failed.")
    
    device_code = r.json()["deviceCode"]
    user_code = r.json()["userCode"]
    verification_url = f"https://link.tidal.com/{user_code}"
    
    auth_state = {
        "status": "pending",
        "user_code": user_code,
        "verification_url": verification_url,
        "error_message": None,
    }
    
    # Step 2: Start background polling thread
    def poll_for_auth():
        global auth_state, tidal_api, tv_session
        
        data = {
            "client_id": session.client_id,
            "device_code": device_code,
            "client_secret": session.client_secret,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "scope": "r_usr w_usr",
        }
        
        max_attempts = 120  # 120 * 2s = 4 minutes max wait
        for attempt in range(max_attempts):
            if auth_state["status"] != "pending":
                return  # Cancelled or already done
                
            time.sleep(2)
            
            try:
                r = req.post(session.TIDAL_AUTH_BASE + "oauth2/token", data=data)
            except Exception as e:
                continue
            
            if r.status_code == 200:
                # Success! Extract tokens
                session.access_token = r.json()["access_token"]
                session.refresh_token = r.json()["refresh_token"]
                session.expires = datetime.now() + timedelta(seconds=r.json()["expires_in"])
                
                # Get user info
                try:
                    r2 = req.get(
                        "https://api.tidal.com/v1/sessions",
                        headers=session.auth_headers(),
                    )
                    if r2.status_code == 200:
                        session.user_id = r2.json()["userId"]
                        session.country_code = r2.json()["countryCode"]
                except:
                    pass
                
                # Save session and initialize API
                save_session_storage(session)
                tv_session = session
                tidal_api = TidalApi({SessionType.TV.name: session})
                
                auth_state = {
                    "status": "success",
                    "user_code": user_code,
                    "verification_url": verification_url,
                    "error_message": None,
                }
                print(f"[SoundHaven] OK: TIDAL login successful! User ID: {session.user_id}")
                return
            
            elif r.status_code == 400:
                # Still waiting for user to authorize
                continue
            
            elif r.status_code == 401:
                auth_state = {
                    "status": "error",
                    "user_code": user_code,
                    "verification_url": verification_url,
                    "error_message": "Authorization denied or expired.",
                }
                return
        
        # Timed out
        auth_state = {
            "status": "error",
            "user_code": user_code,
            "verification_url": verification_url,
            "error_message": "Authorization timed out. Please try again.",
        }
    
    thread = threading.Thread(target=poll_for_auth, daemon=True)
    thread.start()
    
    return {
        "status": "pending",
        "user_code": user_code,
        "verification_url": verification_url,
        "message": f"Open {verification_url} on your phone/browser and log in to TIDAL.",
    }

@app.post("/api/admin/auth/desktop/login")
def desktop_login(auth: AdminAuth):
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    
    import requests as req
    try:
        # 1. Get device code
        r = req.post("https://auth.tidal.com/v1/oauth2/device_authorization", 
            data={"client_id": DESKTOP_CLIENT_ID, "scope": "r_usr w_usr"},
        )  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    if r.status_code != 200:
        desktop_auth_state = {"status": "error", "user_code": None, "verification_url": None, 
                              "error_message": "Desktop Authorization failed."}
        raise HTTPException(status_code=500, detail="TIDAL desktop device authorization failed.")
    
    d = r.json()
    device_code = d["deviceCode"]
    user_code = d["userCode"]
    verification_url = f"https://link.tidal.com/{user_code}"
    
    desktop_auth_state = {
        "status": "pending",
        "user_code": user_code,
        "verification_url": verification_url,
        "error_message": None,
    }
    
    def poll_for_desktop_auth():
        global desktop_auth_state, desktop_session_data
        
        expires = time.time() + d["expiresIn"]
        while time.time() < expires:
            if desktop_auth_state["status"] != "pending":
                return
            
            time.sleep(d["interval"])
            
            try:
                r = req.post("https://auth.tidal.com/v1/oauth2/token", data={
                    "client_id": DESKTOP_CLIENT_ID,
                    "client_secret": DESKTOP_CLIENT_SECRET,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "scope": "r_usr w_usr",
                })
            except Exception:
                continue
            
            if r.status_code == 200:
                desktop_session_data["access_token"] = r.json()["access_token"]
                desktop_session_data["refresh_token"] = r.json()["refresh_token"]
                desktop_session_data["expires"] = datetime.now() + timedelta(seconds=r.json()["expires_in"])
                
                # Save to disk alongside TV token
                stored = {}
                if SESSION_STORAGE_PATH.exists():
                    try:
                        with open(SESSION_STORAGE_PATH, "r") as f:
                            stored = json.load(f)
                    except:
                        pass
                
                stored["desktop_access_token"] = desktop_session_data["access_token"]
                stored["desktop_refresh_token"] = desktop_session_data["refresh_token"]
                stored["desktop_expires"] = desktop_session_data["expires"].isoformat()
                
                with open(SESSION_STORAGE_PATH, "w") as f:
                    json.dump(stored, f, indent=2)
                
                desktop_auth_state = {
                    "status": "success",
                    "user_code": user_code,
                    "verification_url": verification_url,
                    "error_message": None,
                }
                print(f"[SoundHaven] OK: TIDAL Desktop login successful!")
                return
            
            elif r.status_code == 400:
                continue
            
            elif r.status_code == 401:
                desktop_auth_state = {
                    "status": "error",
                    "user_code": user_code,
                    "verification_url": verification_url,
                    "error_message": "Authorization denied or expired.",
                }
                return
        
        desktop_auth_state = {
            "status": "error",
            "user_code": user_code,
            "verification_url": verification_url,
            "error_message": "Authorization timed out. Please try again.",
        }
    
    thread = threading.Thread(target=poll_for_desktop_auth, daemon=True)
    thread.start()
    
    return {
        "status": "pending",
        "user_code": user_code,
        "verification_url": verification_url,
    }

@app.post("/api/admin/auth/logout")
def admin_logout(auth: AdminAuth):
    """Disconnect the current TIDAL account (deletes saved session)."""
    global tidal_api, tv_session, auth_state
    verify_admin(auth)
    
    # Remove session file
    if SESSION_STORAGE_PATH.exists():
        os.remove(SESSION_STORAGE_PATH)
    
    # Clear global state
    tidal_api = None
    tv_session = None
    auth_state = {"status": "idle", "user_code": None, "verification_url": None, "error_message": None}
    
    return {"status": "ok", "message": "TIDAL account disconnected."}

@app.post("/api/admin/auth/desktop/disconnect")
def desktop_disconnect(auth: AdminAuth):
    global desktop_session_data
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    
    desktop_session_data = {
        "access_token": None,
        "refresh_token": None,
        "expires": None
    }
    
    # Save the cleared token to file
    if SESSION_STORAGE_PATH.exists():
        with open(SESSION_STORAGE_PATH, "r") as f:
            stored = json.load(f)
        stored["desktop_access_token"] = None
        stored["desktop_refresh_token"] = None
        stored["desktop_expires"] = None
        with open(SESSION_STORAGE_PATH, "w") as f:
            json.dump(stored, f, indent=4)
            
    return {"status": "ok", "message": "Desktop session disconnected."}

# â”€â”€â”€ Search Endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/api/search")
def search_tidal(q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=300)):
    """
    Search TIDAL for tracks, albums, artists, and playlists.
    Returns structured results for the frontend.
    """
    if not tidal_api and not desktop_session_data.get("access_token"):
        raise HTTPException(status_code=401, detail="TIDAL not connected. Admin needs to link account first.")
    
    import re
    # Check if user pasted a tidal playlist URL
    if "tidal.com" in q and ("playlist/" in q or "playlists/" in q):
        match = re.search(r"playlist(?:s)?/([a-zA-Z0-9-]+)", q)
        if match:
            uuid = match.group(1)
            try:
                pl = tidal_api.get_playlist(uuid)
                pl_obj = {
                    "id": pl.get("uuid", uuid),
                    "title": pl.get("title", "Unknown Playlist"),
                    "creator": pl.get("creator", {}).get("name") if pl.get("creator", {}).get("name") else ("TIDAL" if pl.get("type") == "EDITORIAL" else "user"),
                    "trackCount": pl.get("numberOfTracks", 0),
                    "duration": pl.get("duration", 0),
                    "image": pl.get("image", ""),
                    "squareImage": pl.get("squareImage", "")
                }
                return {
                    "status": "ok",
                    "results": {
                        "tracks": [],
                        "albums": [],
                        "artists": [],
                        "playlists": [pl_obj]
                    }
                }
            except Exception as e:
                print(f"[SoundHaven] WARN: Failed to fetch playlist from URL: {e}")
                # Fallthrough to normal search if it fails
    
    raw = {}
    if desktop_session_data.get("access_token"):
        import requests as req
        
        # Auto-refresh if expired
        if desktop_session_data.get("expires") and datetime.now() > desktop_session_data["expires"]:
            try:
                r = req.post("https://auth.tidal.com/v1/oauth2/token", data={
                    "client_id": DESKTOP_CLIENT_ID,
                    "client_secret": DESKTOP_CLIENT_SECRET,
                    "refresh_token": desktop_session_data["refresh_token"],
                    "grant_type": "refresh_token"
                })
                if r.status_code == 200:
                    desktop_session_data["access_token"] = r.json()["access_token"]
                    desktop_session_data["refresh_token"] = r.json().get("refresh_token", desktop_session_data["refresh_token"])
                    desktop_session_data["expires"] = datetime.now() + timedelta(seconds=r.json()["expires_in"])
                    
                    if SESSION_STORAGE_PATH.exists():
                        with open(SESSION_STORAGE_PATH, "r") as f:
                            stored = json.load(f)
                        stored["desktop_access_token"] = desktop_session_data["access_token"]
                        stored["desktop_refresh_token"] = desktop_session_data["refresh_token"]
                        stored["desktop_expires"] = desktop_session_data["expires"].isoformat()
                        with open(SESSION_STORAGE_PATH, "w") as f:
                            json.dump(stored, f, indent=2)
            except Exception as e:
                print(f"[SoundHaven] WARN: Failed to auto-refresh desktop token: {e}")
                
        country_code = tv_session.country_code if tv_session and hasattr(tv_session, "country_code") and tv_session.country_code else "US"
        headers = {"Authorization": f"Bearer {desktop_session_data['access_token']}"}
        params = {"query": q, "limit": limit, "countryCode": country_code, "types": "TRACKS,ALBUMS,ARTISTS,PLAYLISTS"}
        try:
            r = req.get("https://api.tidal.com/v1/search", params=params, headers=headers)
            if r.status_code == 200:
                raw = r.json()
            else:
                print(f"[SoundHaven] WARN: Desktop search failed ({r.status_code}): {r.text}")
                # Fallback to TV session if Desktop fails
                if tidal_api:
                    raw = tidal_api.get_search_data(q, limit=limit)
        except Exception as e:
            print(f"[SoundHaven] WARN: Desktop search error: {e}")
            if tidal_api:
                raw = tidal_api.get_search_data(q, limit=limit)
    else:
        try:
            raw = tidal_api.get_search_data(q, limit=limit)
        except TidalError as e:
            raise HTTPException(status_code=502, detail=f"TIDAL API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    # Format tracks
    tracks = []
    for item in (raw.get("tracks", {}).get("items", []) or []):
        tracks.append({
            "id": item.get("id"),
            "title": item.get("title", ""),
            "artist": ", ".join(a.get("name", "") for a in item.get("artists", [])) if item.get("artists") else item.get("artist", {}).get("name", "Unknown"),
            "album": item.get("album", {}).get("title", ""),
            "album_id": item.get("album", {}).get("id"),
            "duration": item.get("duration", 0),
            "track_number": item.get("trackNumber", 0),
            "explicit": item.get("explicit", False),
            "cover_url": f"https://resources.tidal.com/images/{item.get('album', {}).get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("album", {}).get("cover") else None,
            "url": f"https://tidal.com/browse/track/{item.get('id')}",
        })
    
    # Format albums
    albums = []
    for item in (raw.get("albums", {}).get("items", []) or []):
        albums.append({
            "id": item.get("id"),
            "title": item.get("title", ""),
            "artist": item.get("artist", {}).get("name", "Unknown") if item.get("artist") else (item.get("artists", [{}])[0].get("name", "Unknown") if item.get("artists") else "Unknown"),
            "release_date": item.get("releaseDate", ""),
            "number_of_tracks": item.get("numberOfTracks", 0),
            "duration": item.get("duration", 0),
            "explicit": item.get("explicit", False),
            "cover_url": f"https://resources.tidal.com/images/{item.get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("cover") else None,
            "url": f"https://tidal.com/browse/album/{item.get('id')}",
        })
    
    # Format artists
    artists = []
    for item in (raw.get("artists", {}).get("items", []) or []):
        pic = item.get("picture", "")
        artists.append({
            "id": item.get("id"),
            "name": item.get("name", ""),
            "picture_url": f"https://resources.tidal.com/images/{pic.replace('-', '/')}/320x320.jpg" if pic else None,
            "url": f"https://tidal.com/browse/artist/{item.get('id')}",
        })
    
    # Format playlists
    playlists = []
    for item in (raw.get("playlists", {}).get("items", []) or []):
        sq_img = item.get("squareImage", "")
        playlists.append({
            "id": item.get("uuid"),
            "title": item.get("title", ""),
            "creator": item.get("creator", {}).get("name", "TIDAL") if item.get("creator") else "TIDAL",
            "number_of_tracks": item.get("numberOfTracks", 0),
            "duration": item.get("duration", 0),
            "cover_url": f"https://resources.tidal.com/images/{sq_img.replace('-', '/')}/640x640.jpg" if sq_img else None,
            "url": f"https://tidal.com/browse/playlist/{item.get('uuid')}",
        })
    
    return {
        "tracks": tracks,
        "albums": albums,
        "artists": artists,
        "playlists": playlists,
    }

@app.get("/api/album/{album_id}/tracks")
def get_album_tracks(album_id: int):
    """Get all tracks from a specific album."""
    if not tidal_api:
        raise HTTPException(status_code=401, detail="TIDAL not connected.")
    
    try:
        raw = tidal_api.get_album_tracks(str(album_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    tracks = []
    for item in raw.get("items", []):
        tracks.append({
            "id": item.get("id"),
            "title": item.get("title", ""),
            "artist": item.get("artist", {}).get("name", "Unknown"),
            "duration": item.get("duration", 0),
            "track_number": item.get("trackNumber", 0),
            "explicit": item.get("explicit", False),
            "cover_url": f"https://resources.tidal.com/images/{item.get('album', {}).get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("album", {}).get("cover") else None,
        })
    
    return {"tracks": tracks}

@app.get("/api/playlist/{playlist_uuid}/tracks")
def get_playlist_tracks(playlist_uuid: str):
    """Get all tracks from a specific playlist."""
    if not tidal_api:
        raise HTTPException(status_code=401, detail="TIDAL not connected.")
    
    try:
        raw = tidal_api.get_playlist_items(playlist_uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    tracks = []
    for item_wrapper in raw.get("items", []):
        # Playlists wrap tracks in an "item" object with a "type": "track"
        if item_wrapper.get("type") != "track":
            continue
        item = item_wrapper.get("item", {})
        
        # Handle multiple artists
        artist_names = []
        for a in item.get("artists", []):
            artist_names.append(a.get("name", "Unknown"))
        artist_str = ", ".join(artist_names) if artist_names else item.get("artist", {}).get("name", "Unknown")

        tracks.append({
            "id": item.get("id"),
            "title": item.get("title", ""),
            "artist": artist_str,
            "duration": item.get("duration", 0),
            "track_number": item.get("trackNumber", 0),
            "explicit": item.get("explicit", False),
            "cover_url": f"https://resources.tidal.com/images/{item.get('album', {}).get('cover', '').replace('-', '/')}/640x640.jpg" if item.get("album", {}).get("cover") else None,
        })
    
    return {"tracks": tracks}

@app.get("/api/artist/{artist_id}")
def get_artist_profile(artist_id: str):
    """Get artist profile details, top tracks, albums, and EPs."""
    if not tidal_api:
        raise HTTPException(status_code=401, detail="TIDAL not connected.")
    
    try:
        # Basic Info
        artist_info = tidal_api.get_artist(artist_id)
        
        # Top Tracks (using _get since it's not a named method in tidal_api)
        try:
            top_tracks_raw = tidal_api._get(f"artists/{artist_id}/toptracks", params={"limit": 10, "countryCode": "US"})
        except Exception as e:
            print(f"[SoundHaven] WARN: Failed to fetch top tracks for artist {artist_id}: {e}")
            top_tracks_raw = {"items": []}

        # Albums
        try:
            albums_raw = tidal_api.get_artist_albums(artist_id)
        except Exception:
            albums_raw = {"items": []}

        # EPs & Singles
        try:
            eps_raw = tidal_api.get_artist_albums_ep_singles(artist_id)
        except Exception:
            eps_raw = {"items": []}

        # Format Top Tracks
        tracks = []
        for item in top_tracks_raw.get("items", []):
            artist_names = [a.get("name", "Unknown") for a in item.get("artists", [])]
            artist_str = ", ".join(artist_names) if artist_names else item.get("artist", {}).get("name", "Unknown")
            
            tracks.append({
                "id": item.get("id"),
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
            "eps_singles": eps
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# â”€â”€â”€ Download Endpoint (Stream & Cleanup) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/api/download/{track_id}")
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
        async with download_semaphore_async:
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
    )

collection_tasks = {}
active_processes = {}

import threading
import subprocess
import uuid
import zipfile
import shutil

async def process_collection_download(task_id: str, type: str, collection_id: str):
    try:
        download_dir = ORPHEUS_DIR / "downloads" / task_id
        download_dir.mkdir(parents=True, exist_ok=True)
        collection_url = f"https://tidal.com/browse/{type}/{collection_id}"
        
        collection_tasks[task_id] = {"status": "processing", "message": "Downloading tracks (this may take a few minutes)..."}
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        async with download_semaphore_async:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "orpheus.py", collection_url, "-o", str(download_dir.absolute()),
                cwd=str(ORPHEUS_DIR),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            active_processes[task_id] = process
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=3600)
            except asyncio.TimeoutError:
                process.kill()
                raise
        
        if task_id in active_processes:
            del active_processes[task_id]
            
        if collection_tasks.get(task_id, {}).get("status") == "cancelled":
            return
            
        audio_files = sorted(
            [f for f in download_dir.rglob("*") if f.suffix in (".flac", ".m4a", ".mp4", ".ogg")],
            key=lambda x: x.name
        )
        
        if not audio_files:
            collection_tasks[task_id] = {"status": "error", "message": "Download completed but no audio files found."}
            return
            
        collection_tasks[task_id] = {"status": "processing", "message": "Zipping tracks..."}
        
        playlist_path = download_dir / f"{type}_{collection_id}.m3u8"
        with open(playlist_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for audio_file in audio_files:
                rel_path = audio_file.relative_to(download_dir)
                f.write(f"{rel_path.as_posix()}\n")
                
        zip_path = ORPHEUS_DIR / "downloads" / f"{type}_{collection_id}_{task_id}.zip"
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zipf:
            zipf.write(playlist_path, arcname=playlist_path.name)
            for item in download_dir.rglob("*"):
                if item.is_file() and item.name != playlist_path.name:
                    arcname = item.relative_to(download_dir)
                    zipf.write(item, arcname=str(arcname))
                    
        shutil.rmtree(download_dir, ignore_errors=True)
        
        collection_tasks[task_id] = {
            "status": "ready",
            "zip_path": str(zip_path),
            "filename": f"SoundHaven_{type}_{collection_id}.zip"
        }
    except subprocess.TimeoutExpired:
        if task_id in active_processes:
            active_processes[task_id].kill()
            del active_processes[task_id]
        collection_tasks[task_id] = {"status": "error", "message": "Download timed out."}
    except Exception as e:
        collection_tasks[task_id] = {"status": "error", "message": str(e)}

@app.delete("/api/download/collection/cancel/{task_id}")
def cancel_download_collection(task_id: str):
    if task_id in active_processes:
        active_processes[task_id].kill()
        del active_processes[task_id]
        
    if task_id in collection_tasks:
        collection_tasks[task_id] = {"status": "cancelled", "message": "Download cancelled by user."}
        
    download_dir = ORPHEUS_DIR / "downloads" / task_id
    if download_dir.exists():
        shutil.rmtree(download_dir, ignore_errors=True)
        
    return {"status": "cancelled"}

@app.get("/api/download/collection/start/{type}/{collection_id}")
async def start_collection_download(type: str, collection_id: str, background_tasks: BackgroundTasks):
    if not tidal_api:
        raise HTTPException(status_code=401, detail="TIDAL not connected.")
    if type not in ["album", "playlist"]:
        raise HTTPException(status_code=400, detail="Invalid collection type.")
        
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_collection_download, task_id, type, collection_id)
    return {"task_id": task_id}

@app.get("/api/download/collection/status/{task_id}")
def check_download_status(task_id: str):
    if task_id not in collection_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return collection_tasks[task_id]

@app.get("/api/download/collection/file/{task_id}")
def get_download_file(task_id: str, background_tasks: BackgroundTasks):
    if task_id not in collection_tasks or collection_tasks[task_id]["status"] != "ready":
        raise HTTPException(status_code=400, detail="File not ready")
        
    zip_path = collection_tasks[task_id]["zip_path"]
    filename = collection_tasks[task_id]["filename"]
    
    def cleanup():
        import os
        try:
            os.remove(zip_path)
            del collection_tasks[task_id]
        except:
            pass
            
    background_tasks.add_task(cleanup)
    
    return FileResponse(
        path=zip_path,
        filename=filename,
        media_type="application/zip",
    )
# â”€â”€â”€ Run â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


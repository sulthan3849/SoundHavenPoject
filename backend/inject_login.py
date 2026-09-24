import os
import json
import pickle
from pathlib import Path
from datetime import datetime

CONFIG_DIR = Path("C:/Mek Project/SoundHavenPoject/backend/orpheusdl/config")
SESSION_STORAGE_PATH = CONFIG_DIR / "soundhaven_session.json"
LOGIN_STORAGE_PATH = CONFIG_DIR / "loginstorage.bin"

def main():
    if not SESSION_STORAGE_PATH.exists():
        print("No soundhaven session found")
        return

    with open(SESSION_STORAGE_PATH, "r") as f:
        data = json.load(f)

    # Reconstruct datetime from string if necessary
    # The actual get_storage expects expires as datetime or float, tidal_api handles it.
    expires_str = data.get("expires")
    if expires_str:
        expires = datetime.fromisoformat(expires_str)
    else:
        expires = None

    storage_dict = {
        "access_token": data.get("access_token"),
        "refresh_token": data.get("refresh_token"),
        "expires": expires,
        "user_id": data.get("user_id"),
        "country_code": data.get("country_code")
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

    with open(LOGIN_STORAGE_PATH, "wb") as f:
        pickle.dump(login_data, f)
        
    print("Successfully injected loginstorage.bin!")

if __name__ == "__main__":
    main()

# Copyright (C) 2026 roblox-multi
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License v3.

import os
import time
import requests
import win32event
import win32api
import msvcrt
import random
import logging
import traceback

class RobloxLauncher:
    def __init__(self):
        self.multi_roblox_mutex = None
        self.mutex_global = None
        self.cookie_file_handle = None
        
        logging.info("roblox-multi Kernel Hook Engine initialized.")
        self._enable_multi_roblox()

    def _enable_multi_roblox(self):
        """
        Locks the 'ROBLOX_singletonEvent' handles before the game client can check for them,
        forcing the engine to open an independent game window for each instance.
        """
        logging.info("Enabling Multi-Instance Bypass Hooks...")

        # Mutex Hooking (Global & Local namespaces)
        try:
            self.mutex_global = win32event.CreateMutex(None, True, r"Global\ROBLOX_singletonEvent")
            if win32api.GetLastError() == 183: 
                logging.warning("Global Namespace Mutex already claimed by another utility.")
            else:
                logging.info("Global Namespace Mutex successfully locked.")
        except Exception as e:
            logging.debug(f"Could not claim Global Mutex (Requires Elevated/Admin privileges): {e}")

        try:
            self.multi_roblox_mutex = win32event.CreateMutex(None, True, "ROBLOX_singletonEvent")
            if win32api.GetLastError() == 183:
                logging.warning("Local Namespace Mutex already claimed.")
            else:
                logging.info("Local Namespace Mutex successfully locked.")
        except Exception as e:
            logging.error(f"Critical error creating Local Mutex: {e}")

        # Roblox Local Storage Synchronization File Lock
        try:
            base_local = os.getenv('LOCALAPPDATA')
            if not base_local: return

            possible_paths = [
                os.path.join(base_local, r'Roblox\LocalStorage\RobloxCookies.dat'),
                os.path.join(base_local, r'Packages\ROBLOXCORPORATION.ROBLOX_55nm5eh3cm0pr\LocalState\RobloxCookies.dat'),
            ]

            target_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    target_path = p
                    break
            
            if target_path:
                logging.info(f"Targeting Roblox Storage File: {target_path}")
                self.cookie_file_handle = open(target_path, 'r+b')
                msvcrt.locking(self.cookie_file_handle.fileno(), msvcrt.LK_NBLCK, os.path.getsize(target_path))
                logging.info("Storage file synchronized and locked.")
            else:
                logging.warning("RobloxCookies.dat file not detected. Initialization skipping.")

        except OSError as e:
            logging.warning(f"Storage file handle already claimed by an active instance: {e}")
        except Exception as e:
            logging.error(f"Error establishing file lock: {e}")

    def _get_csrf_token(self, session):
        try:
            response = session.post("https://auth.roblox.com/v2/logout")
            token = response.headers.get('x-csrf-token')
            if not token:
                logging.error(f"Failed to extract X-CSRF-Token. Status: {response.status_code}")
                return None
            return token
        except Exception as e:
            logging.error(f"CSRF Network Exception: {e}")
            return None

    def _get_auth_ticket(self, session, csrf_token):
        url = "https://auth.roblox.com/v1/authentication-ticket/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.roblox.com/",
            "Origin": "https://www.roblox.com",
            "Content-Type": "application/json",
            "RBX-For-Gameauth": "true",
            "X-CSRF-TOKEN": csrf_token
        }
        
        try:
            response = session.post(url, headers=headers, json={})
            if "rbx-authentication-ticket" not in response.headers:
                logging.error(f"Authentication Ticket generation failed. Status: {response.status_code}")
                return None
            return response.headers.get("rbx-authentication-ticket")
        except Exception as e:
            logging.error(f"Ticket Engine Exception: {e}")
            return None

    def _get_user_id(self, username):
        try:
            r = requests.post("https://users.roblox.com/v1/usernames/users",
                              json={"usernames": [username], "excludeBannedUsers": True})
            data = r.json().get('data', [])
            if data: return data[0]['id']
            return None
        except Exception: 
            return None

    def launch_account(self, cookie, input_value, mode="place"):
        session = requests.Session()
        session.cookies['.ROBLOSECURITY'] = cookie
        session.headers.update({"User-Agent": "Roblox/WinInet"})

        try:
            logging.info(f"Assembling payload... Mode: {mode}, Destination: {input_value}")
            csrf = self._get_csrf_token(session)
            if not csrf: return "Invalid Session Cookie"

            ticket = self._get_auth_ticket(session, csrf)
            if not ticket: return "Ticket Verification Failed"

            launch_time = int(time.time() * 1000)
            browser_id = random.randint(10000000000, 99999999999)
            final_launcher_url = ""

            if mode == "user":
                uid = self._get_user_id(input_value)
                if not uid: return "Target User Missing"
                params = f"request=RequestFollowUser&browserTrackerId={browser_id}&userId={uid}&isPlayTogetherGame=false"
                final_launcher_url = f"https://assetgame.roblox.com/game/PlaceLauncher.ashx?{params}"
            else:
                params = f"request=RequestGame&browserTrackerId={browser_id}&placeId={input_value}&isPlayTogetherGame=false"
                final_launcher_url = f"https://assetgame.roblox.com/game/PlaceLauncher.ashx?{params}"

            protocol = (
                f"roblox-player:1+launchmode:play+gameinfo:{ticket}"
                f"+launchtime:{launch_time}"
                f"+placelauncherurl:{final_launcher_url}"
                f"+browsertrackerid:{browser_id}"
                f"+robloxLocale:en_us+gameLocale:en_us"
            )

            logging.info("Passing protocol sequence to Windows Engine...")
            os.startfile(protocol)
            return "Instance Fired Successfully"

        except Exception as e:
            logging.error(f"Launch Engine Error: {e}")
            logging.debug(traceback.format_exc())
            return f"Error: {e}"
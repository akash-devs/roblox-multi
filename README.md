# Roblox Multi-Instance Launcher (roblox-multi)

An automated, lightweight session manager and multi-instance tool for running concurrent Roblox game clients simultaneously on Windows. 

---

## 🚀 Looking to Download and Play? (Quickest Method)

If you are an end-user and just want to run multiple accounts right now without messing with code, you **do not need to download the source code files**.

1. Look at the right side of this page under the **"Releases"** section.
2. Click on the latest version (e.g., `v1.0.0`).
3. Download the standalone **`roblox-multi.exe`** executable binary.
4. Move it to any folder on your computer and double-click to launch it!

---

## ⚠️ Important Disclaimer & Warnings

**PROJECT IS PROVIDED "AS IS" — USE AT YOUR OWN RISK.**

* **No Liability:** The developer accepts **absolute zero responsibility** for any consequences resulting from the installation or usage of this software. This includes hardware stability, operating system conflicts, data loss, or account restrictions. You assume full liability for your own setup.
* **Terms of Service:** Launching concurrent game windows through third-party automation tools **may violate the Roblox Terms of Service (ToS)**. Utilizing this software could potentially lead to moderate or permanent account enforcement actions or bans.

---

## 🛠️ Repository Organization

This repository is split up to accommodate both regular gamers and software developers:

* **`dist/`**: Contains the compiled source builds if you prefer managing the executable local track manually.
* **`roblox-multi/`**: This folder contains the complete, raw Python source code framework (including `main.py`, `launcher.py`, and `requirements.txt`). If you want to view, audit, or compile the application yourself from scratch, head inside that folder and follow the localized developer guide.

---

## How It Works (A to Z Summary)

Windows natively blocks application duplication using an internal OS flag known as a **Mutex (Mutual Exclusion)**. When a secondary game client launches, it scans the operating system kernel for a handle named `ROBLOX_singletonEvent`—if found, it aborts.

This application safely circumvents that limit by:
1. **Mutex Hooking:** Pre-claiming and holding the `ROBLOX_singletonEvent` handle directly inside the Windows kernel before the official client can inspect it.
2. **File De-confliction:** Applying programmatic file locks (`msvcrt.locking`) to the local cookie database cache to prevent file corruption when multiple game windows write data at the exact same split-second.
3. **Session Ingestion:** Using an automated Selenium instance window to securely save and isolate your profile authentication tokens into an optional hardware-encrypted vault.

---

## License

This project is licensed and distributed under the terms of the **GNU General Public License v3**. See the accompanying `LICENSE` file for full conditions and distribution freedoms.

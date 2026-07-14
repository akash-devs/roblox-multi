# roblox-multi

An automated, lightweight multi-instance manager designed for running concurrent Roblox sessions on Windows architecture. Features automated session token ingestion via a sandboxed login wrapper and optional hardware-encrypted credential vaults.

---

## ⚠️ Important Disclaimer & Warnings

**PROJECT IS PROVIDED "AS IS" — USE AT YOUR OWN RISK.**

* **No Liability:** The developer accepts **absolute zero responsibility** for any consequences resulting from the installation or usage of this software. This includes, but is not limited to, hardware stability issues, operating system failures, loss of data, or account enforcement actions. You are entirely liable for your own configuration.
* **Terms of Service:** Launching concurrent game windows through third-party automation software **is against the Roblox Terms of Service (ToS)**. Utilizing this software may lead to account restrictions, moderations, or permanent bans.

---

## How It Works

Windows operating systems natively restrict application cloning using a kernel object called a **Mutex (Mutual Exclusion)**. 

When the official client initializes, it maps a system-wide hardware handle named `ROBLOX_singletonEvent`. Before a secondary window can initialize, it checks the Windows kernel for this flag; if discovered, the execution path aborts.

**roblox-multi** safely circumvents this:
1. It asynchronously overrides and claims the `ROBLOX_singletonEvent` handle before the game executable completes its initial background check.
2. It applies a low-level programmatic shared file lock (`msvcrt.locking`) over the local cookie database file `RobloxCookies.dat`. This prevents write-access violations and file corruption when multiple game windows attempt to read or modify game state settings at the exact same fraction of a second.

---

## Installation & Usage

Choose **one** of the two deployment methods below to start running multiple accounts:

### Method 1: The Quick Way (Pre-compiled Executable)
No Python installation or command lines required.
1. Download the **`roblox-multi.exe`** file located right side of the main repository click on the releases.
2. Use this pip install command to install all required dependencies."pip install CustomTkinter selenium webdriver-manager requests pywin32 cryptography"
4. Move it to any preferred directory on your computer.
5. Double-click **`roblox-multi.exe`** to launch the software panel directly.

---

### Method 2: Running from Source Code (Python)
For advanced users or developers who prefer interacting with the scripts manually.

#### Prerequisites
* Windows OS Architecture
* **Python 3.10+** installed on your system. *(Ensure you check the box that says **"Add Python to PATH"** during installation)*.

#### Setup Steps
1. Clone or download this repository to your local drive.
2. Open your Windows **Command Prompt (`cmd`)** and change directories into the project folder:
   ```cmd
   cd path/to/your/roblox-multi

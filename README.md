# 1

# auto-bt-manager

A safe, legitimate toolkit to manage and automatically reconnect **your** computer to a Bluetooth speaker using BlueZ (`bluetoothctl`) on Linux.

> **Important:** This project is explicitly designed to control **your local Bluetooth adapter and your own connection attempts only**. It does **not** provide any functionality to interfere with or forcibly disconnect other people's devices. Intentionally attacking or disrupting other devices may be illegal and is not supported.

---

## Table of contents

* [Overview](#overview)
* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)

  * [Connect / Disconnect / Status](#connect--disconnect--status)
  * [Auto-reconnect loop](#auto-reconnect-loop)
* [Service (systemd) example](#service-systemd-example)
* [Cleaning local paired devices (optional & dangerous)](#cleaning-local-paired-devices-optional--dangerous)
* [Troubleshooting](#troubleshooting)
* [Security & Ethics](#security--ethics)
* [FAQ](#faq)
* [Contributing](#contributing)
* [License](#license)

---

## Overview

`auto-bt-manager` is a small set of utilities (Python scripts) and examples that let you automatically scan for, pair with, and connect your Linux machine to a Bluetooth speaker using BlueZ's `bluetoothctl`. It's intended for users who **own** the speaker and want a reliable way to auto-reconnect their computer.

The repository contains two main examples:

* `bt_connect.py` — a minimal helper to connect/disconnect and check status for a single speaker MAC.
* `auto_bt_manager.py` — a more featureful script that scans, pairs if necessary, and runs an auto-reconnect loop. It can optionally (and with explicit configuration) remove other paired-devices from *your local adapter*.

---

## Features

* Scan for a speaker by MAC and attempt to connect when it becomes visible.
* Pair automatically (if needed) — may require manual confirmation on the speaker.
* Auto-reconnect loop with configurable retry and scan intervals.
* Optional cleanup of locally paired devices (affects only your computer's pairing list).
* Clear, documented usage and a systemd service example for background operation.

---

## Requirements

* Linux with **BlueZ** installed (`bluetoothctl` available on PATH).
* Python 3.8+.
* Appropriate user permissions to control Bluetooth (running with your user or `sudo`, depending on distro and policy).

---

## Installation

1. Clone the repository (or copy the scripts) to your machine:

```bash
git clone <your-repo-url>
cd auto-bt-manager
```

2. Make the scripts executable (optional):

```bash
chmod +x bt_connect.py auto_bt_manager.py
```

3. Edit the configuration constants in the script(s) (see [Configuration](#configuration)).

---

## Configuration

Open the script you want to use and set the following values near the top:

* `SPEAKER_MAC` — change to your speaker's MAC address (format: `AA:BB:CC:DD:EE:FF`).
* `SCAN_TIMEOUT`, `RETRY_INTERVAL`, `MAX_RETRIES` — tune scanning and retry behavior.
* `CLEAN_LOCAL_PAIRED` (in `auto_bt_manager.py`) — **default: `False`**. If enabled, the script will remove other devices from **your computer's** paired device list. Use with care.

How to find the speaker MAC:

```bash
bluetoothctl
# inside bluetoothctl run:
scan on
# watch the output for your speaker or
paired-devices
```

---

## Usage

### Connect / Disconnect / Status (bt_connect.py)

```bash
# Connect to the speaker (one-off)
./bt_connect.py connect

# Disconnect
./bt_connect.py disconnect

# Show status/info
./bt_connect.py status

# Start an autoreconnect loop (CTRL+C to stop)
./bt_connect.py autoreconnect
```

`bt_connect.py` is minimal and demonstrates basic interactions with `bluetoothctl`.

### Auto-reconnect loop (auto_bt_manager.py)

This script continuously scans for the configured speaker and, when visible, will attempt to pair (if needed) and connect.

```bash
./auto_bt_manager.py
```

If you want to run it with elevated permissions (some environments require it):

```bash
sudo ./auto_bt_manager.py
```

**Note:** The loop prints timestamps and status messages so you can follow what it's doing.

---

## Service (systemd) example

Create a systemd unit to run the auto-reconnect loop at startup. Example file: `/etc/systemd/system/auto-bt-manager.service`:

```ini
[Unit]
Description=Auto Bluetooth Speaker Reconnect (auto-bt-manager)
After=bluetooth.target

[Service]
Type=simple
User=your-username
Group=your-username
ExecStart=/usr/bin/python3 /path/to/auto_bt_manager.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now auto-bt-manager.service
```

Adjust `User`/`Group` as appropriate for your setup.

---

## Cleaning local paired devices (optional & dangerous)

If `CLEAN_LOCAL_PAIRED = True`, the script will remove other paired devices from **your computer**. Important:

* This only affects the **local adapter's paired-devices list** on your computer. It does **not** remove pairings from the speaker or from other people's devices.
* Use this only if you understand and accept that you will need to re-pair devices you remove.
* If you are unsure, leave `CLEAN_LOCAL_PAIRED = False`.

---

## Troubleshooting

**Problem: `bluetoothctl` reports permission errors**

* Try running the script with `sudo`, or add your user to the `bluetooth` group (distro-dependent).

**Problem: Pairing hangs or requires a PIN**

* Some speakers require you to confirm pairing on the speaker or enter a PIN. Watch the speaker for prompts and accept/confirm if required.

**Problem: Still not connecting even though speaker is visible**

* Check the speaker supports the A2DP/Audio profile.
* Some desktop environments manage Bluetooth connections (Network Manager, GNOME Bluetooth). They may interfere; try disabling other Bluetooth front-ends while testing.

**Problem: Speaker allows multipoint and stays connected to another device**

* Multipoint-enabled speakers can remain connected to multiple devices; behavior depends on speaker model. If you want only your device connected, reset the speaker and pair only your machine immediately afterward (speaker manual or vendor app usually explains factory reset).

---

## Security & Ethics

This repository intentionally avoids any instructions or tools for interfering with or forcibly disconnecting other people’s devices. Use the scripts only to manage connections from **your** machine to devices you own. Misuse to attack or disrupt others is not permitted and may be illegal in many jurisdictions.

---

## FAQ

**Q: Will this script disconnect someone else from my speaker?**
A: Only indirectly — if your device legitimately connects, the speaker may choose to drop another connection as part of its normal behavior. The script does not implement attacks or denial-of-service behavior.

**Q: Can I use this on Windows or macOS?**
A: The scripts are written for Linux/BlueZ. For macOS, consider `blueutil` or CoreBluetooth; for Windows, use native Windows Bluetooth APIs or a small C#/PowerShell helper. Contact the maintainer for example code.

**Q: Can I run multiple instances for different speakers?**
A: Yes — copy the script and set a different `SPEAKER_MAC` for each instance, or adapt the code to accept a MAC as a CLI argument.

---

## Contributing

Contributions are welcome! Suggestions:

* Make the scripts accept CLI args (MAC, scan interval, etc.).
* Add proper logging to a file instead of stdout.
* Add unit tests for parsing functions (mock `bluetoothctl` output).

Please open an issue or a PR with changes.

---

## License

This project is provided under the MIT License. See `LICENSE` for details.

---

If you want, I can also:

* Convert this README to a `README.md` file in the repo (ready-to-save).
* Provide a `systemd` unit tuned for your exact distribution.
* Add CLI argument support so you can pass the MAC at runtime.
* Create a Windows or macOS companion script — tell me which OS and I’ll draft it.



#2



# Bluetooth Speaker Control Script

A Python script to aggressively disconnect other devices from a Bluetooth speaker and connect your own device. This script is designed for Linux systems using `bluetoothctl`.

## ⚠️ Important Disclaimer

This script performs actions that can be disruptive. It is provided for **educational purposes and for use on your own equipment only**. Using this script to interfere with devices that do not belong to you may be illegal or considered malicious activity in your jurisdiction. **You are responsible for how you use this tool.**

## How It Works

The script automates the command-line Bluetooth utility `bluetoothctl` to perform a sequence of actions:

1.  **Pairing:** It first ensures your computer is paired with the target speaker. If not, it attempts to pair.
2.  **Standard Connection:** It attempts to connect normally. For many speakers, an incoming connection from a paired device will automatically disconnect the currently active device.
3.  **Force Disconnect (DoS):** If the standard connection fails (e.g., the speaker is "locked" to another device), the script escalates to a more aggressive method. It floods the speaker with rapid connection requests. This Denial-of-Service (DoS) attack often overwhelms the speaker's firmware, causing it to drop its existing connection. After the flood, it attempts one final, clean connection.

## Prerequisites

*   **Operating System:** Linux (e.g., Ubuntu, Debian, Arch, etc.).
*   **Bluetooth Stack:** BlueZ (the default Linux Bluetooth stack).
*   **Python 3:** Ensure you have Python 3 installed.
*   **Administrator Privileges:** This script **must** be run with `sudo` to interact with system-level Bluetooth hardware.

### Installation Steps

1.  **Install Bluetooth Tools:**
    If you don't have `bluetoothctl` and related tools, install them using your package manager.

    For Debian/Ubuntu:
    ```bash
    sudo apt-get update
    sudo apt-get install bluetooth bluez
    ```

    For Arch Linux:
    ```bash
    sudo pacman -S bluez
    ```

2.  **Install Python Library:**
    The script uses the `pexpect` library to automate the interactive `bluetoothctl` shell.

    ```bash
    pip install pexpect
    ```

## Usage Guide

### 1. Find Your Speaker's MAC Address

You need the unique MAC address of your Bluetooth speaker.

1.  Open a terminal.
2.  Start the `bluetoothctl` utility:
    ```bash
    sudo bluetoothctl
    ```
3.  Turn on scanning:
    ```bash
    [bluetooth]# scan on
    ```
4.  Look for your speaker in the list of discovered devices. Note the address next to its name (e.g., `Device AA:BB:CC:DD:EE:FF JBL Flip 6`).
5.  Once you have the address, turn scanning off and exit:
    ```bash
    [bluetooth]# scan off
    [bluetooth]# exit
    ```

### 2. Configure the Script

1.  Open the Python script (`speaker_control.py` or whatever you named it).
2.  Find the `CONFIGURATION` section at the top.
3.  Replace the placeholder MAC address with your speaker's actual address:

    ```python
    # --- CONFIGURATION ---
    # The MAC address of the Bluetooth speaker you want to control.
    SPEAKER_MAC = "AA:BB:CC:DD:EE:FF" # <--- CHANGE THIS
    ```

### 3. Run the Script

Execute the script from your terminal using `sudo`:

```bash
sudo python speaker_control.py
```

The script will then print its progress as it attempts to pair, connect, and if necessary, force a disconnection.

## What to Expect

*   **Success:** If successful, you will see a `Connection successful` message, and your computer's audio should be routed to the speaker.
*   **Failure:** If it fails, it could be due to several reasons:
    *   The speaker is out of range.
    *   The MAC address is incorrect.
    *   The speaker's firmware is resilient to connection flooding attacks.
    *   Your system's Bluetooth adapter is disabled or has issues.

## Troubleshooting

*   **`pexpect` not found:** Make sure you installed it with `pip install pexpect`.
*   **Permission Denied:** You must run the script with `sudo`. The command is `sudo python your_script_name.py`.
*   **`bluetoothctl: command not found`:** You have not installed the BlueZ tools. See the "Installation Steps" section.
*   **Script hangs or times out:** Sometimes the Bluetooth service can get stuck. Try restarting it with `sudo systemctl restart bluetooth` and then run the script again.

## Platform Limitations

This script is **Linux-only**. The methods used are specific to the `bluetoothctl` command-line tool and the BlueZ stack.

*   **Windows:** Would require using the `pywin32` library to call the complex Windows Bluetooth APIs, which is a much more difficult task.
*   **macOS:** Is heavily locked down and does not provide easy command-line access for this type of aggressive connection management.

## License

This project is provided as-is for educational purposes. Use responsibly.

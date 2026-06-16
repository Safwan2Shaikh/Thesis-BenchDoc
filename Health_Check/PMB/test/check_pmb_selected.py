import subprocess
import time
import sys

# --- Configuration ---
PMB_CONTROL_SCRIPT = "ds2824_control.py"
# The specific relays and their ON/OFF commands for the sequence.
# Each entry is (relay_number, delay_after_on).
# The script will format the relay number to "SR_X" or "SR_XX" as needed.
RELAY_SEQUENCE = [
    (1, 3),  # Will become SR_1_on / SR_1_off
    (4, 3),  # Will become SR_4_on / SR_4_off
    (15, 3)  # Will become SR_15_on / SR_15_off
]

# --- Helper Function ---

def get_full_relay_command_name(relay_number):
    """
    Formats the relay number into the expected command argument format (e.g., "SR_1", "SR_15").
    """
    return f"SR_{relay_number}"

def run_pmb_command(command_arg):
    """
    Executes the PMB_control.py script with the given command argument.
    Returns True on success, False on failure.
    """
    try:
        print(f"  Executing: python {PMB_CONTROL_SCRIPT} {command_arg}")
        result = subprocess.run(
            ["python", PMB_CONTROL_SCRIPT, command_arg],
            capture_output=True,
            text=True,
            check=True # Raise an exception if the command returns a non-zero exit code
        )
        # print("  Script Output (stdout):\n" + result.stdout) # Uncomment to see script's stdout
        if result.stderr:
            print("  Script Error (stderr):\n" + result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: Command failed for '{command_arg}'. Exit Code: {e.returncode}")
        print(f"  Stdout: {e.stdout}")
        print(f"  Stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"  CRITICAL ERROR: '{PMB_CONTROL_SCRIPT}' not found. Make sure it's in the same directory or in PATH.")
        print("  Please ensure 'python' is also correctly configured in your system's PATH.")
        sys.exit(1) # Exit immediately as we can't control anything
    except Exception as e:
        print(f"  An unexpected error occurred while running command '{command_arg}': {e}")
        return False

# --- Main Test Procedure ---

def main():
    print("--------------------------------------------------")
    print("        PMB Relay Control Sequence Started        ")
    print("--------------------------------------------------")
    print(f"Using '{PMB_CONTROL_SCRIPT}' for relay control.")
    
    # List the relays as they will be commanded
    commanded_relays = [get_full_relay_command_name(r[0]) for r in RELAY_SEQUENCE]
    print(f"Executing sequence for relays: {', '.join(commanded_relays)}")
    print("\n")

    # Initial check that the control script exists
    try:
        # Just try to run it without arguments to see if it's found
        subprocess.run(["python", PMB_CONTROL_SCRIPT], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(f"CRITICAL ERROR: '{PMB_CONTROL_SCRIPT}' not found. Make sure it's in the same directory or in PATH.")
        print("Please ensure 'python' is also correctly configured in your system's PATH.")
        sys.exit(1)

    print("--- Starting Relay Sequence ---")
    sequence_success = True

    for i, (relay_number, delay_time) in enumerate(RELAY_SEQUENCE):
        # Format the relay name to match "SR_X" or "SR_XX" convention
        full_relay_name = get_full_relay_command_name(relay_number)

        print(f"\n--- Step {i+1}: Controlling Relay {full_relay_name} ---")

        # Turn ON
        print(f"Turning ON {full_relay_name}...")
        if not run_pmb_command(f"{full_relay_name}_on"):
            print(f"ERROR: Failed to turn ON {full_relay_name}. Stopping sequence.")
            sequence_success = False
            break # Exit the loop if a command fails

        print(f"Waiting {delay_time} seconds...")
        time.sleep(delay_time)

        # Turn OFF
        print(f"Turning OFF {full_relay_name}...")
        if not run_pmb_command(f"{full_relay_name}_off"):
            print(f"ERROR: Failed to turn OFF {full_relay_name}. Stopping sequence.")
            sequence_success = False
            break # Exit the loop if a command fails

    print("\n--------------------------------------------------")
    print("               PMB Sequence Summary               ")
    print("--------------------------------------------------")
    if sequence_success:
        print("All relay commands in the sequence executed successfully.")
    else:
        print("The relay sequence was interrupted due to a command failure.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
    
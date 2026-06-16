import serial
import time
import struct

COM_PORT = 'COM3'
BAUD_RATE = 115200
PARITY = serial.PARITY_ODD # 'odd' parity as per doc
STOPBITS = serial.STOPBITS_ONE
TIMEOUT = 0.5 # Seconds for read timeout

# Initialize nominal values (will be updated after querying device info)
NOMINAL_VOLTAGE = 0.0
NOMINAL_CURRENT = 0.0

# --- Serial Port Setup ---
try:
    ser = serial.Serial(
        port=COM_PORT,
        baudrate=BAUD_RATE,
        parity=PARITY,
        stopbits=STOPBITS,
        timeout=TIMEOUT
    )
    print(f"Connected to {COM_PORT}")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

# --- Helper Functions ---

def calculate_checksum(data_bytes_without_checksum):
    """Calculates the 2-byte checksum for the telegram."""
    checksum_val = sum(data_bytes_without_checksum)
    # Checksum is two bytes, high byte first
    return bytes([(checksum_val >> 8) & 0xFF, checksum_val & 0xFF])

def create_telegram(is_query: bool, expected_response_data_len: int,
                    device_node: int, object_id: int, data_field: bytes = b''):
    """
    Constructs a binary telegram for PC->Device communication.
    :param is_query: True for a query command, False for a send data command.
    :param expected_response_data_len: Expected length of the DATA_FIELD in bytes in the *response*.
                                       Used for SD bits 0-3 (expected_response_data_len - 1).
                                       If `is_query` is False, this determines the data_field length of the *command*.
    :param device_node: 0 for Output 1 / Single model, 1 for Output 2 (Triple model).
    :param object_id: The object ID (e.g., 0x00 for Device Type).
    :param data_field: The actual data bytes to send (empty for queries).
    :return: A complete telegram as bytes.
    """
    
    # SD Byte construction
    sd_bits_data_length = (expected_response_data_len - 1) & 0x0F 
    
    sd_bit_direction = 1 << 4 # Bit 4 (1 for PC->Device)
    sd_bit_cast_type = 1 << 5 # Bit 5 (1 for sending/querying from PC)

    if is_query:
        transmission_type = 0b01 # Query data (bits 6+7 = 01)
    else:
        transmission_type = 0b11 # Send data (bits 6+7 = 11)
        sd_bits_data_length = (len(data_field) - 1) & 0x0F # For send, use command's data length

    sd_bits_transmission_type = transmission_type << 6 # Bits 6+7

    sd = sd_bits_data_length | sd_bit_direction | sd_bit_cast_type | sd_bits_transmission_type
    
    # Telegram without checksum
    telegram_parts = bytes([sd, device_node, object_id]) + data_field
    
    checksum = calculate_checksum(telegram_parts)
    return telegram_parts + checksum

def send_and_receive_binary(command_bytes: bytes, expected_response_total_len: int):
    """Sends a binary command and reads the expected response."""
    print(f"Sending: {command_bytes.hex().upper()}")
    ser.write(command_bytes)
    time.sleep(0.05) # Minimum latency as per doc

    response = ser.read(expected_response_total_len)
    if not response:
        print("No response received within timeout.")
        return None
    print(f"Received: {response.hex().upper()}")
    return response

# --- Functions for Reading Device Data ---

def get_global_device_info():
    """Queries and prints global device information like type, serial, nominals."""
    global NOMINAL_VOLTAGE, NOMINAL_CURRENT # Declare intention to modify global vars
    
    print("\n--- Getting Global Device Information (DN 0x00) ---")

    # For global device info, always use DN 0x00
    global_dn = 0x00 

    # Object 0x00: Device Type (ro, string, 16 bytes)
    # Total response: 1(SD) + 1(DN) + 1(OBJ) + 16(DATA) + 2(CS) = 21 bytes.
    cmd_dev_type = create_telegram(is_query=True, expected_response_data_len=16, device_node=global_dn, object_id=0x00)
    response = send_and_receive_binary(cmd_dev_type, 21)
    
    # --- DEBUGGING START ---
    print(f"  DEBUG: Object 0x00 check for response: {response.hex() if response else 'None'}")
    if response:
        print(f"  DEBUG:   len(response)={len(response)} == 21: {len(response) == 21}")
        print(f"  DEBUG:   (response[0] & 0xC0)={response[0] & 0xC0:02X} == 0x80: {(response[0] & 0xC0) == 0x80}")
        print(f"  DEBUG:   response[2]={response[2]:02X} == 0x00: {response[2] == 0x00}")
    # --- DEBUGGING END ---

    if response and len(response) == 21 and (response[0] & 0xC0) == 0x80 and response[2] == 0x00:
        calculated_cs = calculate_checksum(response[:-2])
        if calculated_cs == response[-2:]:
            device_type = response[3:19].decode('ascii', errors='ignore').strip('\x00')
            print(f"  Device Type (Model): {device_type}")
        else:
            print(f"  Checksum mismatch for Device Type response. Expected {calculated_cs.hex()}, got {response[-2:].hex()}")
    else:
        print("  Failed to get Device Type or unexpected response format.")

    # Object 0x01: Device Serial Number (ro, string, 16 bytes)
    # Total response: 1(SD) + 1(DN) + 1(OBJ) + 16(DATA) + 2(CS) = 21 bytes.
    cmd_dev_serial = create_telegram(is_query=True, expected_response_data_len=16, device_node=global_dn, object_id=0x01)
    response = send_and_receive_binary(cmd_dev_serial, 21)
    
    # --- DEBUGGING START ---
    print(f"  DEBUG: Object 0x01 check for response: {response.hex() if response else 'None'}")
    if response:
        print(f"  DEBUG:   len(response)={len(response)} == 21: {len(response) == 21}")
        print(f"  DEBUG:   (response[0] & 0xC0)={response[0] & 0xC0:02X} == 0x80: {(response[0] & 0xC0) == 0x80}")
        print(f"  DEBUG:   response[2]={response[2]:02X} == 0x01: {response[2] == 0x01}")
    # --- DEBUGGING END ---

    if response and len(response) == 21 and (response[0] & 0xC0) == 0x80 and response[2] == 0x01:
        calculated_cs = calculate_checksum(response[:-2])
        if calculated_cs == response[-2:]:
            device_serial = response[3:19].decode('ascii', errors='ignore').strip('\x00')
            print(f"  Device Serial Number: {device_serial}")
        else:
            print(f"  Checksum mismatch for Serial Number response. Expected {calculated_cs.hex()}, got {response[-2:].hex()}")
    else:
        print("  Failed to get Device Serial Number or unexpected response format.")

    # Object 0x02: Nominal Voltage (ro, float, 4 bytes)
    # Total response: 1(SD) + 1(DN) + 1(OBJ) + 4(DATA) + 2(CS) = 9 bytes.
    cmd_nom_volt = create_telegram(is_query=True, expected_response_data_len=4, device_node=global_dn, object_id=0x02)
    response = send_and_receive_binary(cmd_nom_volt, 9)
    
    if response and len(response) == 9 and (response[0] & 0xC0) == 0x80 and response[2] == 0x02:
        calculated_cs = calculate_checksum(response[:-2])
        if calculated_cs == response[-2:]:
            nominal_voltage_val = struct.unpack('>f', response[3:7])[0] # >f for big-endian float
            print(f"  Nominal Voltage: {nominal_voltage_val:.2f}V")
            NOMINAL_VOLTAGE = nominal_voltage_val
        else:
            print(f"  Checksum mismatch for Nominal Voltage response. Expected {calculated_cs.hex()}, got {response[-2:].hex()}")
    else:
        print("  Failed to get Nominal Voltage or unexpected response format.")

    # Object 0x03: Nominal Current (ro, float, 4 bytes)
    # Total response: 1(SD) + 1(DN) + 1(OBJ) + 4(DATA) + 2(CS) = 9 bytes.
    cmd_nom_curr = create_telegram(is_query=True, expected_response_data_len=4, device_node=global_dn, object_id=0x03)
    response = send_and_receive_binary(cmd_nom_curr, 9)
    
    if response and len(response) == 9 and (response[0] & 0xC0) == 0x80 and response[2] == 0x03:
        calculated_cs = calculate_checksum(response[:-2])
        if calculated_cs == response[-2:]:
            nominal_current_val = struct.unpack('>f', response[3:7])[0]
            print(f"  Nominal Current: {nominal_current_val:.2f}A")
            NOMINAL_CURRENT = nominal_current_val
        else:
            print(f"  Checksum mismatch for Nominal Current response. Expected {calculated_cs.hex()}, got {response[-2:].hex()}")
    else:
        print("  Failed to get Nominal Current or unexpected response format.")


def read_actual_values(output_node: int):
    """Reads actual voltage and current from a given output node."""
    print(f"\n--- Reading Actual Values for Output {output_node + 1} (Device Node {output_node}) ---")

    if NOMINAL_VOLTAGE == 0.0 or NOMINAL_CURRENT == 0.0:
        print("  Warning: Nominal Voltage/Current not set. Cannot convert percentage to actual values.")
        print("  Please ensure get_global_device_info() runs successfully first.")
        return None

    # Object 0x47 (71): Status + Actual values. Returns 6 bytes of data.
    # Total response: 1(SD) + 1(DN) + 1(OBJ) + 6(DATA) + 2(CS) = 11 bytes.
    cmd_telegram = create_telegram(is_query=True, expected_response_data_len=6, device_node=output_node, object_id=0x47)
    
    response = send_and_receive_binary(cmd_telegram, 11)
    
    if response and len(response) == 11 and (response[0] & 0xC0) == 0x80 and response[2] == 0x47:
        calculated_cs = calculate_checksum(response[:-2])
        if calculated_cs == response[-2:]:
            status0 = response[3]
            status1 = response[4]
            voltage_percent = int.from_bytes(response[5:7], byteorder='big')
            current_percent = int.from_bytes(response[7:9], byteorder='big')

            actual_voltage = NOMINAL_VOLTAGE * voltage_percent / 25600
            actual_current = NOMINAL_CURRENT * current_percent / 25600

            print(f"  Raw Status Bytes: 0x{status0:02X}, 0x{status1:02X}")
            print(f"  Actual Voltage: {actual_voltage:.2f}V (Raw Percent: {voltage_percent})")
            print(f"  Actual Current: {actual_current:.2f}A (Raw Percent: {current_percent})")
            
            # Decoding for status1 (Byte 1 of Object 71 data, doc page 11)
            output_on = bool(status1 & 0b00000001) # Bit 0
            regulator_status_code = (status1 & 0b00000110) >> 1 # Bits 1+2 (00=CV, 10=CC)
            regulator_status_str = {0:'CV', 2:'CC'}.get(regulator_status_code, 'Unknown') # 00=CV, 10=CC
            tracking_active = bool(status1 & 0b00001000) # Bit 3
            ovp_active = bool(status1 & 0b00010000) # Bit 4
            ocp_active = bool(status1 & 0b00100000) # Bit 5
            opp_active = bool(status1 & 0b01000000) # Bit 6
            otp_active = bool(status1 & 0b10000000) # Bit 7

            print(f"  Decoded Status:")
            print(f"    Output ON: {output_on}")
            print(f"    Regulator State: {regulator_status_str}")
            print(f"    Tracking Active: {tracking_active}")
            print(f"    OVP Active: {ovp_active}")
            print(f"    OCP Active: {ocp_active}")
            print(f"    OPP Active: {opp_active}")
            print(f"    OTP Active: {otp_active}")

            return {
                "voltage": actual_voltage,
                "current": actual_current,
                "status0": status0,
                "status1": status1
            }
        else:
            print(f"  Checksum mismatch for Actual Values response. Expected {calculated_cs.hex()}, got {response[-2:].hex()}")
    else:
        # Check for generic error response (6 bytes: SD=0x80, DN=0x00, OBJ=0xFF, ErrorCode, CS)
        if response and len(response) == 6 and (response[0] & 0xC0) == 0x80 and response[2] == 0xFF:
            error_code = response[3]
            calculated_cs = calculate_checksum(response[:-2])
            if calculated_cs == response[-2:]:
                print(f"  Error: Received generic binary error 0x{error_code:02X} for Output {output_node + 1}.")
            else:
                print(f"  Checksum mismatch for Error response. Expected {calculated_cs.hex()}, got {response[-2:].hex()}")
        else:
            print(f"  Failed to read actual values for Output {output_node + 1} or unexpected response format.")
        return None

# --- Main Execution ---
try:
    # 1. Get global device information once (e.g., Device Type, Serial No., Nominal Volts/Amps)
    get_global_device_info()

    # 2. Query individual output channels for their actual values
    # For a Triple model (like PS 1342-10B Triple), both DN 0 and DN 1 should be queryable.

    # Output Channel 1 (Device Node 0)
    read_actual_values(output_node=0)

    # Output Channel 2 (Device Node 1)
    read_actual_values(output_node=1)


except Exception as e:
    print(f"\nAn unhandled error occurred: {e}")
finally:
    if ser.is_open:
        ser.close()
        print("\nSerial port closed.")

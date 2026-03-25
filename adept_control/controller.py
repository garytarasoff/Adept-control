import serial
import time
import logging

class AdeptController:
    """Manages the physical RS-232 serial connection to the Adept robot."""

    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.logger = logging.getLogger(__name__)
        self.on_send = None  # Protocol callback for monitoring sent commands

    def connect(self):
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.logger.info(f"Connected to {self.port} at {self.baudrate} baud.")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.logger.info("Disconnected.")

    def send_command(self, cmd_string):
        if self.serial_connection and self.serial_connection.is_open:
            # V+ typically expects a carriage return
            full_cmd = f"{cmd_string}\r\n".encode('ascii')
            self.serial_connection.write(full_cmd)
            self.logger.debug(f"Sent: {cmd_string}")
            if self.on_send:
                self.on_send(cmd_string)
        else:
            self.logger.warning("Attempted to send command without an active connection.")

    def read_response(self):
        if self.serial_connection and self.serial_connection.is_open:
            response = self.serial_connection.readlines()
            decoded = [line.decode('ascii', errors='replace').strip() for line in response]
            if decoded:
                self.logger.debug(f"Received: {decoded}")
            return decoded
        return []

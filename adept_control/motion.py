class RobotMotion:
    """Translates Python function calls into V+ ASCII DO commands."""

    def __init__(self, controller):
        self.controller = controller

    def _do(self, command):
        """Prepends DO and sends the command."""
        self.controller.send_command(f"DO {command}")

    def calibrate(self):
        """Initializes the robot positioning system."""
        self._do("CALIBRATE")

    def enable_power(self, enable=True):
        """Enables or disables high power."""
        state = "ENABLE" if enable else "DISABLE"
        self._do(f"{state} POWER")

    def auto_power_off(self, enable):
        """Enables or disables the AUTO.POWER.OFF system switch."""
        state = "ENABLE" if enable else "DISABLE"
        self._do(f"{state} AUTO.POWER.OFF")

    def dry_run(self, enable):
        """Places the controller into dry-run mode."""
        state = "ENABLE" if enable else "DISABLE"
        self._do(f"{state} DRY.RUN")

    def align(self):
        """Aligns the robot tool Z axis with the nearest world axis."""
        self._do("ALIGN")

    def base(self, x_shift=0, y_shift=0, z_shift=0, z_rotation=0):
        """Translates and rotates the World reference frame."""
        self._do(f"BASE {x_shift}, {y_shift}, {z_shift}, {z_rotation}")

    def move_to(self, location_name):
        """Initiates motion to a specified position."""
        self._do(f"MOVE {location_name}")

    def move_straight(self, location_name):
        """Executes a straight-line path."""
        self._do(f"MOVES {location_name}")
        
    def approach(self, location_name, distance):
        """Starts a motion toward a location, offset by a distance along Z-axis."""
        self._do(f"APPRO {location_name}, {distance}")

    def depart(self, distance):
        """Starts a motion away from current location, offset along Z-axis."""
        self._do(f"DEPART {distance}")

    def drive(self, joint_num, value):
        """Moves an individual joint."""
        self._do(f"DRIVE {joint_num}, {value}")

    def ready(self):
        """Moves the robot into a standard, safe configuration."""
        self._do("READY")
        
    def set_speed(self, speed_percent):
        """Sets the nominal speed percentage."""
        self._do(f"SPEED {speed_percent}")

    def abort(self):
        """Aborts the current robot motion."""
        # PANIC is a monitor command.
        self.controller.send_command("PANIC")

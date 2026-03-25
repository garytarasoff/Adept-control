class TaskManager:
    """Handles the execution and monitoring of pre-written V+ programs and resource allocation."""

    def __init__(self, controller):
        self.controller = controller

    def execute_program(self, task_number, program_name):
        """Starts a V+ program on a specific task."""
        self.controller.send_command(f"EXECUTE {task_number} {program_name}")

    def load_program(self, file_name):
        """Loads a program from the active default disk drive."""
        # Note: LOAD is a Monitor Command, entered with no 'DO' prefix.
        self.controller.send_command(f"LOAD {file_name}")

    def set_default_drive(self, drive_path="A:\\"):
        r"""Sets the system's default path (e.g., A:\ for the primary floppy)."""
        self.controller.send_command(f"DEFAULT = {drive_path}")

    def abort_task(self, task_number):
        """Aborts a specific task."""
        self.controller.send_command(f"ABORT {task_number}")

    def panic(self):
        """Immediately aborts current motion but keeps high power enabled."""
        self.controller.send_command("PANIC")

    def attach(self, lun=0, mode=1):
        """Attaches a Logical Unit Number (LUN). Default 0 is the Robot."""
        self.controller.send_command(f"DO ATTACH ({lun}, {mode})")
        
    def detach(self, lun=0):
        """Detaches a Logical Unit Number (LUN)."""
        self.controller.send_command(f"DO DETACH ({lun})")

    def fset(self, port, baud, parity):
        """Configures a serial port, e.g., FSET (1) 9600, 'NONE'."""
        self.controller.send_command(f"DO FSET ({port}) {baud}, {parity}")

    def term_type(self, message):
        """Sends a TYPE command to the V+ terminal."""
        self.controller.send_command(f"DO TYPE {message}")

    def id(self):
        """Display information identifying the configuration of the current system."""
        self.controller.send_command("ID")

    def status(self):
        """View the current status of the system."""
        self.controller.send_command("STATUS")

    def where(self):
        """Prints the manipulator arm position."""
        self.controller.send_command("WHERE")

    def signal(self, signal_num, state):
        """Turns on or off external binary output signals."""
        s = signal_num if state else -signal_num
        self.controller.send_command(f"DO SIGNAL {s}")

    def speed(self, level):
        """Sets the monitor speed of the controller."""
        self.controller.send_command(f"SPEED {level}")

# Adept Robot V+ Control (PyQt6)

A modern, Python-based GUI application designed to interface with and control Adept robot arms using the legacy V+ Control Architecture.

This project abstracts the low-level RS-232 serial communication and V+ syntax into an intuitive graphical interface, allowing operators to execute motion commands, manage system resources, and load programs directly from their modern PC.

## Features

- **Robust Serial Communication (`AdeptController`)**: Manages the underlying RS-232 connection to the Adept controller, providing asynchronous logging and error handling.
- **V+ Motion Wrappers (`RobotMotion`)**: High-level Python methods translated directly into V+ `DO` commands, supporting:
  - System Initialization (`CALIBRATE`)
  - Power States (`ENABLE POWER`, `DISABLE POWER`, `AUTO.POWER.OFF`)
  - Movement (`MOVE`, `MOVES`, `APPRO`, `DEPART`, `READY`, `PANIC`)
  - Advanced Settings (`DRY.RUN`, `ALIGN`, `BASE`)
- **Task & Storage Management (`TaskManager`)**: Provides explicit control over V+ background tasks and disk loading:
  - Resource Allocation (`ATTACH`, `DETACH`, `LUN`)
  - Serial Configuration (`FSET`)
  - System Diagnostics (`ID`, `STATUS`, `WHERE`, `SIGNAL`, `SPEED`)
  - Floppy Disk Interactions (`DEFAULT`, `LOAD`, `EXECUTE`)
- **PyQt6 Interface (`RobotGUI`)**: A multi-tabbed interface featuring:
  - **Main**: System Initialization, Power status, Calibration, and Resource Management.
  - **Movement**: Safe coordinate entry, READY staging, and PANIC emergency stops.
  - **Programs**: Complete workflow logic for loading V+ files off the controller's `.A:\` or `.C:\` drives and executing them to tasks.
  - **Terminal (Persistent)**: Split view of TX (sent commands) and RX (received responses) across all logic layers.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/garytarasoff/Adept-control.git
   cd Adept-control
   ```

2. Create and activate a Virtual Environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Connect your workstation to the Adept Controller using an RS-232 to USB adapter.
2. Launch the application:
   ```bash
   python main.py
   ```
3. Use the **Connection** panel at the top to select the correct COM port and hit connect.
4. Navigate through the tabs to initiate calibration, manage power, and send movement commands. All outgoing commands and incoming responses will be constantly logged in the bottom persistent terminal.

## Architecture Guidelines

This system follows strict adherence to the **Adept V+ Control Architecture**:
- Hardware mappings abstract properly to Logical Units (LUNs, specifically 0 for robot motion).
- The `FSET` instruction is specifically designed to execute *after* attachment to prevent state overriding.
- `PANIC` is implemented as a direct monitor command, halting motion while preserving the high-power state to allow for process recovery without hardware restart.

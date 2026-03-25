import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QGroupBox, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QGraphicsView, QGraphicsScene,
    QSplitter, QCheckBox, QComboBox
)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, Qt

class SignalEmitter(QObject):
    log_tx_signal = pyqtSignal(str)
    log_rx_signal = pyqtSignal(str)
    system_signal = pyqtSignal(str)

class RobotGUI(QMainWindow):
    """The main application window for controlling the Adept robot using PyQt6."""

    def __init__(self, controller, motion, task_manager):
        super().__init__()
        self.setWindowTitle("Adept Robot Control (PyQt6)")
        self.resize(900, 700)

        self.controller = controller
        self.motion = motion
        self.task_manager = task_manager

        # Hook the controller's outgoing commands into the GUI terminal
        self.controller.on_send = lambda cmd: self.emitter.log_tx_signal.emit(f"> {cmd}")

        self.emitter = SignalEmitter()
        self.emitter.log_tx_signal.connect(self.log_tx)
        self.emitter.log_rx_signal.connect(self.log_rx)
        self.emitter.system_signal.connect(self.log_system)

        self.create_widgets()

        # Polling timer for serial responses
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_serial)
        self.poll_timer.start(100)  # Polling every 100 ms

    def create_widgets(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 1. Connection Frame (Top) ---
        conn_group = QGroupBox("Connection")
        conn_layout = QHBoxLayout()
        
        conn_layout.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.port_combo.setFixedWidth(100)
        conn_layout.addWidget(self.port_combo)

        self.btn_scan = QPushButton("Scan")
        self.btn_scan.clicked.connect(self.scan_ports)
        conn_layout.addWidget(self.btn_scan)
        
        # Populate initial port list
        self.scan_ports()

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_serial)
        conn_layout.addWidget(self.btn_connect)

        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.clicked.connect(self.disconnect_serial)
        conn_layout.addWidget(self.btn_disconnect)

        conn_layout.addStretch()
        conn_group.setLayout(conn_layout)
        main_layout.addWidget(conn_group)

        # --- 2. Tabbed Interface (Middle) ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Main (renamed from Control & Operations)
        self.tab_main = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.tab_main, "Main")

        # Tab 2: Movement
        self.tab_movement = QWidget()
        self.setup_movement_tab()
        self.tabs.addTab(self.tab_movement, "Movement")

        # Tab 3: Programs
        self.tab_programs = QWidget()
        self.setup_programs_tab()
        self.tabs.addTab(self.tab_programs, "Programs")

        # Tab 4: Virtual Diagram
        self.tab_diagram = QWidget()
        self.setup_diagram_tab()
        self.tabs.addTab(self.tab_diagram, "Virtual Diagram")

        # --- 3. Terminal Area (Bottom, Always Visible) ---
        term_group = QGroupBox("Terminal (TX / RX)")
        term_layout = QVBoxLayout()
        term_group.setLayout(term_layout)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # TX Side (Left)
        tx_widget = QWidget()
        tx_layout = QVBoxLayout(tx_widget)
        tx_layout.setContentsMargins(0, 0, 5, 0)
        
        tx_layout.addWidget(QLabel("TX (Sent commands & System logs):"))
        self.txt_tx = QTextEdit()
        self.txt_tx.setReadOnly(True)
        self.txt_tx.setStyleSheet("background-color: black; color: white; font-family: Consolas, monospace;")
        tx_layout.addWidget(self.txt_tx)

        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("Command:"))
        self.cmd_entry = QLineEdit()
        self.cmd_entry.returnPressed.connect(self.send_manual_cmd)
        cmd_layout.addWidget(self.cmd_entry)

        btn_send = QPushButton("Send")
        btn_send.clicked.connect(self.send_manual_cmd)
        cmd_layout.addWidget(btn_send)
        
        tx_layout.addLayout(cmd_layout)
        
        # RX Side (Right)
        rx_widget = QWidget()
        rx_layout = QVBoxLayout(rx_widget)
        rx_layout.setContentsMargins(5, 0, 0, 0)
        
        rx_layout.addWidget(QLabel("RX (Received data):"))
        self.txt_rx = QTextEdit()
        self.txt_rx.setReadOnly(True)
        self.txt_rx.setStyleSheet("background-color: black; color: white; font-family: Consolas, monospace;") 
        rx_layout.addWidget(self.txt_rx)

        splitter.addWidget(tx_widget)
        splitter.addWidget(rx_widget)
        
        term_layout.addWidget(splitter)
        main_layout.addWidget(term_group)
        
        # Set proportions: tabs get 2/3 of space, terminal gets 1/3
        main_layout.setStretchFactor(self.tabs, 2)
        main_layout.setStretchFactor(term_group, 1)

    def setup_main_tab(self):
        layout = QVBoxLayout(self.tab_main)
        
        # --- Initialization & Power Group ---
        init_group = QGroupBox("System Initialization & Power")
        init_layout = QHBoxLayout()
        
        btn_power = QPushButton("Enable Power")
        btn_power.clicked.connect(lambda: self.motion.enable_power(True))
        init_layout.addWidget(btn_power)

        btn_power_off = QPushButton("Disable Power")
        btn_power_off.clicked.connect(lambda: self.motion.enable_power(False))
        init_layout.addWidget(btn_power_off)

        btn_calibrate = QPushButton("CALIBRATE")
        btn_calibrate.clicked.connect(self.motion.calibrate)
        init_layout.addWidget(btn_calibrate)

        self.chk_power = QCheckBox("AUTO.POWER.OFF enabled")
        self.chk_power.toggled.connect(lambda checked: self.motion.auto_power_off(checked))
        init_layout.addWidget(self.chk_power)
        
        init_layout.addStretch()
        init_group.setLayout(init_layout)
        layout.addWidget(init_group)

        # --- Resource Management Group ---
        res_group = QGroupBox("Resource Management (LUNs & Serial)")
        res_layout = QHBoxLayout()

        btn_attach = QPushButton("ATTACH (LUN 0)")
        btn_attach.clicked.connect(lambda: self.task_manager.attach(0, 1))
        res_layout.addWidget(btn_attach)

        btn_detach = QPushButton("DETACH (LUN 0)")
        btn_detach.clicked.connect(lambda: self.task_manager.detach(0))
        res_layout.addWidget(btn_detach)

        btn_fset = QPushButton("Default FSET")
        btn_fset.clicked.connect(lambda: self.task_manager.fset(1, 9600, "'NONE'"))
        res_layout.addWidget(btn_fset)

        res_layout.addStretch()
        res_group.setLayout(res_layout)
        layout.addWidget(res_group)

        # --- System Information Group ---
        info_group = QGroupBox("System Information")
        info_layout = QHBoxLayout()

        btn_id = QPushButton("ID")
        btn_id.clicked.connect(self.task_manager.id)
        info_layout.addWidget(btn_id)

        btn_status = QPushButton("STATUS")
        btn_status.clicked.connect(self.task_manager.status)
        info_layout.addWidget(btn_status)

        btn_where = QPushButton("WHERE")
        btn_where.clicked.connect(self.task_manager.where)
        info_layout.addWidget(btn_where)

        info_layout.addStretch()
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # --- Advanced Settings Group ---
        adv_group = QGroupBox("Advanced Settings")
        adv_layout = QHBoxLayout()

        self.chk_dry_run = QCheckBox("DRY.RUN mode")
        self.chk_dry_run.toggled.connect(lambda checked: self.motion.dry_run(checked))
        adv_layout.addWidget(self.chk_dry_run)

        btn_align = QPushButton("ALIGN Tool")
        btn_align.clicked.connect(self.motion.align)
        adv_layout.addWidget(btn_align)

        adv_layout.addStretch()
        adv_group.setLayout(adv_layout)
        layout.addWidget(adv_group)

        layout.addStretch()

    def setup_movement_tab(self):
        layout = QVBoxLayout(self.tab_movement)
        
        # --- Base Motion Group ---
        mot_group = QGroupBox("Motion Commands")
        mot_layout = QVBoxLayout()

        btn_ready = QPushButton("READY")
        btn_ready.clicked.connect(self.motion.ready)
        mot_layout.addWidget(btn_ready)

        btn_panic = QPushButton("PANIC (Emergency Stop)")
        btn_panic.clicked.connect(self.motion.abort)
        btn_panic.setStyleSheet("background-color: red; color: white; font-weight: bold; height: 50px;")
        mot_layout.addWidget(btn_panic)

        mot_group.setLayout(mot_layout)
        layout.addWidget(mot_group)
        
        # Simple manual MOVE/APPRO entry
        manual_group = QGroupBox("Manual Motion")
        manual_layout = QHBoxLayout()
        
        manual_layout.addWidget(QLabel("Location:"))
        self.loc_entry = QLineEdit("point1")
        manual_layout.addWidget(self.loc_entry)
        
        btn_move = QPushButton("MOVE")
        btn_move.clicked.connect(lambda: self.motion.move_to(self.loc_entry.text()))
        manual_layout.addWidget(btn_move)
        
        btn_moves = QPushButton("MOVES")
        btn_moves.clicked.connect(lambda: self.motion.move_straight(self.loc_entry.text()))
        manual_layout.addWidget(btn_moves)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)

        layout.addStretch()

    def setup_programs_tab(self):
        layout = QVBoxLayout(self.tab_programs)

        # --- Disk Navigation Group ---
        disk_group = QGroupBox("Disk Navigation & Loading")
        disk_layout = QVBoxLayout()
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Default Drive/Path:"))
        self.path_entry = QLineEdit("A:\\")
        path_layout.addWidget(self.path_entry)
        
        btn_path = QPushButton("Set Default Path")
        btn_path.clicked.connect(lambda: self.task_manager.set_default_drive(self.path_entry.text()))
        path_layout.addWidget(btn_path)
        disk_layout.addLayout(path_layout)

        load_layout = QHBoxLayout()
        load_layout.addWidget(QLabel("File Name:"))
        self.file_entry = QLineEdit()
        load_layout.addWidget(self.file_entry)
        
        btn_load = QPushButton("LOAD")
        btn_load.clicked.connect(lambda: self.task_manager.load_program(self.file_entry.text()))
        load_layout.addWidget(btn_load)
        disk_layout.addLayout(load_layout)

        disk_group.setLayout(disk_layout)
        layout.addWidget(disk_group)

        # --- Execution Group ---
        exec_group = QGroupBox("Task Execution")
        exec_layout = QVBoxLayout()

        task_layout = QHBoxLayout()
        task_layout.addWidget(QLabel("Task #:"))
        self.task_num_entry = QLineEdit("0")
        self.task_num_entry.setFixedWidth(50)
        task_layout.addWidget(self.task_num_entry)

        task_layout.addWidget(QLabel("Program Name:"))
        self.prog_entry = QLineEdit()
        task_layout.addWidget(self.prog_entry)

        btn_exec = QPushButton("EXECUTE")
        btn_exec.clicked.connect(lambda: self.task_manager.execute_program(self.task_num_entry.text(), self.prog_entry.text()))
        btn_exec.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        task_layout.addWidget(btn_exec)
        exec_layout.addLayout(task_layout)

        ctrl_layout = QHBoxLayout()
        btn_abort = QPushButton("ABORT Task")
        btn_abort.clicked.connect(lambda: self.task_manager.abort_task(self.task_num_entry.text()))
        btn_abort.setStyleSheet("background-color: orange; color: black;")
        ctrl_layout.addWidget(btn_abort)

        btn_prog_status = QPushButton("Task STATUS")
        btn_prog_status.clicked.connect(self.task_manager.status)
        ctrl_layout.addWidget(btn_prog_status)
        exec_layout.addLayout(ctrl_layout)

        exec_group.setLayout(exec_layout)
        layout.addWidget(exec_group)

        layout.addStretch()

    def setup_diagram_tab(self):
        layout = QVBoxLayout(self.tab_diagram)
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        
        # Placeholder for diagram
        self.scene.addText("Virtual Robot Diagram Area")
        self.scene.addRect(0, 50, 100, 100) # Simple box placeholder

        layout.addWidget(self.view)

    def scan_ports(self):
        import serial.tools.list_ports
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.device)
        if not ports:
            self.port_combo.addItem("COM1") # Fallback if no ports found
            
    def connect_serial(self):
        self.controller.port = self.port_combo.currentText()
        if self.controller.connect():
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.emitter.system_signal.emit("System: Connected.")
        else:
            self.emitter.system_signal.emit("System: Connection failed.")

    def disconnect_serial(self):
        self.controller.disconnect()
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.emitter.system_signal.emit("System: Disconnected.")

    def send_manual_cmd(self):
        cmd = self.cmd_entry.text().strip()
        if cmd:
            self.controller.send_command(cmd)
            self.cmd_entry.clear()

    def log_tx(self, text):
        self.txt_tx.append(text)

    def log_rx(self, text):
        self.txt_rx.append(text)

    def log_system(self, text):
        # System messages go to both sides to indicate events
        self.txt_tx.append(f"<span style='color:yellow;'>{text}</span>")
        self.txt_rx.append(f"<span style='color:yellow;'>{text}</span>")

    def poll_serial(self):
        responses = self.controller.read_response()
        for line in responses:
            if line:
                self.emitter.log_rx_signal.emit(f"< {line}")

    def closeEvent(self, event):
        self.poll_timer.stop()
        self.controller.disconnect()
        super().closeEvent(event)

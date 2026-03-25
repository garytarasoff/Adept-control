import sys
import logging
from PyQt6.QtWidgets import QApplication
from adept_control import AdeptController, RobotMotion, TaskManager, RobotGUI

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    # Initialize components
    controller = AdeptController(port="COM1")
    motion = RobotMotion(controller)
    task_manager = TaskManager(controller)
    
    # Start GUI
    app = QApplication(sys.argv)
    window = RobotGUI(controller, motion, task_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

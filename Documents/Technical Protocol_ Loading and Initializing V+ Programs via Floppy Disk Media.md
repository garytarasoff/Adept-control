### Technical Protocol: Loading and Initializing V+ Programs via Floppy Disk Media

#### 1\. Executive Overview of the V+ Operating System Interface

The V+ Operating System (Version 12.1+) is the central authority for all hardware interaction within the Adept MV Controller environment. Beyond its role as a high-level programming language, V+ functions as a real-time operating system that abstracts complex joint-servo and digital I/O interactions. Program management via floppy disk media is a mandatory skill for establishing system modularity and executing disaster recovery.Operators interact with the system via the  **Key Tronic Model 3417**  (Part \#16300-00220) programmer’s keyboard. This 101-key interface utilizes  **capacitive technology**  to ensure high reliability in industrial settings. Before entering commands, the engineer must map the physical hardware to the logical addresses recognized by the V+ kernel.

#### 2\. Hardware Mapping and Device Identification

V+ employs Logical Units (LUNs) to abstract physical hardware into software-accessible addresses. This abstraction is the primary mechanism for software portability across different Adept configurations. Assigning the correct LUN is the first step in ensuring the controller can communicate with the floppy disk drive.The system provides default device assignments for disk-based operations. LUNs 5 through 8 serve as the primary interfaces for disk media, while LUNs 17 through 19 provide extended support.

##### Default Device Mapping (Disk Operations)

Logical Unit (LUN),Default Device Name,Typical Mapping/Hardware  
5,DISK,Primary Floppy Drive (FLPY:)  
6-8,DISK,Secondary/Tertiary Disk Interfaces  
17-19,DISK,Extended Disk Interfaces  
When utilizing ATTACH or FOPEN commands, the operator must distinguish between specific device names:

* **"DISK"** : Points directly to the physical disk hardware.  
* **"SYSTEM"** : References the disk device, drive, and subdirectory path currently defined as the default.**Quick-Start Mapping Sequence:**  
1. Verify physical media is seated in the drive.  
2. Ensure no other task has attached the target LUN.  
3. Use the $DEFAULT string function to verify the current system pathing before attempting a load.

#### 3\. The Command Sequence for Media Navigation and Loading

Setting a default path is the primary defense against syntax-driven load failures during high-pressure system recoveries. Establishing the source drive before calling the file reduces the length of terminal strings and minimizes the risk of "Device not found" errors.

##### The DEFAULT Protocol

Set the system's default path to the floppy drive by entering the following at the monitor prompt:  
DEFAULT \= DISK\>

##### The LOAD Protocol

Once the default is established, the LOAD monitor command transfers the program from the physical media into the controller's active memory.  **Note:**  LOAD is a Monitor Command and must be entered at the system dot (.) prompt.  
.LOAD \[file\_name\]

**Operational Note:**  AUTOmatic variables (declared via the AUTO instruction) are created on the program stack and are not preserved by STORE or restored by LOAD. They exist only during active task execution.

#### 4\. Pre-Execution Initialization and Calibration

Movement under program control is impossible and unsafe until the positioning system is synchronized. The CALIBRATE instruction is the mandatory protocol for aligning the controller's internal software model with the robot's physical encoders.

##### The CALIBRATE Instruction

This instruction must be processed every time the system is booted from disk or power-cycled.  
.CALIBRATE

**Critical Safety Constraints:**

* **Dry Run Alert:**  If the DRY.RUN system switch is enabled, the CALIBRATE instruction will have no effect, as V+ is not communicating with the robot servos.  
* **Physical Motion:**  Execution triggers physical motion as the robot searches for joint zero-indexes.  
* **Hardstop Collision Risk:**  If a joint is positioned against a  **hardstop** , the calibration move may fail immediately. Ensure the robot is moved manually to a neutral position before executing.  
* **Calibration Status:**  Use the NOT.CALIBRATED parameter to check if the system requires a reset.

#### 5\. Program Execution and Task Management

Loading a program into memory does not activate it. The EXECUTE command transitions the code into an active "Task."

##### The EXECUTE Protocol

Initiate the program using the following syntax:  
.EXECUTE \[program\_name\]

**Task 0 Distinction:**  By default, this command activates  **Task 0** . Per the V+ standard,  **Program Task 0 automatically attaches Robot \#1.**  In multi-robot environments, any other task number (1-24) must use an explicit ATTACH instruction to gain control of the arm.

##### Operational Status Monitoring

Post-execution, use these diagnostic commands to evaluate program health:

* **STATUS** : Returns the current execution status of the application task.  
* **STATE** : Returns the robot system state (e.g., confirming "COMP" mode or identifying "Envelope Errors").

#### 6\. Operational Troubleshooting for Disk-to-Memory Transfers

Aggressive error-trapping is required to maintain system uptime. Failures during the load-and-start sequence typically stem from cabling noise or hardware misalignment.

##### Diagnostic Corrective Actions

V+ Error Message,"Corrective Action (""So What?"")"  
Motor Amplifier Fault,Check the Arm Power Cable. Ensure the  bare shield wire ground (AP-SHLD)  is secure to prevent noise. Inspect all 24 pins in the motor winding loop.  
No Zero Index,"Execute the  Encoder Activity Test  via the Manual Control Pendant. If values are static, perform a  JIB Swap Test  to isolate the Joint Interface Board."  
Envelope Error,"Check for physical obstructions. Perform the  100 Ohm Test  on encoder lines. If occurring during nulling, toggle AUTO.POWER.OFF to DISABLE."  
Illegal Digital Signal,"Ensure the program is not attempting to write to Signal 2032 (Brake Solenoid), which is read-only."  
Robot Not Attached,"Verify Task 0 is active. If using another task, ensure an ATTACH instruction preceded the first motion command."  
Adhering to this structured command sequence ensures the 100,000+ hour MTBF of the Key Tronic Model 3417 interface hardware is matched by the operational reliability of the software environment. Follow these protocols to maximize system availability and minimize recovery time.  

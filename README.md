# Energy Monitoring System – Bachelor Thesis

**Author:** Filip Novakovic  
**Supervisor:** Prof. Anthony Girardin, HEPIA Geneva  
**Date:** January 2025  

## Overview

This project was developed for a real boat ("Lammouche") to monitor electrical energy consumption and production. The goals were:

- Analyse existing data from an **eGauge datalogger** (15 channels, current transformers).
- Understand generator behaviour, consumption patterns, and thresholds.
- Build a **portable simulator** using a Raspberry Pi + CN0554 board to reproduce realistic electrical signals.
- Provide documented Python code for future students and engineers.

The simulator can generate voltage signals that mimic the boat’s electrical profile, enabling testing without the real hardware.

## Hardware Requirements

To run the simulator (optional – analysis scripts run on any PC):

- **Raspberry Pi 4** (or 3B+)
- **Analog Devices CN0554** "hat" (DAC/ADC board)
- **eGauge datalogger** (for full integration)
- Current transformers (simulated via voltage dividers)
- MicroSD card (16 GB minimum)

For data analysis only, you only need Python and the CSV files.

## Software & Dependencies

Install the required Python libraries:

bash
pip install -r requirements.txt
requirements.txt
text
numpy
pandas
matplotlib
scipy
adijupyter
For the Raspberry Pi + CN0554, you must use the Analog Devices Kuiper Linux image. See the official installation guide.

## Project Structure & Key Results
1. Data Analysis (threshold_analysis.py, density_analysis.py)
Threshold detection: Identified that the PORT generator activates when STBD generator reaches ~40 kW. STBD is the primary generator.

Gaussian density analysis: Showed typical power production at 40 kW, with a secondary mode at higher loads. Consumption is shifted 11 kW left, indicating an unmeasured constant consumer.

Daily patterns: Generators follow human activity (peaks at 10h, 18h-22h; minimum at night). Guest areas show waking hours (6-8h) and evening inactivity.

2. Hardware Simulator (cn0554_controller.py)
The script:

Connects to the CN0554 board via pyadi-iio library.

Sets DAC output voltages (0–5V range) to simulate current transformer signals.

Reads ADC inputs to verify the generated signals.

Can replay real power data from CSV files (intended for eGauge injection).

Current known bug: The main_test() loop that repeatedly changes DAC output causes a Broken Pipe (Errno 32) error after 1–2 iterations. The main_stable() function (fixed voltage) works correctly. This is documented in the code comments and thesis memo.

## How to Run
Data Analysis (on any computer)
bash
python threshold_analysis.py
python density_analysis.py
The density script includes an interactive mode: use up/down arrows to switch between PORT/STBD, left/right arrows to browse different electrical loads.

CN0554 Simulator (on Raspberry Pi with Kuiper OS)
Flash Kuiper Linux to the microSD card.

Boot the Raspberry Pi and connect the CN0554 hat.

Find the CN0554 URI:

bash
iio_info -s
Update uri = "ip:192.168.1.242" in cn0554_controller.py with your device’s IP.

Run the controller:

bash
python cn0554_controller.py
The script starts with main_stable() – sets all DAC outputs to 5V and reads ADC every 10 seconds.

To test with real data, switch to main_test() (note the bug).

## Known Issues & Troubleshooting
Error	Cause	Workaround
[Errno 110] Connection timeout	
Wrong URI or intermittent connection	Verify URI with iio_info -s. Reboot Raspberry Pi.

[Errno 13] Permission denied	
File or user permissions	Run chmod u+x yourfile.py or modify sudoers (see thesis memo).

[Errno 32] Broken Pipe	
IO management bug in pyadi-iio or CN0554 driver	Use main_stable() for demos. Future work: investigate driver reset between writes.
For detailed debugging steps, refer to the "Problèmes rencontrés" section in the thesis memo (page 37–38).

## Next Steps & Future Work
Resolve the Broken Pipe error to enable continuous data replay.

Build a portable suitcase with physical buttons to switch between real data and optimised scenarios.

Integrate the simulator with the eGauge datalogger using voltage dividers.

Add a simple GUI (Qt) to control the simulation.

## License
This project is open-source under the MIT License. Feel free to use and adapt for educational or research purposes.

## Contact
Filip Novakovic – filip-novakovic@hotmail.com
Thesis advisor: Prof. Anthony Girardin, HEPIA Geneva

For full details, please read the bachelor thesis memo (docs/thesis_memo.pdf).

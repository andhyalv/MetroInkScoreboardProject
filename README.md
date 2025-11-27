\# Metro Ink Splatoon Scoreboard Capture for in person events.

This project seeks to make it easier to capture stats for in person Splatoon events. As there is no native stat capturing or replay system built into the LAN functionality of the game, this solution for capturing stats was made.



This repository contains:

* A Flask server to connect the devices capturing in game scoreboards, and a central dashboard controlling all station devices
* Central Flask server to control all Raspberry Pi's script running.
* Screenshot uploading to Windows (Central) PC via SCP
* Scripts and dependencies for easy setup on new Pi systems.



\## Setup







1. Prepare Raspberry Pi: Install Pi OS, enable SSH.
   ```bash,sudo systemctl enable ssh
   sudo systemctl start ssh```
   
2. Connect to Travel Router (or other Private Network).
3. Update The System:
   ```bash,sudo apt update \&\& sudo apt upgrade -y
   sudo apt install python3-pip git -y```
4. Clone the Repository
5. Install the Python Dependencies
   ```bash, pip3 install -r requirements.txt```
6. Edit the Pi script (main.py) to set the Windows IP, username, and destination folder for screenshots: If not already done.
7. Configure Pi's to have static IP's and adjust them in the Dashboard.py script if needed.
8. Create SSH Connections from the Central Computer to the PI and share their public keys to allow for seamless communication.
9. Create Hostnames for the pi that match the station being used. E.g station-a
10. Navigate to the Repo Folder on the local machine.
11. Pip install -r requirements .txt
12. Once all dependencies and packages are installed, Static IP's known. Change the

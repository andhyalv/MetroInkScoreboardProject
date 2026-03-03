\# Metro Ink Splatoon Scoreboard Capture for in person events.

This project seeks to make it easier to capture stats for in person Splatoon events. As there is no native stat capturing or replay system built into the LAN functionality of the game, this solution for capturing stats was made.



This repository contains:
* A script to capture screenshots of scoreboards as they appear in game, then upload those screenshots to a central Host PC. 
* A Flask server to connect the devices capturing in game scoreboards, and a central dashboard controlling all station devices
* Central Flask server to control all Raspberry Pi's script running.
* Screenshot uploading to Windows (Central) PC via SCP
* Scripts and dependencies for easy setup on new Pi systems.



\## Central PC Setup
1. Ensure it can run SSH Server & has Public Keys. See Pi Setup Section for more info.
2. Install dependencies for Dashboard Python code.
```pip install flask paramiko requests scp```
3. Import Github repo.
4. Connect to Travel Router / Private Network and access the dashboard to modify IP Address Settings. Static IP's.
4. Adjust Station names, General Pi Username (used by all Pi's), Pi Static IP Addresses and Folder Destination in CentralDashboard.py
5. Run CentralDashboard.py, follow the ip to the dashboard.

\## Raspberry Pi Scoreboard Detection Setup

Prepare Raspberry Pi: 
First Time: Install Pi OS, enable SSH. Use your central PC's Public Key. 'id_ed25519.pub' found in /.ssh folder. If it doesn't exist, skip to
SSH Server Setup below.

After First Time/Updates: Mirror Original Pi SD to other Pi SD Cards.

Connect Wifi to Travel Router (or other Private Network).
Configure Pi's to have static IP's and adjust them in the Dashboard.py script if needed on Central PC.

SSH from Central (Windows) to Pi. IF your key is already established, skip to step 4.
1. Open Powershell and run

```Powershell, Get-Service sshd```

2\. If it says Service not found, install

```Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0```

```Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0```

3\. Start the SSH Server

```Start-Service sshd```

```Set-Service -Name sshd -StartupType Automatic```

4\. Generate SSH key on Windows if you don't have one.

```Powershell, ssh-keygen```

5\. Copy the public key from Windows to your PI OS IMage Setup.

SSH from Windows to Pi.

2. Update The System:

```sudo apt update && sudo apt upgrade -y```


```sudo apt install python3-venv python3-opencv v4l-utils -y```


3. Clone the Repository

```git clone "HTTP from GitHub repository"```

4. Install the Python Dependencies
Create a virtual environment

```python3 -m venv venv```

Activate it

```source venv/bin/activate```

 Now install packages
 sudo apt install python3-venv python3-opencv v4l-utils -y
 
 python3 -m venv venv
source venv/bin/activate
pip install opencv-python paramiko scp flask
```pip install -r requirements.txt```
```pip3 install flask paramiko scp opencv-python numpy```

5. Edit the config.json example file to set the Windows IP, username, and destination folder for screenshots and set it to config.json If not already done.
6. change the config.json script to match the id's of this station.


Run Central_dashboard.py from the Main PC and pi_server.py from the Pi. Test out if screen capture works through dashboard control without issue.
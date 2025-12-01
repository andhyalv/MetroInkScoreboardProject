\# Metro Ink Splatoon Scoreboard Capture for in person events.

This project seeks to make it easier to capture stats for in person Splatoon events. As there is no native stat capturing or replay system built into the LAN functionality of the game, this solution for capturing stats was made.



This repository contains:
* A script to capture screenshots of scoreboards as they appear in game, then upload those screenshots to a central Host PC. 
* A Flask server to connect the devices capturing in game scoreboards, and a central dashboard controlling all station devices
* Central Flask server to control all Raspberry Pi's script running.
* Screenshot uploading to Windows (Central) PC via SCP
* Scripts and dependencies for easy setup on new Pi systems.



\## Setup


1. Prepare Raspberry Pi: Install Pi OS, enable SSH.

```bash, sudo systemctl enable ssh sudo systemctl start ssh```
 If that doesn't work, do this and go to Interface.
```sudo raspi-config```
Check firewall status to make sure Pi isn't blocking SSH at port 22
```sudo ufw status verbose```
If it is, then run this.
```sudo ufw allow ssh```

Change the host name as well to match the station name.
```System Options  →  Hostname```

2. Connect to Travel Router (or other Private Network).
Configure Pi's to have static IP's and adjust them in the Dashboard.py script if needed on Central PC.

3. Connect via SSH from Central Device. 
```ssh username@IP```


4. Update The System:

```sudo apt update sudo apt upgrade -y sudo apt install python3-pip git -y```



5. Clone the Repository

```git clone "HTTP from GitHub repository"```

6. Install the Python Dependencies
Create a virtual environment

```python3 -m venv venv```

Activate it

```source venv/bin/activate```

 Now install packages
```pip install -r requirements.txt```
```pip3 install flask paramiko scp opencv-python numpy```

6. Edit the Pi script (main.py) to set the Windows IP, username, and destination folder for screenshots: If not already done.
7. change the config.json script to match the id's of this station.


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

5\. Copy your Windows key to each raspberry pi. Open Git Bash

```ssh-copy-id pi@192.168.8.xxx```

or 

```scp ~/.ssh/id_rsa.pub pi@192.168.8.xxx:/home/pi/```

9. On the Pi (Optional? It logged in without doing this.)

```mkdir -p ~/.ssh```

```cat ~/id_rsa.pub >> ~/.ssh/authorized_keys```

```chmod 600 ~/.ssh/authorized_keys```

```rm ~/id_rsa.pub```

Pi to Windows SSH:
1. Find Windows IP

```ipconfig```

2. make .ssh folder if not already there.

```mkdir $env:USERPROFILE\.ssh```

3. Copy pi Keys to windows (on pi)

```ssh-keygen```

```ssh-copy-id yourwindowsusername@192.168.8.131```

If it fails, do this.

```cat ~/.ssh/id_rsa.pub```
 Copy it.

4. Paste it in the file authorized_keys folder on Windows, then save. (Windows)

```notepad $env:USERPROFILE\.ssh\authorized_keys```

Make sure the authorized_keys file does not save as .txt!

Run main.py -> listener.py and go through an trial run of multiple pis running scoreboard detection.
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

2. Connect to Travel Router (or other Private Network).
3. Update The System:
```bash,sudo apt update \&\& sudo apt upgrade -y sudo apt install python3-pip git -y
```
4. Clone the Repository
5. Install the Python Dependencies
```bash, pip3 install -r requirements.txt
```
6. Edit the Pi script (main.py) to set the Windows IP, username, and destination folder for screenshots: If not already done.
7. Configure Pi's to have static IP's and adjust them in the Dashboard.py script if needed on Central PC.
8. Create Hostnames for the pi that match the station being used. E.g station-a
```sudo raspi-config
```
```System Options  →  Hostname
```


SSH from Central (Windows) to Pi.

1. Open Powershell and run

```Powershell, Get-Service sshd
```

2\. If it says Service not found, install

```Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

```Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
```

3\. Start the SSH Server

```Start-Service sshd
```
```Set-Service -Name sshd -StartupType Automatic
```

4\. Find Pi IP, run this on the Pi.

```hostname -I
```

5\. SSH Login from Windows

```ssh pi@192.168.8.xxx
```

6\. If pi says permission Denied, run this

```sudo raspi-config
```

Interface Options -> SSH -> Enable

7\. Generate SSH key on Windows if you don't have one.

```Powershell, ssh-keygen
```
8\. Copy your Windows key to each raspberry pi. Open Git Bash
```ssh-copy-id pi@192.168.8.xxx
```
or 
```scp ~/.ssh/id_rsa.pub pi@192.168.8.xxx:/home/pi/
```

9. On the Pi
```mkdir -p ~/.ssh
```
```cat ~/id_rsa.pub >> ~/.ssh/authorized_keys
```
```chmod 600 ~/.ssh/authorized_keys
```
```rm ~/id_rsa.pub
```

Pi to Windows SSH:
1. Find Windows IP
```ipconfig
```
2. make .ssh folder if not already there.
```mkdir $env:USERPROFILE\.ssh
```
3. Copy pi Keys to windows (on pi)
```ssh-keygen
```
```ssh-copy-id yourwindowsusername@192.168.8.131
```
If it fails, do this.
```cat ~/.ssh/id_rsa.pub
```
or whatever name your ID is. Copy it.
4. Paste it in the file here, then save. (Windows)
```notepad $env:USERPROFILE\.ssh\authorized_keys
```

Make sure the authorized_keys file does not save as .txt!

1. Navigate to the Repo Folder on the local machine.
2. Pip install -r requirements .txt
3. Once all dependencies and packages are installed, Static IP's known. Change the

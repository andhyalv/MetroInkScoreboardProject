\# Metro Ink Splatoon Scoreboard Capture for in person events.

This project seeks to make it easier to capture stats for in person Splatoon events. As there is no native stat capturing or replay system built into the LAN functionality of the game, this solution for capturing stats was made.



This repository contains:

* A Flask server to connect the devices capturing in game scoreboards, and a central dashboard controlling all station devices
* Central Flask server to control all Raspberry Pi's script running.
* Screenshot uploading to Windows (Central) PC via SCP
* Scripts and dependencies for easy setup on new Pi systems.



\## Setup



1. Clone the Repo
2. Install the Python Dependencies
3. Connect the Raspberry Pi to a secure private network and assign it a static IP. 
4. Create SSH Connections from the Central Computer to the PI and share their public keys to allow for seamless communication.
5. Create Hostnames for the pi that match the station being used. E.g station-a
6. Navigate to the Repo Folder on the local machine.
7. Pip install -r requirements .txt
8. Once all dependencies and packages are installed, Static IP's known. Change the 

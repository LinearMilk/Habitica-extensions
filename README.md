# README.md

## Habitica Dailies to To-Dos Automation Script

This script automates the process of converting specific Dailies in [Habitica](https://habitica.com) into To-Dos based on certain criteria. It's designed to run on a Raspberry Pi but can be used on any system with Python 3 installed.

### Features

- **Identifies Dailies that are due today** and have notes starting with a specified prefix (e.g., "Recurrent"), followed by a difficulty descriptor (**Trivial**, **Easy**, **Medium**, **Hard**).
- **Extracts the difficulty descriptor** from the notes and sets the priority of the new To-Do accordingly.
- **Removes the prefix and difficulty descriptor** from the notes when creating the new To-Do.
- **Copies over any checklist items** from the original Daily to the new To-Do, resetting their completion status.
- **Sets the due date** of the new To-Do to the day after tomorrow.
- **Marks the original Daily as completed** instead of deleting it.
- **Handles notes with line breaks and special characters**.
- **Supports multiple Habitica users**.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Automation with Cron](#automation-with-cron)
- [Logging](#logging)
- [Security Considerations](#security-considerations)

---

## Prerequisites

- A Raspberry Pi running a recent version of Raspberry Pi OS (or any system with Python 3).
- Python 3.6 or higher.
- Internet connection.
- Habitica accounts with User ID and API Token.

---

## Installation

### 1. Clone the Repository

SSH into your Raspberry Pi or open a terminal, and clone the repository:

```bash
cd /home/pi
git clone https://github.com/yourusername/habitica-dailies-to-todos.git
```
Replace ``yourusername`` with your GitHub username.

### 2. Install Required Python Packages
The script requires the requests library. Install it using pip3:    

```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install requests
```
If you encounter issues with ``pip3`` due to the environment being externally managed, you can install the ``requests`` library using ``apt``:

```bash
sudo apt-get install python3-requests
```
### 3. Ensure Script Permissions
Make the script executable:

```bash

chmod +x /home/pi/habitica-dailies-to-todos/habitica_automation.py
```

## Configuration
### 1. Prepare the users.json File
Create a ``users.json`` file in the repository directory to store your Habitica API credentials and criteria:

```bash
nano /home/pi/habitica-dailies-to-todos/users.json
```
Add your users' credentials and criteria in the following format:

```json

[
    {
        "username": "YourName",
        "user_id": "your-user-id",
        "api_token": "your-api-token",
        "criteria": {
            "notes_prefix": "Recurrent"
        }
    },
    {
        "username": "PartnerName",
        "user_id": "partner-user-id",
        "api_token": "partner-api-token",
        "criteria": {
            "notes_prefix": "Recurrent"
        }
    }
]
```

* Replace ``"your-user-id"`` and ``"your-api-token"`` with your actual Habitica User ID and API Token.
* Optional: Adjust ``"notes_prefix"`` if you use a different prefix.
Note: Keep this file secure as it contains sensitive information.

### 2. Secure the users.json File
Set permissions to restrict access:

``` bash
chmod 600 /home/pi/habitica-dailies-to-todos/users.json
```

##Usage
Run the Script Manually
You can run the script manually to test it:

```bash
python3 /home/pi/habitica-dailies-to-todos/habitica_automation.py
```

Verify the Script's Actions
* Check your Habitica account(s) to ensure that the Dailies have been converted to To-Dos as expected.
* Review the log files generated in the repository directory:
```bash
cat /home/pi/habitica-dailies-to-todos/habitica_automation_<username>.log
```

# Automation with Cron
To automate the script to run daily at a specific time (e.g., 8:00 AM), set up a cron job.

1. Open the Crontab Editor
```bash
crontab -e
```
2. Add the Cron Job
Add the following line to schedule the script to run every day at 8:00 AM:

```bash
0 8 * * * /usr/bin/python3 /home/pi/habitica-dailies-to-todos/habitica_automation.py
```
Ensure that the path to ``python3`` is correct. You can check it with ``which python3``.
3. Save and Exit
* In the editor, save the changes and exit.
* For nano, press Ctrl + O, then Enter to save, and Ctrl + X to exit.

# Logging
* Logs are generated per user in the repository directory with the filename ``habitica_automation_<username>.log``.
* Ensure the logs are secured:

```bash
chmod 600 /home/pi/habitica-dailies-to-todos/habitica_automation_*.log
```
* Review the logs to monitor the script's activity and troubleshoot any issues.
#Security Considerations
* API Credentials: Store your Habitica User IDs and API Tokens securely in the ``users.json`` file.
* File Permissions: Restrict access to sensitive files using ``chmod 600``.
Public Repositories: If you plan to publish this repository publicly, do not include the ``users.json`` file or any files containing sensitive information.
Add ``users.json`` to ``.gitignore`` to prevent it from being committed to the repository.

# Acknowledgments
This script was developed to enhance the Habitica experience by automating task management.
Special thanks to the Habitica community for their support and inspiration.

# Contact
If you have any questions or need assistance, feel free to reach out. If you have found any bugs, or would like to request a feature, please let me know. If you would like to collaborate or hire me to do some work, let me know as well, please.

# Notes
* **Customization:** Feel free to modify the script to better suit your needs. Ensure that any changes comply with the Habitica API terms of service.
* **Testing:** It's recommended to test the script with a single user and a few tasks before deploying it for multiple users.
* **Backup:** Consider backing up your Habitica data before running the script, especially if it will mark tasks as completed.
---
**Enjoy your automated Habitica task management!**
---
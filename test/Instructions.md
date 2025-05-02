# EVCS Data Collection System Deployment

## Setup Instructions

1. **Install Required Packages**
   ```bash
   pip install schedule requests pymongo
   ```

2. **File Structure**
   - Save your main data collection script as `evcs_data_collector.py`
   - Save the scheduler script as `evcs_scheduler.py`
   - The scheduler will create a `logs` directory automatically

3. **Run the Scheduler**
   ```bash
   python evcs_scheduler.py
   ```

## Running as a Background Service

### On Linux (using systemd)

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/evcs-collector.service
   ```

2. Add the following content (adjust paths as needed):
   ```
   [Unit]
   Description=EVCS Data Collection Service
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/home/hung/Documents/DEMO/charging-station/test/
   ExecStart=/home/hung/.local/share/virtualenvs/works-4wnlDAsI/bin/python /home/hung/Documents/DEMO/charging-station/test/evcs_scheduler.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable evcs-collector.service
   sudo systemctl start evcs-collector.service
   ```

4. Check service status:
   ```bash
   sudo systemctl status evcs-collector.service
   ```

### On Windows (using Task Scheduler)

1. Create a batch file (run_scheduler.bat):
   ```batch
   @echo off
   cd /d %~dp0
   python evcs_scheduler.py
   ```

2. Open Task Scheduler and create a new task:
   - General: Run whether user is logged on or not
   - Triggers: At startup
   - Actions: Start a program -> Browse to your batch file
   - Conditions: Start the task only if the computer is idle for 1 minute
   - Settings: Allow task to be run on demand, run task as soon as possible after a scheduled start is missed

## Monitoring

The scheduler creates daily log files in the `logs` directory. You can monitor these logs to check for any issues:

```bash
tail -f logs/evcs_scheduler_20250502.log
```

The log files contain information about when each collection job started, its completion status, and any errors encountered.
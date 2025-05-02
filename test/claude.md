### The Scheduler Script Features:

1. **Scheduled Execution:**
   - Runs your data collection script every 30 minutes using the `schedule` library
   - Executes once immediately on startup, then follows the schedule

2. **Robust Logging:**
   - Creates dated log files in a `logs` directory
   - Logs start/end times and duration of each collection job
   - Captures and logs both standard output and errors from your script

3. **Error Handling:**
   - Monitors script return codes to detect failures
   - Catches and logs any exceptions that occur
   - Continues running even if individual jobs fail

4. **Process Management:**
   - Runs your script as a subprocess to keep it isolated
   - If your script crashes, the scheduler will still run the next job on schedule

### How to Use It:

1. Save your original data collection script as `evcs_data_collector.py`
2. Save the scheduler as `evcs_scheduler.py`
3. Install the required packages: `pip install schedule`
4. Run the scheduler: `python evcs_scheduler.py`
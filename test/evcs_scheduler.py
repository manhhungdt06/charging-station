import schedule
import time
import subprocess
import logging
import datetime
import os

# Setup logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'evcs_scheduler_{datetime.datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)

# Path to the data collection script
script_path = '/home/hung/Documents/DEMO/charging-station/test/evcs_data_collector.py'

def run_collection_job():
    job_start_time = datetime.datetime.now()
    logging.info(f"Starting data collection job at {job_start_time}")
    
    try:
        # Run the data collection script as a subprocess
        process = subprocess.Popen(['python', script_path], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
        
        # Get output and errors
        stdout, stderr = process.communicate()
        
        # Log script output
        if stdout:
            for line in stdout.splitlines():
                logging.info(f"SCRIPT OUTPUT: {line}")
        
        # Log any errors
        if stderr:
            for line in stderr.splitlines():
                logging.error(f"SCRIPT ERROR: {line}")
        
        # Check return code
        if process.returncode != 0:
            logging.error(f"Data collection script failed with return code {process.returncode}")
        else:
            logging.info("Data collection completed successfully")
    
    except Exception as e:
        logging.error(f"Failed to run data collection script: {e}")
    
    job_end_time = datetime.datetime.now()
    duration = (job_end_time - job_start_time).total_seconds()
    logging.info(f"Data collection job finished at {job_end_time} (Duration: {duration:.2f} seconds)")

def main():
    logging.info("Starting EVCS data collection scheduler")

    # Schedule jobs at :00 and :30 of every hour
    schedule.every().hour.at(":00").do(run_collection_job)
    # schedule.every().hour.at(":30").do(run_collection_job)

    # # Optionally run initial job immediately (if needed)
    # logging.info("Running initial data collection job")
    # run_collection_job()

    # Keep the script running and execute scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler crashed: {e}")
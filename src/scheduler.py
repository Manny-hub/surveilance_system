from apscheduler.schedulers.background import BackgroundScheduler
import logging
import time

logging.basicConfig(level=logging.INFO)

def start_scheduler(task_func, interval_minutes=15):
    scheduler = BackgroundScheduler()
    scheduler.add_job(task_func, 'interval', minutes=interval_minutes)
    scheduler.start()
    logging.info(f"Scheduler started: running every {interval_minutes} minutes.")

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Scheduler stopped.")
import datetime
import os
import shutil
import time

from appdirs import user_log_dir

APP_NAME = "net.dmlane.test"
AUTHOR = "dave"
folder = user_log_dir(APP_NAME, AUTHOR)
os.makedirs(folder, exist_ok=True)

dt = datetime.datetime.combine(
    datetime.date.today(), datetime.datetime.min.time()
) - datetime.timedelta(hours=12)

secs = int(time.mktime(dt.timetuple()))

for day in range(1, 8):
    if day > 1:
        fn = f'{folder}/test_logger.log.{dt.strftime("%Y%m%d")}'
    else:
        fn = f"{folder}/test_logger.log"

    with open(fn, "a") as f:
        f.write("Something\n")
    os.utime(fn, (secs, secs))
    secs -= 24 * 60 * 60
    dt = dt - datetime.timedelta(days=1)

import os
import logging
from utils.shortcuts import get_env
import datetime

formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s] - [%(name)s:%(lineno)d]  - %(message)s', '%Y-%m-%d %H:%M:%S')
serverlogger = logging.getLogger(__name__)
userlogger = logging.getLogger("HTTP-Method")

production_env = get_env("YG_ENV", "dev") == "production"
if production_env:
    LOG_PATH = "/data/log/user"
else:
    LOG_PATH = "./data/log/user"

trfh = logging.handlers.TimedRotatingFileHandler(
    filename = os.path.join(LOG_PATH, f"{datetime.datetime.today().strftime('%Y-%m-%d')}.log"),
    when = "midnight",
    interval=1,
    encoding="utf-8",
)
trfh.setFormatter(formatter)
trfh.setLevel(logging.INFO)
userlogger.addHandler(trfh)
userlogger.setLevel(logging.DEBUG)
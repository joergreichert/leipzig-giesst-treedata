import logging
import os
from datetime import datetime
from datetime import timedelta
import urllib.request

# setting up logging
logging.basicConfig()
LOGGING_MODE = None
if "LOGGING" in os.environ:
    LOGGING_MODE = os.getenv("LOGGING")
    if LOGGING_MODE == "ERROR":
        logging.root.setLevel(logging.ERROR)
    elif LOGGING_MODE == "WARNING":
        logging.root.setLevel(logging.WARNING)
    elif LOGGING_MODE == "INFO":
        logging.root.setLevel(logging.INFO)
    else:
        logging.root.setLevel(logging.NOTSET)
else:
    logging.root.setLevel(logging.NOTSET)

# get last day of insert
last_date = datetime.now() + timedelta(days=-2)

end_date = datetime.now() + timedelta(days=-1)
date = datetime.combine(last_date, datetime.min.time())

# create a temporary folder to store the downloaded DWD data
path = "weather_data/data_files/"
if not os.path.isdir(path):
    os.mkdir(path)

while date <= end_date:
    url = 'https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/RW-{}.tar.gz'.format(
        date.strftime("%Y%m%d"))
    url_split = url.split("/")
    dest_name = url_split[len(url_split) - 1]
    dest = path + dest_name

    try:
        urllib.request.urlretrieve(url, dest)
    except:
        logging.warning("❌Could not download {}".format(url))

    date += timedelta(days=1)
    logging.info("Downloading: {} / {}".format(end_date, date))

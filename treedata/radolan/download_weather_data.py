import logging
import os
from datetime import datetime
from datetime import timedelta
import urllib.request

ROOT_DIR = os.path.abspath(os.curdir)

def download_weather_data(start_days_offset, end_days_offset):
    # get last day of insert
    last_date = datetime.now() + timedelta(days=-start_days_offset)

    end_date = datetime.now() + timedelta(days=-end_days_offset)
    date = datetime.combine(last_date, datetime.min.time())

    # create a temporary folder to store the downloaded DWD data
    path = f"{ROOT_DIR}/../resources/radolan/"
    if not os.path.isdir(path):
        os.mkdir(path)

    while date <= end_date:
        url = 'https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/RW-{}.tar.gz'\
            .format(date.strftime("%Y%m%d"))
        url_split = url.split("/")
        dest_name = url_split[len(url_split) - 1]
        dest = path + dest_name

        try:
            urllib.request.urlretrieve(url, dest)
        except:
            logging.warning("❌Could not download {}".format(url))

        date += timedelta(days=1)
        logging.info("Downloading: {} / {}".format(end_date, date))

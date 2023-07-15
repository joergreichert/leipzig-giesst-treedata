import logging
import os
import tarfile
import gzip
import shutil

path = "weather_data/data_files/"


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


# unpack the data and delete the zips afterwards
for (dirpath, dirnames, filenames) in os.walk(path):
  for fileindex, filename in enumerate(filenames):
    if ".tar.gz" in filename:
      # first unzip
      full_filename = path + filename
      with gzip.open(full_filename, 'rb') as f_in:
        with open(full_filename.split(".gz")[0], 'wb') as f_out:
          shutil.copyfileobj(f_in, f_out)
      #os.remove(full_filename)

      # now untar
      with tarfile.open(full_filename.split(".gz")[0], "r") as tar:
        temp_path = full_filename.split(".tar")[0]
        if os.path.isdir(temp_path) == False:
            os.mkdir(temp_path)
        tarlist = []
        for member in tar.getmembers():
            tarlist.append(member)
        tar.extractall(temp_path, tarlist)
        tar.close()

      os.remove(full_filename.split(".gz")[0])
      logging.info("Unzipping: {} / {}".format(len(filenames), fileindex+1))
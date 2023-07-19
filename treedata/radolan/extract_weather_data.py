import logging
import os
import tarfile
import gzip
import shutil

ROOT_DIR = os.path.abspath(os.curdir)
path = f"{ROOT_DIR}/../resources/radolan/"


def extract_weather_data():
    for (dirpath, dirnames, filenames) in os.walk(path):
        for fileindex, filename in enumerate(filenames):
            if ".tar.gz" in filename:
                # first unzip
                full_filename = path + filename
                with gzip.open(full_filename, 'rb') as f_in:
                    with open(full_filename.split(".gz")[0], 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # now untar
                with tarfile.open(full_filename.split(".gz")[0], "r") as tar:
                    temp_path = full_filename.split(".tar")[0]
                    if not os.path.isdir(temp_path):
                        os.mkdir(temp_path)
                    tarlist = []
                    for member in tar.getmembers():
                        tarlist.append(member)
                    tar.extractall(temp_path, tarlist)
                    tar.close()

                os.remove(full_filename.split(".gz")[0])
                logging.info("Unzipping: {} / {}".format(len(filenames), fileindex + 1))

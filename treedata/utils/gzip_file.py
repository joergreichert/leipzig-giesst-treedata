import gzip


def gzip_file(file_path):
    file = open(file_path, "rb")
    data = file.read()
    bindata = bytearray(data)
    gzip_file_path = f"{file_path}.gz"
    with gzip.open(file_path, "wb") as f:
        f.write(bindata)
    return gzip_file_path


def gzip_files(file_path_to_file_name):
    gzip_file_path_to_file_name = {}
    for file_path in file_path_to_file_name:
        file_name = file_path_to_file_name[file_path]
        gzip_file_path = gzip_file(file_path)
        gzip_file_path_to_file_name[gzip_file_path] = f"{file_name}.gz"
    return gzip_file_path_to_file_name

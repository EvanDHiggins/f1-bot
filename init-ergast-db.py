import requests
from clint.textui import progress
import tempfile
import gzip
import shutil
import os

ergast_sqlite_db_url = 'https://ergast.com/downloads/f1db.sql.gz'
output_temp_file_name = 'f1db.sql.gz'
db_file_name = 'f1db.sql'
db_name = 'ergast'

def get_length(r: requests.Response) -> int:
    header_val = r.headers.get('content-length')
    if header_val is None:
        raise ValueError('Request did not have a "content-length" header.')
    return int(header_val)


def download_zipped(file_name: str):
    r = requests.get(ergast_sqlite_db_url, stream=True)
    with open(file_name, 'wb') as f:
        total_length = get_length(r)
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            f.write(chunk)
            f.flush()


def unzip(src: str, dst: str):
    with gzip.open(src, 'rb') as f_in:
        with open(dst, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def replace_mysql_db(db_path: str):
    os.system(f"echo 'drop database {db_name}; create database {db_name};' | mysql -u root")
    os.system(f"mysql -u root {db_name} < {db_path}")

    # clean up unzipped db file.
    os.remove(db_file_name)


def main():
    tmp = tempfile.NamedTemporaryFile()
    download_zipped(tmp.name)
    unzip(tmp.name, db_file_name)
    replace_mysql_db(db_file_name)


if __name__ == '__main__':
    main()

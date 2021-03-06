from urllib.request import urlretrieve
import os
import tarfile
import pysftp
import json
from glob import glob
from pandas.io.json import json_normalize

ALLEN_AI_RESOURCES = ['https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/comm_use_subset.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/noncomm_use_subset.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/custom_license.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/biorxiv_medrxiv.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/metadata.csv',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-13/all_sources_metadata_2020-03-13.readme']

DIMENSIONS_RESOURCES = ['https://docs.google.com/spreadsheets/d/1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw/export?format=csv&id=1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw&gid=1470772867']

ELSEVIER_SFTP = {
    'host': 'coronacontent.np.elsst.com',
    'user': 'public',
    'password': 'beat_corona'
}

BASE_DIR = "res/"


def download_resources(urls, target_dir, verbose=True):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for url in urls:
        file_name = url.split('/')[-1]
        if '?' in url:
            file_suffix = '.csv' if 'csv' in file_name.split('?')[1] else ''
            file_name = file_name.split('?')[0] + file_suffix # fix e.g. <url>/export?queryParam=23 -> <url>/export
        target_file_path = os.path.join(target_dir, file_name)
        if verbose:
            print(f"Downloading from {url} to {target_file_path}")
        urlretrieve(url, target_file_path)


def download_from_sftp(host, user, pwd, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if host == ELSEVIER_SFTP['host'] and not os.path.exists(os.path.join(target_dir, 'meta')):
        os.makedirs(os.path.join(target_dir, 'meta'))

    print(f"Downloading from stfp://{host} to {target_dir}")

    # do not perform sftp hostkey check
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(host, username=user, password=pwd, cnopts=cnopts) as sftp:
        sftp.get_d("./", target_dir, preserve_mtime=True)
        if host == ELSEVIER_SFTP['host']:
            # only get metadata from elsevier, as the other files take a huge amount of time to be transferred
            sftp.get_d("meta/", os.path.join(target_dir, 'meta'), preserve_mtime=True)

def unzip_resources(folder):
    for path in glob(folder + "/*.tar.gz"):
        print(f"Extracting {path}")
        tar = tarfile.open(path)
        tar.extractall(path=folder)
        tar.close()


def merge_to_jsonl(folder, target_file):
    json_list = []
    for f in glob(folder + "/*.json"):
        with open(f, "r") as infile:
            # fixes invalid files before loading
            json_list.append(json.loads("".join(infile.readlines()).replace("\n",""))['full-text-retrieval-response'])
            # includes simple normalization

    json_normalize(json_list).to_json(target_file, orient='records', lines=True)


def download_all(base_dir=BASE_DIR):
    for res_folder, url_list, perform_import in \
            zip(['allenai', 'dimensions'], [ALLEN_AI_RESOURCES, DIMENSIONS_RESOURCES], [True, False]):
        if not perform_import:
            print("Skipping retrieval for", res_folder)
            continue
        target_folder = os.path.join(base_dir, res_folder)
        print("Fetching files to " + target_folder)
        download_resources(url_list, target_folder)
        unzip_resources(target_folder)

    # for res_folder, sftp_con_info in (zip(['elsevier'], [ELSEVIER_SFTP])):
    #     target_folder = os.path.join(base_dir, res_folder)
    #     download_from_sftp(sftp_con_info['host'], sftp_con_info['user'], sftp_con_info['password'], target_folder)
    #
    # # convert input format
    # merge_to_jsonl(os.path.join(base_dir, 'elsevier', 'meta'), os.path.join(base_dir, 'elsevier', 'meta.jsonl'))
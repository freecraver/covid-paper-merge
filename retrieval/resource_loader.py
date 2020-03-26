from urllib.request import urlretrieve
import os
import tarfile
from glob import glob

ALLEN_AI_RESOURCES = ['https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/comm_use_subset.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/noncomm_use_subset.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/custom_license.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/biorxiv_medrxiv.tar.gz',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-20/metadata.csv',
                      'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-03-13/all_sources_metadata_2020-03-13.readme']

BASE_DIR = "res/"


def download_resources(urls, target_dir, verbose=True):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for url in urls:
        target_file_path = os.path.join(target_dir, url.split('/')[-1])
        if verbose:
            print(f"Downloading from {url} to {target_file_path}")
        urlretrieve(url, target_file_path)


def unzip_resources(folder):
    for path in glob(folder + "/*.tar.gz"):
        print(f"Extracting {path}")
        tar = tarfile.open(path)
        tar.extractall(path=folder)
        tar.close()


def download_all(base_dir=BASE_DIR):
    for res_folder, url_list in zip(['allenai'], [ALLEN_AI_RESOURCES]):
        target_folder = os.path.join(base_dir, res_folder)
        print("Fetching files to " + target_folder)
        download_resources(url_list, target_folder)
        unzip_resources(target_folder)
import os.path
from os import path
from time import sleep

import requests
from random import randint


class HtmlCache:
    def __init__(self, cache_filepath: str):
        self.__cache_base_dir = cache_filepath

    def get_base_dir(self) -> str:
        return self.__cache_base_dir

    def get(self, url: str, cache_file_path: str) -> str | None:
        if cache_file_path.endswith('/') or cache_file_path.endswith('\\'):
            raise ValueError(
                "cache_file_path must be a file path, and not end in directory path delimiter (ambiguity: would this be a file path or a dir path?)")

        if path.exists(f'{cache_file_path}'):
            with open(cache_file_path, 'r', encoding='utf8') as fp:
                return fp.read()

        # sleep for a random amount of time, to prevent flooding a site with requests
        min_sleep_secs = 1
        max_sleep_secs = 5
        sleep(randint(min_sleep_secs, max_sleep_secs))

        req = requests.get(url)
        if req.status_code != 200:
            return None

        # create dirs as needed
        cache_file_path_dirname = os.path.dirname(cache_file_path)
        if not os.path.exists(cache_file_path_dirname):
            os.makedirs(cache_file_path_dirname)

        with open(f'{cache_file_path}', 'w', encoding='utf8') as fp:
            fp.write(req.text)

        return req.text

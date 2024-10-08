from os import path
from time import sleep
from random import randint

import requests


class HtmlCache:
    def __init__(self, cache_filepath: str):
        self.__cache_base_dir = cache_filepath

    def get_base_dir(self) -> str:
        return self.__cache_base_dir

    def get(self, url: str, filepath: str) -> str | None:
        if path.exists(f'{filepath}'):
            with open(filepath, 'r') as fp:
                return fp.read()

        # sleep for a random amount of time, to prevent flooding a site with requests
        min_sleep_secs = 1
        max_sleep_secs = 5
        sleep(randint(min_sleep_secs, max_sleep_secs))

        req = requests.get(url)
        if req.status_code != 200:
            return None

        with open(f'{self.__cache_base_dir}/{filepath}', 'w') as fp:
            fp.write(req.text)

        return req.text

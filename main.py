from zipcodeInfo import ZipcodeInfo

import csv
from os import path
from typing import List

from bs4 import BeautifulSoup
import requests

from random import randint
from time import sleep


def zipcode_infos_from_csv(filepath: str) -> List[ZipcodeInfo]:
    with open(filepath, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        next(spamreader)  # skip the header row

        result: List[ZipcodeInfo] = []
        for i, row in enumerate(spamreader):
            zipcode = row[0]
            zip_part_district, zip_part_street = zipcode.split('-')
            zipcode_info = ZipcodeInfo(zip_part_district, zip_part_street)
            result.append(zipcode_info)
        return result


def get_from_html_cache(cache_path: str, district_code: str, street_code: str) -> str | None:
    filepath = f"{cache_path}/{district_code}-{street_code}.html"
    if path.exists(filepath):
        with open(filepath, 'r') as fp:
            data = fp.read()
            return data
    return None


def cache_html(cache_path: str, district_code: str, street_code: str, text: str):
    filepath = f"{cache_path}/{district_code}-{street_code}.html"
    with open(filepath, 'w') as fp:
        fp.write(text)


def main():
    csv_file_path = r"codigos_postais.csv"
    url_fmt = r'https://www.codigo-postal.pt/?cp4={zip_district}&cp3={zip_street}'
    cache_path = 'cache'
    failed_requests_log_filepath = 'failed.txt'

    failed_requests_fp = open(failed_requests_log_filepath, 'a')

    infos = zipcode_infos_from_csv(csv_file_path)

    infos_slice = infos[:120]

    for i, zipInfo in enumerate(infos_slice):
        print()
        print(f"{i} CP: {zipInfo.district_code}-{zipInfo.street_code}")
        url = url_fmt.format(zip_district=zipInfo.district_code, zip_street=zipInfo.street_code)

        print(f"Getting from {url}")

        text: str = get_from_html_cache(cache_path, zipInfo.district_code, zipInfo.street_code)

        if text is None:
            print("HTML data not cached. Downloading...")

            min_sleep_sec = 1
            max_sleep_sec = 5
            sleep(randint(min_sleep_sec, max_sleep_sec))  # sleep before getting HTML

            page = requests.get(url)
            if page.status_code != 200:
                print(f"Failed to get with status code {page.status_code}")
                failed_requests_fp.write(f"url: {url} code: {page.status_code}\n")
                continue
            text = page.text
            cache_html(cache_path, zipInfo.district_code, zipInfo.street_code, text)
        else:
            print("HTML data was cached.")

        soup = BeautifulSoup(text, 'html.parser')
        selector_entries = '#isolated > div'
        entries = soup.select(selector_entries)
        if len(entries) == 0:
            print("No entries")
            continue

        first_entry = entries[0]

        #TODO: follow the URL from the first local, and grab Distrito and Concelho from there,
        # instead of doing this, which is erroneous

        locals_class_selector = '.local'
        entries_locals = first_entry.select(locals_class_selector)
        if len(entries_locals) == 0:
            print("No locals")
            continue

        first_local = entries_locals[0]

        first_local_parts = [x.strip() for x in first_local.text.split(',')]
        if len(first_local_parts) < 2:
            print("Missing Concelho and Distrito")
            continue

        local_concelho = first_local_parts[-2]
        local_distrito = first_local_parts[-1]

        print(f"Concelho: {local_concelho}, Distrito: {local_distrito}")

    failed_requests_fp.close()


if __name__ == '__main__':
    main()

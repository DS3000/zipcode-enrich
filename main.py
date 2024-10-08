import csv
from datetime import datetime, UTC
from typing import List

from CodigoPostalPtExtractor import CodigoPostalPtExtractor
from CttCodigoPostalExtractor import CttCodigoPostalExtractor
from HtmlCache import HtmlCache
from LocaleInfo import LocaleInfo
from ZipInfoExtractor import ZipInfoExtractor
from ZipcodeInfo import ZipcodeInfo


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


def main():
    csv_file_path = r"codigos_postais.csv"
    failed_requests_log_filepath = 'failed.txt'
    missing_data_log_filepath = 'missing.txt'

    failed_requests_fp = open(failed_requests_log_filepath, 'a')
    failed_requests_fp.write("\n\n")
    missing_data_fp = open(missing_data_log_filepath, 'a')
    missing_data_fp.write("\n\n")
    html_cache: HtmlCache = HtmlCache('cache')

    extractors: List[ZipInfoExtractor] = [
        CodigoPostalPtExtractor(html_cache),
        CttCodigoPostalExtractor(html_cache)
    ]

    infos = zipcode_infos_from_csv(csv_file_path)

    slice_start_idx = 0
    slice_end_idx = 100

    infos_slice = infos[slice_start_idx: slice_end_idx]

    for i, zip_info in enumerate(infos_slice):
        print()
        print(f"{i} CP: {zip_info.cp4}-{zip_info.cp3}")

        res: LocaleInfo | None = None
        got_info = False
        for ex in extractors:
            res = ex.fetch_info(zip_info)
            if res is not None:
                got_info = True
                print(f"Extractor {ex.__class__.__name__} got a hit")
                break

        if not got_info:
            print("Failed to get info")
            missing_data_fp.write(f"{datetime.now(UTC)} - {zip_info}\n")
            continue

        print(f"Got {res}")

    missing_data_fp.close()
    failed_requests_fp.close()


if __name__ == '__main__':
    main()

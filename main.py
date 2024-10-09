import csv
import mysql.connector
from datetime import datetime, UTC
from flask import Flask, request, jsonify
from typing import List, Dict

import my_secrets
from CodigoPostalPtExtractor import CodigoPostalPtExtractor
from CttCodigoPostalExtractor import CttCodigoPostalExtractor
from HtmlCache import HtmlCache
from LocaleInfo import LocaleInfo
from ZipInfoExtractor import ZipInfoExtractor
from ZipcodeInfo import ZipcodeInfo

cnx = mysql.connector.connect(user='root', database='zipcode_db', host='localhost', password=my_secrets.db_password)


def db_search_for_zipcode(zip_info: ZipcodeInfo) -> LocaleInfo | None:
    with cnx.cursor() as cursor:
        query = (
            "select t_concelho.name, t_distrito.name, t_infomap.zip from t_infomap"
            " left join t_concelho on t_concelho.id_concelho=t_infomap.id_concelho"
            " left join t_distrito on t_distrito.id_distrito=t_infomap.id_distrito"
            f" where t_infomap.zip='{zip_info}'"
        )
        cursor.execute(query)
        print("Query results:")

        for concelho, distrito, zipcode in cursor:
            print(f"Concelho: {concelho}, Distrito: {distrito}, zipcode: {zipcode}")
            return LocaleInfo(distrito, concelho)

    return None


flask_app: Flask = Flask(__name__)

html_cache: HtmlCache = HtmlCache('cache')

extractors: List[ZipInfoExtractor] = [
    CodigoPostalPtExtractor(html_cache),
    CttCodigoPostalExtractor(html_cache)
]

info_map: Dict[ZipcodeInfo, LocaleInfo] = {}


@flask_app.route('/', methods=['GET'])
def get_locale_info():
    param_name = 'codigo_postal'

    codigo_postal = request.args.get(param_name)

    if codigo_postal is None:
        msg = (
            f'Missing param {param_name}. Format must be <cp4>-<cp3>,'
            ' where cp4 is four digits, and cp3 is three digits'
        )
        return (
            jsonify({'message': msg}),
            400
        )

    try:
        parts = codigo_postal.split('-')

        # make sure they're valid numbers
        cp4 = int(parts[0])
        cp3 = int(parts[1])

        zip_info: ZipcodeInfo = ZipcodeInfo(parts[0], parts[1])
    except:
        msg = (
            f'{codigo_postal} is not a valid zip code. Format must be <cp4>-<cp3>,'
            ' where cp4 is four digits, and cp3 is three digits'
        )
        return (
            jsonify({'message': msg}),
            400
        )

    print(f"Request made, with info {zip_info}")

    res = info_map.get(zip_info)
    # res = db_search_for_zipcode(zip_info)
    print(f"Got {res}")

    if res is None:
        return (
            jsonify({'message': f'zip code not in the database'}),
            404
        )

    return (
        jsonify({'concelho': res.concelho, 'distrito': res.distrito}),
        200
    )


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


def dump_infos_to_csv(filepath: str, infos: Dict[ZipcodeInfo, LocaleInfo]):
    with open(filepath, 'w', newline='', encoding='utf8') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(["cp7", "concelho", "distrito"])
        for zip_info, locale_info in infos.items():
            csv_writer.writerow([f"{zip_info.cp4}-{zip_info.cp3}", locale_info.concelho, locale_info.distrito])


def insert_into_db(info_map: Dict[ZipcodeInfo, LocaleInfo]):
    insert_into_concelho_query = "insert into t_concelho (name) values(%(concelho_name)s)"
    insert_into_distrito_query = "insert into t_distrito (name) values(%(distrito_name)s)"
    insert_into_infomap_query = ("insert into t_infomap (id_concelho, id_distrito, zip)"
                                 " values(%(id_concelho)s, %(id_distrito)s, %(zip_code)s)")

    for zipcode_info, locale_info in info_map.items():
        with cnx.cursor() as cursor:
            try:
                cursor.execute(insert_into_concelho_query, {"concelho_name": locale_info.concelho})
                id_concelho = cursor.lastrowid

                cursor.execute(insert_into_distrito_query, {"distrito_name": locale_info.distrito})
                id_distrito = cursor.lastrowid

                data = {
                    'id_distrito': id_distrito,
                    'id_concelho': id_concelho,
                    'zip_code': str(zipcode_info)
                }

                cursor.execute(insert_into_infomap_query, data)

                cnx.commit()
            except mysql.connector.Error as e:
                # TODO: handle duplicate entries
                print("Error code:", e.errno)  # error number
                print("SQLSTATE value:", e.sqlstate)  # SQLSTATE value
                print("Error message:", e.msg)  # error message
                print("Error:", e)  # errno, sqlstate, msg values
                s = str(e)
                print("Error:", s)  # errno, sqlstate, msg values


def main():
    csv_file_path = r"codigos_postais.csv"
    failed_requests_log_filepath = 'failed.txt'
    missing_data_log_filepath = 'missing.txt'

    failed_requests_fp = open(failed_requests_log_filepath, 'a')
    failed_requests_fp.write("\n\n")
    missing_data_fp = open(missing_data_log_filepath, 'a')
    missing_data_fp.write("\n\n")

    infos = zipcode_infos_from_csv(csv_file_path)

    slice_start_idx = 0
    slice_end_idx = 200

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

        info_map[zip_info] = res
        print(f"Got {res}")

    missing_data_fp.close()
    failed_requests_fp.close()

    dump_infos_to_csv('enriched.csv', info_map)

    insert_into_db(info_map)

    print("Serving API now...")
    flask_app.run()

    cnx.close()


if __name__ == '__main__':
    main()

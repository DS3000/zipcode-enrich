import requests
from typing import Dict, Tuple

from ZipInfoExtractor import ZipInfoExtractor
from secrets import cttcodigpostal_api_key
from ZipcodeInfo import ZipcodeInfo
from LocaleInfo import LocaleInfo


class CttCodigoPostalExtractor(ZipInfoExtractor):
    __url_fmt = r"https://www.cttcodigopostal.pt/api/v1/{api_key}/{cp4}-{cp3}"

    def fetch_info(self, zip_info: ZipcodeInfo) -> LocaleInfo | None:
        url = self.__url_fmt.format(api_key=cttcodigpostal_api_key,
                                    cp4=zip_info.cp4,
                                    cp3=zip_info.cp3)
        #TODO: use HtmlCache class

        resp = requests.get(url)
        if resp.status_code != 200:
            return

        json_data = resp.json()
        if not isinstance(json_data, list):
            return

        if len(json_data) == 0:
            return

        json_data: Dict = json_data[0]

        distrito = json_data.get('distrito')
        concelho = json_data.get("concelho")

        return LocaleInfo(distrito, concelho)

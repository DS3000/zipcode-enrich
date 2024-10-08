import json
from typing import Dict

from LocaleInfo import LocaleInfo
from ZipInfoExtractor import ZipInfoExtractor
from ZipcodeInfo import ZipcodeInfo
from secrets import cttcodigpostal_api_key


class CttCodigoPostalExtractor(ZipInfoExtractor):
    __url_fmt = r"https://www.cttcodigopostal.pt/api/v1/{api_key}/{cp4}-{cp3}"
    extractor_cache_subdir = "cttcodigopostal"

    def fetch_info(self, zip_info: ZipcodeInfo) -> LocaleInfo | None:
        url = self.__url_fmt.format(api_key=cttcodigpostal_api_key,
                                    cp4=zip_info.cp4,
                                    cp3=zip_info.cp3)

        cache_filepath = f"{self.cache.get_base_dir()}/{self.extractor_cache_subdir}/{zip_info.cp4}-{zip_info.cp3}.json"
        text = self.cache.get(url, cache_filepath)

        if text is None:
            return None

        json_data = json.loads(text)
        if not isinstance(json_data, list):
            return None

        if len(json_data) == 0:
            return None

        json_data: Dict = json_data[0]

        distrito = json_data.get('distrito')
        concelho = json_data.get("concelho")

        return LocaleInfo(distrito, concelho)

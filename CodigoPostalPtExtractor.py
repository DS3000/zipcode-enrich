from bs4 import BeautifulSoup
from dataclasses import dataclass, field

from LocaleInfo import LocaleInfo
from ZipInfoExtractor import ZipInfoExtractor
from ZipcodeInfo import ZipcodeInfo


@dataclass
class CodigoPostalPtExtractor(ZipInfoExtractor):
    __base_url: str = field(init=False, default=r'https://www.codigo-postal.pt')
    __url_fmt: str = field(init=False, default=r'https://www.codigo-postal.pt/?cp4={cp4}&cp3={cp3}')
    extractor_cache_subdir = "codigopsotalpt"

    def fetch_info(self, zip_info: ZipcodeInfo) -> LocaleInfo | None:
        url = self.__url_fmt.format(cp4=zip_info.cp4,
                                    cp3=zip_info.cp3)

        cache_filepath = f'{self.cache.get_base_dir()}/{self.extractor_cache_subdir}/{zip_info.cp4}-{zip_info.cp3}.html'
        text = self.cache.get(url, cache_filepath)
        if text is None:
            return
        try:
            return self.__parse_html_data(text, zip_info)
        except:
            return None

    def __parse_html_data(self, text: str, zipcode_info: ZipcodeInfo) -> LocaleInfo | None:
        soup = BeautifulSoup(text, 'html.parser')
        selector_entries = '#isolated > div.places'
        places = soup.select_one(selector_entries)
        if places is None:
            return None

        place_link = places.select_one('a')
        if place_link is None:
            return None

        href = place_link['href']

        place_info_link = self.__base_url + href
        cache_filepath = f"{self.cache.get_base_dir()}/{self.extractor_cache_subdir}/{zipcode_info.cp4}-{zipcode_info.cp3}-local.html"

        place_info_html = self.cache.get(place_info_link, cache_filepath)
        if place_info_html is None:
            return None

        soup2 = BeautifulSoup(place_info_html, 'html.parser')
        el = soup2.select_one('.geoinfo>div.text')
        if el is None:
            return None
        parts = (
            el.text.
            replace('Concelho', '\nConcelho')
            .replace('Distrito', '\nDistrito')
            .replace('GPS', '\nGPS')
            .replace(': \n', ':')
            .split('\n')
        )

        distrito: str = ""
        concelho: str = ""

        parts = [x.strip().split(': ') for x in parts]
        for part in parts:
            if len(part) < 2:
                continue

            label = part[0]
            info = part[1]

            match label:
                case "Distrito":
                    distrito = info
                case "Concelho":
                    concelho = info

        result = LocaleInfo(distrito, concelho)
        return result

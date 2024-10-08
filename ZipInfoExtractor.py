from dataclasses import dataclass
from typing import Tuple

from HtmlCache import HtmlCache
from ZipcodeInfo import ZipcodeInfo
from LocaleInfo import LocaleInfo


@dataclass
class ZipInfoExtractor:
    cache: HtmlCache

    def fetch_info(self, zip_info: ZipcodeInfo) -> LocaleInfo | None:
        pass

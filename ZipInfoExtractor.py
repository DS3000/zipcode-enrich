from dataclasses import dataclass, field
from typing import Tuple

from HtmlCache import HtmlCache
from ZipcodeInfo import ZipcodeInfo
from LocaleInfo import LocaleInfo


@dataclass
class ZipInfoExtractor:
    cache: HtmlCache
    extractor_cache_subdir: str = field(init=False)

    def fetch_info(self, zip_info: ZipcodeInfo) -> LocaleInfo | None:
        pass

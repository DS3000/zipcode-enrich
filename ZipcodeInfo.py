from dataclasses import dataclass


@dataclass
class ZipcodeInfo:
    cp4: str
    cp3: str

    def __str__(self):
        return f"{self.cp4}-{self.cp3}"

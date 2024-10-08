from dataclasses import dataclass


@dataclass
class LocaleInfo:
    distrito: str
    concelho: str

    def __str__(self):
        return f"Distrito: {self.distrito}; Concelho: {self.concelho}"
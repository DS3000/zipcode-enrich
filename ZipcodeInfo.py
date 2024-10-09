from dataclasses import dataclass


@dataclass
class ZipcodeInfo:
    cp4: str
    cp3: str

    def __str__(self):
        return f"{self.cp4}-{self.cp3}"

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__) and
                self.cp4 == other.cp4 and
                self.cp3 == other.cp3
        )

    def __hash__(self):
        return hash(f"{self.cp4}-{self.cp3}")

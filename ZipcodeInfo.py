class ZipcodeInfo:
    cp4: str
    cp3: str

    def __init__(self, cp4: str, cp3: str):
        valid_cp4 = len(cp4) == 4 and cp4.isnumeric()
        valid_cp3 = len(cp3) == 3 and cp3.isnumeric()

        if not (valid_cp4 and valid_cp3):
            raise Exception("cp4 and cp3 must be string-encoded numbers, with length 4 and 3 respectively")

        self.cp4 = cp4
        self.cp3 = cp3

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

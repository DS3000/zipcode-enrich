class LocaleInfo:
    distrito: str
    concelho: str

    def __init__(self, distrito: str, concelho: str):
        if not (len(distrito) > 0 and len(concelho) > 0):
            raise Exception("distrito and concelho must be strings with non-zero length")

        self.distrito = distrito.lower()
        self.concelho = concelho.lower()

    def __str__(self):
        return f"Distrito: {self.distrito}; Concelho: {self.concelho}"

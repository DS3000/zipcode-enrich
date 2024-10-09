class LocaleInfo:
    distrito: str
    concelho: str

    def __init__(self, distrito: str, concelho: str):
        self.distrito = distrito.lower()
        self.concelho = concelho.lower()

    def __str__(self):
        return f"Distrito: {self.distrito}; Concelho: {self.concelho}"

class WikiException(Exception):
    def __init__(self, code, e):
        super().__init__(e)
        self.code = code

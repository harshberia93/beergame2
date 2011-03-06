class InvalidStateChange(Exception):
    """If a player whose current state attempts to change from,
    for example, step1 to order will throw this exception"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

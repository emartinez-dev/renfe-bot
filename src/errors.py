"""All exceptions for RenfeBot"""

class RenfeBotException(BaseException):
    """Base exception for the rest of the program"""
    pass


class StationNotFound(RenfeBotException):
    """Raise when the station provided is not found at the Stations file"""
    pass

class InvalidDWRToken(RenfeBotException):
    """Raise when the DWR token provided is invalid"""
    pass
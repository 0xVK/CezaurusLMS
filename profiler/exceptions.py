from django.db import IntegrityError


class AlreadyExistsError(IntegrityError):
    """Friend request already exists"""
    def __init__(self, message):
        self.message = message


class AlreadyFriendsError(IntegrityError):
    """Users is already friends"""
    def __init__(self, message):
        self.message = message


class AlreadySentRequestToYouError(IntegrityError):
    """User already sent request to you"""
    def __init__(self, message):
        self.message = message


from django.db import IntegrityError


class InviteAlreadyExistsError(IntegrityError):
    """Community Invite already exists"""
    def __init__(self, message):
        self.message = message


class AlreadyMemberError(IntegrityError):
    """Users is already community member"""
    def __init__(self, message):
        self.message = message


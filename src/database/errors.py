

class DBError(Exception):
    pass


class CommitError(DBError):
    """Occures on database commitment"""


class RollbackError(DBError):
    "Occurs on database rollback"
    
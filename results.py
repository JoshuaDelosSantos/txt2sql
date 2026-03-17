class EntityResult(list):
    """A list of entity names that also carries token usage metadata.

    Behaves identically to a plain list for all existing callers.
    The API layer can read .usage to get the raw usage_metadata dict.
    """

    def __init__(self, entities, usage=None):
        super().__init__(entities)
        self.usage = usage


class SQLResult(str):
    """A SQL string that also carries token usage metadata.

    Behaves identically to a plain str for all existing callers.
    The API layer can read .usage to get the raw usage_metadata dict.
    """

    def __new__(cls, sql, usage=None):
        instance = super().__new__(cls, sql)
        instance.usage = usage
        return instance
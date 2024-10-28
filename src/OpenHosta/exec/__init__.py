PREFIX = "\033[0m\033[32m\033[1mHostaExec \033[33m(%s)\033[32m |\033[0m"

def prefix(value):
    """
    Returns the formatted prefix with the provided value.

    :param value: The value to insert into the prefix.
    :return: The formatted prefix.
    """
    return PREFIX % value

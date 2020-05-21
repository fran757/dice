"""Data representation method."""


def report(title, data, message, file=None):
    """Present data in custom message.
    data should be a dictionnary, and the message formats every key, value pair.
    """
    if not file:
        print(f"\033[1m{title}\033[0m")
        message = "    " + message
    if not data:
        print("    Nothing to report")
    for key, value in data.items():
        print(message.format(key=key, value=value), file=file)

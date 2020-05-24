"""Data representation method."""


def report(title, data, message, file=None):
    """Present data in custom message.
    data should be a dictionnary, and the message formats every (key, value) pair.
    """
    if not file:
        print(f"\033[1m{title}\033[0m")
        message = "    " + message
    if not data:
        print("    Nothing to report")
    for key, value in data.items():
        print(message.format(key=key, value=value), file=file)

def table(title, data, output=None):
    """Report data in a table format."""
    width       = max([len(str(x)) for entry in data.values() for x in entry])
    columns     = len(list(data.values())[0])
    label_width = max([len(key) for key in data.keys()])
    label       = f"{{key:<{label_width}}} |"
    cells       = " ".join([f"{{value[{i}]:<{width}}}" for i in range(columns)])
    message = "{{l}} {{c}}".format(l=label, c=cells)
    report(title, data, f"{label} {cells}", output)

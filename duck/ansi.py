import re


ANSI_REMOVAL_PATTERN = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")


def remove_ansi_escape_codes(lines):
    return [ANSI_REMOVAL_PATTERN.sub("", line) for line in lines]


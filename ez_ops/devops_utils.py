import re
import sys
from enum import Enum
from typing import Any, List, Literal


__FIRST_PRINTOUT: bool = True
__PREV_COMMAND_NUM_LINES: int = 0
__DEBUG_TPRINT_MODE: bool = False


def count_references_in_str(s: str, substring: str) -> int:
    return len([m.start() for m in re.finditer(substring, s)])


def tprint(
    *values: object,
    new_section: bool = False,
    callout: bool = False,
    callout_str: str = "-",
    indent: bool = False,
    indent_amt: int = 3,
    header: bool = False,
    header_str: str = "=",
    sep: str = " ",
    end: str = "\n",
    flush: Literal[False] = False,
) -> int:
    global __FIRST_PRINTOUT
    global __PREV_COMMAND_NUM_LINES

    num_lines: int = 0
    callout_str = max(len(str(value)) for value in values) * callout_str
    if indent:
        callout_str = indent_amt * " " + callout_str
        values = tuple(indent_amt * " " + f"{value}" for value in values)

    if __FIRST_PRINTOUT:
        new_section = False
        __FIRST_PRINTOUT = False
    if new_section:
        num_lines += 1
        print("")
    if callout:
        num_lines += 1
        print(callout_str)

    if header:
        print(header_str * 10, *values, header_str * 10, sep=sep, end=end, flush=flush)
        __FIRST_PRINTOUT = True
    else:
        print(*values, sep=sep, end=end, flush=flush)
    num_lines += count_references_in_str(sep, "\n") * len(
        values
    ) + count_references_in_str(end, "\n")
    if callout:
        num_lines += 1
        print(callout_str)

    __PREV_COMMAND_NUM_LINES = num_lines
    return num_lines


def toggle_debug_mode(mode: bool | None = None) -> None:
    global __DEBUG_TPRINT_MODE
    if mode is not None:
        __DEBUG_TPRINT_MODE = mode
    else:
        __DEBUG_TPRINT_MODE = not __DEBUG_TPRINT_MODE
    Colors.BRIGHT_MAGENTA.tprint(
        f"SETTING DEBUG MODE TO {__DEBUG_TPRINT_MODE}", callout=True
    )


def debug_tprint(
    *values: object,
    new_section: bool = False,
    callout: bool = False,
    callout_str: str = "-",
    indent: bool = False,
    indent_amt: int = 3,
    header: bool = False,
    header_str: str = "=",
    sep: str = " ",
    end: str = "\n",
    flush: Literal[False] = False,
) -> int:
    if __DEBUG_TPRINT_MODE:
        return tprint(
            *values,
            new_section=new_section,
            callout=callout,
            callout_str=callout_str,
            indent=indent,
            indent_amt=indent_amt,
            header=header,
            header_str=header_str,
            sep=sep,
            end=end,
            flush=flush,
        )
    return 0


def clear_lines(num_lines: int | None) -> None:
    if num_lines is None:
        num_lines = __PREV_COMMAND_NUM_LINES
    for _ in range(num_lines):
        print("\033[1A", end="\x1b[2K")


class Colors(Enum):
    NORMAL: str = "\033[0m"
    BOLD: str = "\033[1m"
    ITALIC: str = "\033[3m"
    GREEN: str = "\033[32m"
    BLUE: str = "\033[34m"
    CYAN: str = "\033[36m"
    RED: str = "\033[31m"
    MAGENTA: str = "\033[35m"
    BRIGHT_MAGENTA: str = "\033[95m"
    UNDERLINE: str = "\033[4m"
    BRIGHT_RED: str = "\033[91m"
    YELLOW: str = "\033[33m"
    HGREEN: str = "\033[42m"
    HYELLOW: str = "\033[103m"
    HCYAN: str = "\033[106m"
    HMAGENTA: str = "\033[105m"
    BLACK: str = "\033[30m"

    @staticmethod
    def color(s: Any, *color_ls: "Colors") -> str:
        color_ls_str = "".join([color.value for color in color_ls])
        return f"{color_ls_str}{s}{Colors.NORMAL.value}"

    def color(self, s: Any, *others: "Colors") -> str:
        return self.color(s, self, *others)

    def tprint(
        self,
        s: str,
        *others: "Colors",
        new_section: bool = False,
        indent: bool = False,
        indent_amt: int = 3,
        callout: bool = False,
        header: bool = False,
        header_str: str = "=",
        sep: str = " ",
        end: str = "\n",
    ) -> int:
        return tprint(
            self.color(s, *others),
            new_section=new_section,
            callout=callout,
            sep=sep,
            end=end,
            indent=indent,
            indent_amt=indent_amt,
            header=header,
            header_str=header_str,
        )


class Shapes(Enum):
    GREEN_CIRCLE = chr(128994)
    RED_CIRCLE = chr(128308)
    ORANGE_CIRCLE = chr(128992)
    REVOLVING_ARROW = " " + chr(8635)
    RED_X = chr(10060)
    QUESTION = chr(10067)


def prompt_user_confirm(
    prompt: str,
    default_confirm: bool = False,
    exit_on_false: bool = False,
    new_section: bool = True,
) -> bool:
    tprint("", new_section=new_section, end="")
    ending = "(Y/n)" if default_confirm else "(y/N)"
    resp = input(f"{prompt.strip()} {ending} ").strip().lower()
    confirmation: bool
    if default_confirm:
        confirmation = resp == "y" or resp == ""
    else:
        confirmation = resp == "y"

    if exit_on_false and not confirmation:
        sys.exit("Operation canceled by user.")

    return confirmation


def grep(full_str: str, search_str: str) -> List[str]:
    return [line for line in full_str.splitlines() if search_str in line]
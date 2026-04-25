"""終端輸出工具：統一顏色與訊息格式。"""

import sys

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"


def color_text(text: str, color: str) -> str:
    """套用 ANSI 顏色。"""
    return f"{color}{text}{COLOR_RESET}"


def print_success(text: str) -> None:
    print(color_text(text, COLOR_GREEN))


def print_warn(text: str) -> None:
    print(color_text(text, COLOR_YELLOW))


def print_error(text: str, to_stderr: bool = False) -> None:
    if to_stderr:
        print(color_text(text, COLOR_RED), file=sys.stderr)
        return
    print(color_text(text, COLOR_RED))


from typing import Union, Literal, Optional
from enum import Enum
import platform

IS_UNIX = platform.system() != "Windows"

class ANSIColor(Enum):
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bold colors
    BLACK_BOLD = '\033[1;30m'
    RED_BOLD = '\033[1;31m'
    GREEN_BOLD = '\033[1;32m'
    YELLOW_BOLD = '\033[1;33m'
    BLUE_BOLD = '\033[1;34m'
    PURPLE_BOLD = '\033[1;35m'
    CYAN_BOLD = '\033[1;36m'
    WHITE_BOLD = '\033[1;37m'

    # Bright (light) colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'  # Bright/Light Green
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_PURPLE = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    UNDERLINE = '\033[4m'
    REVERSED = '\033[7m'

class Logger:
    def __init__(self, log_file_path: Optional[str] = None, verbose: Union[Literal[0, 1, 2], bool] = 2):
        self.log_file_path: Optional[str] = log_file_path
        if log_file_path:
            self.log_file = open(log_file_path, "w")
            self.log_file.close()
        self.verbose = verbose if isinstance(verbose, int) else 2 if verbose else 0
        assert self.verbose is not None and 0 <= self.verbose <= 2, "Please provide a valid verbose level (0, 1 or 2) default is 2"

    def _log(
            self,
            prefix: str,
            message: str,
            level: int = 1,
            color: ANSIColor = ANSIColor.BRIGHT_GREEN,
            text_color: ANSIColor = ANSIColor.RESET,
            one_line : bool = False
    ):
        """
        Internal logging method.
        :param prefix: The prefix for the log message
        :param message: The message to log
        :param level: The verbose level (0: Essential, 1: Normal, 2: Debug)
        :param color: The color to use for the prefix
        """
        if level <= self.verbose:
            if one_line and IS_UNIX:
                print(f"{ANSIColor.RESET.value}[{color.value}{prefix}{ANSIColor.RESET.value}] {text_color.value}{message}", end="\r")
            else:
                print(f"{ANSIColor.RESET.value}[{color.value}{prefix}{ANSIColor.RESET.value}] {text_color.value}{message}")
        if self.log_file_path:
            with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"[{prefix}] {message}" + "\n")

    def log_error(self, message: str, level: int = 1):
        self._log("Error", message, level, ANSIColor.BRIGHT_RED, ANSIColor.BRIGHT_RED)

    def log_critical(self, message: str, level: int = 1):
        self._log("Critical", message, level, ANSIColor.RED, ANSIColor.BRIGHT_RED)

    def log_exception(self, exception: Exception, level: int = 1):
        self._log("Exception", str(exception), level, ANSIColor.BRIGHT_RED, ANSIColor.BRIGHT_RED)

    def log_warning(self, message: str, level: int = 1):
        self._log("Warning", message, level, ANSIColor.BRIGHT_YELLOW, ANSIColor.BRIGHT_YELLOW)

    def log_info(self, message: str, level: int = 1):
        self._log("Info", message, level, ANSIColor.BRIGHT_BLUE)

    def log_success(self, message: str, level: int = 1):
        self._log("Success", message, level, ANSIColor.BRIGHT_GREEN)

    def log_debug(self, message: str, level: int = 2):
        self._log("Debug", message, level, ANSIColor.BRIGHT_PURPLE)

    def log_verbose(self, message: str, level: int = 2):
        self._log("Verbose", message, level, ANSIColor.BRIGHT_CYAN)

    def log_custom(
            self,
            prefix: str,
            message: str,
            level: int = 1,
            color: ANSIColor = ANSIColor.BRIGHT_GREEN,
            text_color: ANSIColor = ANSIColor.RESET,
            one_line : bool = False
    ):
        self._log(prefix, message, level, color, text_color, one_line)

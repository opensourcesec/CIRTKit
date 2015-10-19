# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from colorama import Fore, Style


def color(text, color_code, readline=False):
    """Colorize text.
    @param text: text.
    @param color_code: color.
    @return: colorized text.
    """

    if readline:
        # special readline escapes to fix colored input promps
        # http://bugs.python.org/issue17337
        return "\x01\x1b[%dm\x02%s\x01\x1b[0m\x02" % (color_code, text)

    return "\x1b[%dm%s\x1b[0m" % (color_code, text)

def red(text, readline=False):
    return Fore.RED + str(text) + Fore.RESET

def green(text, readline=False):
    return Fore.GREEN + str(text) + Fore.RESET

def yellow(text, readline=False):
    return Fore.YELLOW + str(text) + Fore.RESET

def blue(text, readline=False):
    return Fore.BLUE + str(text) + Fore.RESET

def magenta(text, readline=False):
    return Fore.MAGENTA + str(text) + Fore.RESET

def cyan(text, readline=False):
    return Fore.CYAN + str(text) + Fore.RESET

def white(text, readline=False):
    return Fore.WHITE + str(text) + Fore.RESET

def bold(text, readline=False):
    return Style.BRIGHT + str(text) + Style.RESET_ALL

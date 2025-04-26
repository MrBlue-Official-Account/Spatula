"""
    # Banner
"""
from colorama import Fore, Style

BRIGHT = Style.BRIGHT
RED = Fore.RED
BLUE = Fore.BLUE
CYAN = Fore.CYAN
WHITE = Fore.WHITE
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
MAGENTA = Fore.MAGENTA
RESET = Fore.RESET

BANNER = f"""\t      {BRIGHT}{BLUE}_____{RESET}
        {BRIGHT}{BLUE}╔═╗┌─┐|\\|/|┬ ┬┬  ┌─┐{RESET}
        {BRIGHT}{WHITE}╚═╗├─┘ |@| │ ││  ├─┤
        ╚═╝┴   |_| └─┘┴─┘┴ ┴
            {GREEN}\\ v.1.2.0 /{RESET}"""

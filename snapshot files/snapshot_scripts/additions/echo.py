import subprocess


class EchoStyles:
    DEFAULT = '\\e[0m'
    RED = '\\e[31m'
    GREEN = '\\e[32m'
    BLUE = '\\e[34m'
    CYAN = '\\e[36m'
    BOLD = '\\e[1m'
    CLEARBOLD = '\\e[22m'
    UNDERLINE = '\\e[4m'
    CLEARUNDERLINE = '\\e[24m'
    INVERT = '\\e[7m'
    pass

def CombineEchoStyles(*styles: str):
    if len(styles) == 0:
        return

    newStyles = styles[0]

    i = 1
    while i < len(styles):
        newStyles += ';' + (styles[i].replace("\\e[", ''))
        i += 1
        pass
    newStyles = newStyles.replace('m', '')
    
    return newStyles + 'm'
    
def Echo(printLine, colorcode=EchoStyles.DEFAULT): # stdout=subprocess.PIPE
    command = f'echo -e "{colorcode}{printLine}{EchoStyles.DEFAULT}"'
    
    echo = subprocess.Popen(command, shell=True, universal_newlines=True)

    echo.communicate()
    pass


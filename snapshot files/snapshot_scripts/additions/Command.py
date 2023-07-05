import subprocess

def RunCommand(command, useOutput=True):
    if not useOutput: command = f"{command}> /dev/null"
    
    proc = subprocess.Popen(command, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = proc.communicate()
    
    return out, err
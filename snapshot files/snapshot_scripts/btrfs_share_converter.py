import sys
import os
import string
import random

from sys import argv
from time import sleep
from additions.Command import RunCommand
from additions.AllDisks import GetDiskArray
from additions.echo import Echo, EchoStyles, CombineEchoStyles


convertingAll = False
if len(argv) <= 1 or argv[1] == '':
    Echo("You need to pass the name of the share to convert as an argument.")
    Echo("Use the '-all' argument to convert all the shares to btrfs.")
    exit(0)

shareList = []

# share = None
if argv[1].lower() == "-all":
    convertingAll = True
    path = "/mnt/user"
    for dir in os.listdir(path):
        if dir == ".snapshots": continue
        
        if os.path.isdir(os.path.join(path, dir)):
            shareList.append(dir)
        pass
else:
    s = os.path.basename(argv[1])# just in case the full path is passed through
    s = s.replace('/', '')
    shareList.append(s)

# check if share exists
if not convertingAll:
    shareExists = shareList[0] in os.listdir("/mnt/user")
    if not shareExists:
        Echo(f"Can't find any share with the name {shareList[0]}", EchoStyles.RED)
        Echo("Shares are case-sensitive")
        exit(0)

diskArray = GetDiskArray(True)

for share in shareList:
    for disk in diskArray:
        path = f"{disk}/{share}"

        # skip this disk if it's already a btrfs subvolume
        directoryNum,err = RunCommand(f'stat --format=%i "{disk}/{share}"')
        directoryNum = directoryNum.replace('\n', '')
        if directoryNum == str(256):
            Echo(f"{EchoStyles.UNDERLINE}{path}{EchoStyles.CLEARUNDERLINE} is already a btrfs subvolume. (skipping conversion)", EchoStyles.GREEN)
            continue

        # create subvolume if nothing exists for the path
        if not os.path.exists(path):
            RunCommand(f'btrfs sub create "{path}"')
            Echo(f"{EchoStyles.UNDERLINE}{path}{EchoStyles.CLEARUNDERLINE} was converted to a btrfs subvolume.", EchoStyles.GREEN)
            continue
        else:
            # replace the share if it is empty
            if len(os.listdir(path)) == 0:
                RunCommand(f'rmdir "{path}"')
                RunCommand(f'btrfs sub create "{path}"')
                Echo(f"{EchoStyles.UNDERLINE}{path}{EchoStyles.CLEARUNDERLINE} was converted to a btrfs subvolume.", EchoStyles.GREEN)
                continue
        
        # generate random name
        letters = string.ascii_lowercase
        rand = ''.join(random.choice(letters) for i in range(10))

        # move share to temp directory
        tempPath = f"{disk}/{rand}"
        RunCommand(f'mv -v "{path}" "{tempPath}"')
        
        # create sub volume
        RunCommand(f'btrfs sub create "{path}"')

        # move data back to share
        RunCommand(f'cp -R --reflink=always "{tempPath}"/* "{path}"')

        # remove temp share
        RunCommand(f'rm -r "{tempPath}"')

        # RunCommand("sleep 1")

        # remove share config file
        config = f"/boot/config/shares/{rand}.cfg"
        timeoutLimit = 6
        timer = 0
        while not os.path.exists(config):
            if timer > timeoutLimit:
                break
            timer += .1
            sleep(.1)

        if os.path.exists(config):
            out, err = RunCommand(f'rm "{config}"')

            if len(out) != 0:
                print(f"output: {len(out)}")
                Echo(out)
            if len(err) != 0:
                print(f"output: {len(err)}")
                Echo(err, EchoStyles.RED)
            pass
        
        Echo(f"{EchoStyles.UNDERLINE}{path}{EchoStyles.CLEARUNDERLINE} was converted to a btrfs subvolume.", EchoStyles.GREEN)
        pass
    Echo("")
    pass
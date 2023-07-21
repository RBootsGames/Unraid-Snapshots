import os

from additions.Command import RunCommand
from additions.AllDisks import GetDiskArray
from additions.echo import Echo, EchoStyles, CombineEchoStyles

def CheckShares():

    diskArray = GetDiskArray(True)

    for disk in diskArray:
        print()
        Echo(disk, CombineEchoStyles(EchoStyles.BOLD, EchoStyles.UNDERLINE))

        shareList = os.listdir(disk)
        for share in shareList:
            if share == ".snapshots": continue
            directoryNum,err = RunCommand(f'stat --format=%i "{disk}/{share}"')
            directoryNum = directoryNum.replace('\n', '')
            
            if directoryNum == str(256):
                Echo(f" +-----|{share.ljust(15)}| Ready to create snapshots", EchoStyles.GREEN)
            else:
                Echo(f" +-----|{share.ljust(15)}| Must be converted to btrfs subvolume first", EchoStyles.RED)
            pass
        pass
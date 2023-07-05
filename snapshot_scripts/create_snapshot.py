# import subprocess
import os
import datetime

from sys import argv
from os.path import basename
from pathlib import Path
from additions.xml_controls import XmlControls
from additions.echo import Echo, EchoStyles, CombineEchoStyles
from additions.AllDisks import GetDiskArray
from additions.Command import RunCommand




shareName = ""
snapshotName = ""
retentionPeriod = ""
# this will get rid of empty arguments
args = [i for i in argv if i]

if len(args) >= 4:
    snapshotName = args[3]
    retentionPeriod = args[2]
    shareName = args[1]
    pass
elif len(args) == 3:
    retentionPeriod = args[2]
    shareName = args[1]
    pass
elif len(args) == 2:
    shareName = args[1]
    pass
else:
    Echo("Usage:")
    Echo("  create <share name> [retention period] [snapshot name]", EchoStyles.CYAN)
    Echo("  The retention period and snapshot name are optional", EchoStyles.BOLD)
    Echo("Retention period will default to infinite.\nAssign duration with <number>'d' 'm' 'y'. If only the number is provided it will default to days.")
    Echo("Without a snapshot name, it will default to using the timestamp as the name.")
    exit(0)
    pass

fullPath = f"/mnt/user/{shareName}"

if not os.path.exists(fullPath):
    Echo("Share not found", EchoStyles.RED)
    Echo("Make sure you are only using the name of the share. Share names are case-sensitive. Check spelling and try again.")
    exit(0)
    pass

diskArray = GetDiskArray()


timeStamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
# Load the xml file
snapCreated = False
xml = XmlControls()

if snapshotName != "":
    snapshotName = xml.CheckName(snapshotName)
else:
    snapshotName = timeStamp



for disk in diskArray:
    path = f"/mnt/{disk}/{shareName}"
    
    # skip share if it doesn't exist on this disk
    if not os.path.exists(path):
        continue

    # check if the share is actually a btrfs subvolume capable of snapshotting
    dirId,err = RunCommand(f'stat --format=%i "{path}"')
    dirId = dirId.replace('\n', '')

    if dirId != str(256):
        Echo(f"{path}/  Snapshot failed. You need to convert this share to btrfs before snapshots can be created.", EchoStyles.RED)
        continue
        

    # create .snapshots subvolume if it doesn't exist
    snapPath = f"/mnt/{disk}/.snapshots"
    if not os.path.exists(snapPath):
        RunCommand(f'btrfs sub create "{snapPath}"')
        Echo(f"Created subvolume {EchoStyles.BOLD}.snapshots{EchoStyles.DEFAULT} in {EchoStyles.BOLD}/mnt/{disk}/")
        pass
    
    
    snapPath += f"/{shareName}" #eg. /mnt/disk1/.snapshots/appdata
    #create share snapshot folder if it doesn't exist
    if not os.path.exists(snapPath):
        RunCommand(f'btrfs sub create "{snapPath}"')
        Echo(f"Created subvolume {EchoStyles.BOLD}{shareName}{EchoStyles.DEFAULT} in {EchoStyles.BOLD}/mnt/{disk}/.snapshots/")
        pass


                                                                        #  custom_name
                                        #eg  /mnt/disk1/.snapshots/appdata/2020-11-20_12:30:00
    # create snapshot       #eg. /mnt/disk1/appdata
    RunCommand(f'btrfs sub snap "{path}" "{snapPath}/{snapshotName}"')

    Echo(f"Created snapshot {CombineEchoStyles(EchoStyles.UNDERLINE, EchoStyles.GREEN)}{snapshotName}{EchoStyles.DEFAULT} in {EchoStyles.BOLD}{snapPath}")
    snapCreated = True
    pass

if snapCreated:
    # update the xml file with the new snapshot information
    xml.AddSnapshot(shareName, timeStamp, retentionPeriod, snapshotName)
    xml.SaveXml()
import subprocess
import sys
import os

from os.path import basename
from additions.AllDisks import GetDiskArray
from additions.echo import Echo, EchoStyles, CombineEchoStyles
from additions.xml_controls import XmlControls
from additions.snapinfo import Snapshot



def Usage():
    Echo("Usage:")
    Echo(f"  remove <ID/'retention'>")
    Echo("  Entering in an ID will remove the snapshot associated with that ID.")
    Echo("  Entering 'retention' will remove snapshots based on their retention period")
    Echo("  Add '-y' at then end to skip the removal confirmation.")
    exit(0)

def Remove(index):
    try:
        snapName = xml.snapshotList[index].Name
        shareName = xml.snapshotList[index].Share
        xml.RemoveSnapshot(index)
    except:
        Echo(f"Can't find snapshot with ID of {index}", EchoStyles.RED)
        exit(0)
    
    diskArray = GetDiskArray()

    for disk in diskArray:
        path = f"/mnt/{disk}/.snapshots/{shareName}/{snapName}"
        if os.path.exists(path):
            command = f'btrfs sub delete "{path}"> /dev/null'
            subvolume = subprocess.Popen(command, shell=True)
            subvolume.communicate()
        pass

    Echo(f"Deleted snapshot {EchoStyles.BOLD}{snapName}{EchoStyles.DEFAULT} for share {EchoStyles.BOLD}{shareName}")
    xml.SaveXml()

    pass


removeID = -1
preApproved = False
removingRetention = False
if len(sys.argv) > 1:
    try:
        removeID = int(sys.argv[1])
    except:
        if sys.argv[1] == "retention":
            removingRetention = True
        else:
            Usage()
    
    if sys.argv[2].lower() == '-y':
        preApproved = True
else:
    Usage()

# confirm restore
gettingAnswer = True
while preApproved == False and gettingAnswer:
    ask = "Are you sure you want to remove this snapshot? (y/n): " if not removingRetention else "Are you sure you want to remove snapshots based on their retention period? (y/n): "
    ans = input(ask)

    if ans.lower() == 'n':
        Echo("Removal canceled.")
        exit(0)
    elif ans.lower() == 'y':
        Echo("continuing")
        Echo("removing snapshot(s)", EchoStyles.CYAN)
        gettingAnswer = False
    pass

if preApproved and gettingAnswer:
    Echo("removing snapshot(s)", EchoStyles.CYAN)

xml = XmlControls()

if removingRetention:
    removers = []
    for snap in xml.snapshotList:
        snap: Snapshot
        if snap.CheckPastRetention(): removers.append(snap)
        pass
    removers.reverse()

    for rem in removers:
        rem: Snapshot
        Remove(int(rem.Index))
    exit(0)
else:
    Remove(removeID)
    pass

import subprocess
import sys
import os

from os.path import basename
from additions.AllDisks import GetDiskArray
from additions.echo import Echo, EchoStyles, CombineEchoStyles
from additions.xml_controls import XmlControls
from additions.snapinfo import Snapshot


xml:XmlControls

def Usage():
    Echo("Usage:")
    Echo(f"  remove <ID/'retention'>")
    Echo("  Entering in an ID will remove the snapshot associated with that ID.")
    Echo("  Entering 'retention' will remove snapshots based on their retention period")
    Echo("  Add '-y' at then end to skip the removal confirmation.")
    sys.exit()
    
def DoRemove(index):
    global xml

    try:
        snapName = xml.snapshotList[index].Name
        shareName = xml.snapshotList[index].Share
        xml.RemoveSnapshot(index)
    except:
        Echo(f"Can't find snapshot with ID of {index}", EchoStyles.RED)
        sys.exit()
    
    diskArray = GetDiskArray()

    for disk in diskArray:
        path = f"/mnt/{disk}/.snapshots/{shareName}/{snapName}"
        if os.path.exists(path):
            command = f'btrfs sub delete "{path}"> /dev/null'
            subvolume = subprocess.Popen(command, shell=True)
            subvolume.communicate()
        pass
    
    # remove empty directory if there are no snapshots for a share
    if len(os.listdir(f"/mnt/user/.snapshots/{shareName}")) == 0:
        os.rmdir(f"/mnt/user/.snapshots/{shareName}")

    Echo(f"Deleted snapshot {EchoStyles.BOLD}{snapName}{EchoStyles.DEFAULT} for share {EchoStyles.BOLD}{shareName}")
    xml.SaveXml()

    pass



def RemoveSnapshot(a1, a2):
    global xml

    if a1 == None:
        Usage()
    
    removeID = -1
    preApproved = False
    removingRetention = False
    try:
        removeID = int(a1)
    except:
        if a1 == "retention":
            removingRetention = True
        else:
            Usage()
    
    if a2 != None and a2.lower() == '-y':
        preApproved = True

    # confirm restore
    gettingAnswer = True
    while preApproved == False and gettingAnswer:
        ask = "Are you sure you want to remove this snapshot? (y/n): " if not removingRetention else "Are you sure you want to remove snapshots based on their retention period? (y/n): "
        ans = input(ask)

        if ans.lower() == 'n':
            Echo("Removal canceled.")
            sys.exit()
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
            DoRemove(int(rem.Index))
        sys.exit()
    else:
        DoRemove(removeID)
        pass

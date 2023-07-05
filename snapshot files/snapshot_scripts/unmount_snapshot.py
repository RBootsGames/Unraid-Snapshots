import os
from sys import argv

from additions.snapinfo import Snapshot
from additions.Command import RunCommand
from additions.AllDisks import GetDiskArray
from additions.xml_controls import XmlControls
from additions.echo import Echo, EchoStyles, CombineEchoStyles

def Usage():
    Echo("Usage:")
    Echo("  unmount <ID>")
    Echo("  Unmounts and removes the created share of a previously mounted snapshot.")
    Echo("  ")
    Echo("Note:")
    Echo("  Get a list of mounted snapshots and their IDs by running snapshot mount list")
    exit(0)
    pass

def UnmountSnapshot(snapId):
    xml = XmlControls()

    if len(xml.snapshotData) == 0:
        print("No snapshots were found.")
        exit(0)

    # if snapId+1 > len(xml.snapshotData):
    snap:Snapshot
    try:
        snap = xml.snapshotList[snapId]
    except IndexError as err:
        Echo(err, EchoStyles.RED)
        exit(0)

    if snap.IsMounted() == False:
        Echo("This snapshot is not currently mounted.")
        exit(0)

    # get mount name
    mountName = snap.GetMountNameFromConfig()
    allDisks = GetDiskArray(True)

    for disk in allDisks:
        mPath = f"{disk}/{mountName}"
        if not os.path.exists(mPath):
            continue
        
        # unmount directory
        RunCommand(f'umount -f "{mPath}"')

        # remove directory
        os.rmdir(f'{mPath}')
        

    # remove .cfg file
    os.remove(f"/boot/config/shares/{mountName}.cfg")

    Echo(f"Successfully unmounted snapshot from share {EchoStyles.BOLD}{mountName}")
    pass

if __name__ == "__main__":
    # this will get rid of empty arguments
    args = [i for i in argv if i]
    
    if len(args) == 1:
        Usage()

    if args[1].isdigit():
        UnmountSnapshot(int(args[1]))
    else:
        Echo("ID needs to be a number.", EchoStyles.RED)
        Usage()
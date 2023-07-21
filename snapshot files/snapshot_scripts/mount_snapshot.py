import os
import sys
from sys import argv

from time import sleep
from additions.snapinfo import Snapshot
from additions.Command import RunCommand
# from additions.AllDisks import GetDiskArray
from additions.xml_controls import XmlControls
from additions.echo import Echo, EchoStyles, CombineEchoStyles



def Usage():
    Echo("Usage:")
    Echo("  mount <ID/'list'> [optional: mountpoint name] [optional: -w]")
    Echo("  This will create a new share using the snapshot specified.")
    Echo("  By default, the snapshot is mounted as a read-only file system.")
    Echo("  In order to mount with write access, add '-w' at then end of your arguments.")
    Echo("Note: The mountpoint will always be placed in '/mnt/user/' and cannot start with a '.'.")
    Echo("  ")
    Echo(f"  {EchoStyles.BOLD}mount list{EchoStyles.CLEARBOLD}")
    Echo("  List all mounted snapshots.")
    sys.exit()
    pass

def ListMounts():
    xml = XmlControls()

    if len(xml.snapshotData) == 0:
        print("No snapshots were found.")
        sys.exit()

    mountedSnapshots = xml.GetMountedSnapshots()
    
    if len(mountedSnapshots) == 0:
        print("No mounted snapshots were found.")
        sys.exit()
    else:
        Echo("  ID   Snapshot Name        Mount Name                  ", EchoStyles.UNDERLINE)
    for snap in mountedSnapshots:
        snap:Snapshot
        print(f'  {str(snap.Index).ljust(5)}{snap.Share.ljust(16)}->   {snap.GetMountNameFromConfig()}')

    pass

def MountSnapshot(snapID:int, mountPoint=None, mountAsReadOnly=True):
    if snapID == None:
        Usage()
    if mountPoint == "-w":
        mountPoint = None

    if mountPoint != None:
        if '/' in mountPoint:
            Echo("  The mountpoint cannot contain a '/'.", EchoStyles.RED)
            Echo("  The mountpoint will always be placed in '/mnt/user/'.")
            sys.exit()
        elif mountPoint.startswith('.'):
            Echo("  The mountpoint cannot start with '.' because those directories are hidden.")
            sys.exit()


    xml = XmlControls()
    
    for snap in xml.GetMountedSnapshots():
        if int(snap.Index) == int(snapID):
            Echo("This snapshot is already mounted", EchoStyles.BOLD)
            sys.exit()

    if len(xml.snapshotData) == 0:
        Echo("No snapshots found.", EchoStyles.RED)
        sys.exit()
    elif snapID >= len(xml.snapshotList):
        Echo(f"ID {snapID} could not be found.", EchoStyles.BOLD)
        sys.exit()

    snap:Snapshot
    snap = xml.snapshotList[snapID]
    
    if mountPoint == None:
        mountPoint = snap.GetMountableName();
    else:
        mountPoint = mountPoint.replace(":", "-")
    # The filter gets rid of '.snapshots' and other hidden shares.
    shareList = list(filter(lambda sh: sh.startswith('.') == False, os.listdir("/mnt/user")))


    if mountPoint in shareList: # can't mount
        Echo("The share '" + mountPoint + "' already exists. Pick a mountpoint that doesn't already exist.", EchoStyles.RED)
        Echo("If you want to replace an existing share, use 'snapshot restore' to replace the cooresponding share.")
        sys.exit()


    # mountPath = f"/mnt/user/{mountPoint}"
    allSourcePaths = snap.GetSnapshotPath(True)
    
    for src in allSourcePaths:
        mPath = src.split("/.snapshots")[0]
        mPath += "/" + mountPoint
        
        # make directory to mount to first
        os.mkdir(f"{mPath}")
        if mountAsReadOnly:
            RunCommand(f'mount -Br "{src}" "{mPath}"')
        else:
            RunCommand(f'mount -B "{src}" "{mPath}"')
    
    

    # wait until the config file gets created by unraid
    cfgLocation = f"/boot/config/shares/{mountPoint}.cfg"
    timeoutLimit = 6
    timer = 0
    while not os.path.exists(cfgLocation):
        if timer > timeoutLimit:
            Echo("Couldn't find the config file for the share, but it was successfully mounted.", EchoStyles.RED)
            Echo(f"Snapshot for {snap.Share} mounted at {mountPoint}", EchoStyles.GREEN)
            return
        timer += .1
        sleep(.1)
    
    # change config to export it, set it to public and add a comment
    cfgData = []
    with open(cfgLocation, "r") as cfg:
        cfgData = cfg.read().split("\n")
    for i in range(len(cfgData)):
        if "shareExport=" in cfgData[i]:
            cfgData[i] = 'shareExport="e"' # enables share export for smb
        elif "shareSecurity=" in cfgData[i]:
            cfgData[i] = 'shareSecurity="public"' # changes security to public
        elif "shareComment=" in cfgData[i]:
            cfgData[i] = f'shareComment="Mount for: {snap.GetMountableName()}' # adds a comment that helps identify the mount point


    with open(cfgLocation, "w") as cfg:
        cfg.write("\n".join(cfgData))
    
    finalText = f"Snapshot for {snap.Share} mounted at {mountPoint}"
    if mountAsReadOnly:
        finalText += f" with {EchoStyles.BOLD}read-only{EchoStyles.CLEARBOLD} access"
    else:
        finalText += f" with {EchoStyles.BOLD}write{EchoStyles.CLEARBOLD} access"
    Echo(finalText, EchoStyles.GREEN)
    pass


# def RunCommand(a1, a2, a3):
#     isReadOnly = not (a2 == "-w" or a3 == "-w")
    # if not isReadOnly:
    #     args = args[:-1]
    # if a1 == None:
    #     Usage()
    
    # if a1 == "list":
    #     ListMounts()

    # try:
    #     snapID = int(a1)
    # except: Usage()

    # mountPoint = a2

    # MountSnapshot(snapID, mountPoint, isReadOnly)

    # if len(args) == 2:
    #     if args[1] == "list":
    #         ListMounts()
    #     elif args[1].isdigit():
    #         MountSnapshot(int(args[1]))
    #     else:
    #         Usage()
        
    #     sys.exit()
    # elif len(args) > 2:
    # if a3 != None:
    #     snapID = -1
    #     mountPoint:str
    #     try:
    #         snapID = a1
    #     except: Usage()

        
    #     # if '/' in a2:
    #     #     Echo("  The mountpoint cannot contain a '/'.", EchoStyles.RED)
    #     #     Echo("  The mountpoint will always be placed in '/mnt/user/'.")
    #     #     sys.exit()
    #     # elif a2.startswith('.'):
    #     #     Echo("  The mountpoint cannot start with '.' because those directories are hidden.")
    #     #     sys.exit()
    #     # else:
    #     #     mountPoint = a2

    #     MountSnapshot(snapID, mountPoint, isReadOnly)
    # else:
    #     Usage()

import os
import sys

from os.path import basename
from additions.echo import Echo, EchoStyles, CombineEchoStyles
from additions.AllDisks import GetDiskArray
from additions.xml_controls import XmlControls
from additions.snapinfo import Snapshot
from additions.Command import RunCommand


def Usage():
    Echo("Usage:")
    Echo(f"  restore <ID>")
    Echo("  This will overwrite all the files in the current share.")
    Echo("  If you use '-y' at the end it won't ask for confirmation.")
    exit(0)
    pass

preApproved = False
restoreIndex = -1
if len(sys.argv) > 1:
    try:
        restoreIndex = int(sys.argv[1])
        if sys.argv[2] == '-y': preApproved = True
    except: Usage()
else:
    Usage()

# confirm restore
if not preApproved:
    gettingAnswer = True
    Echo("Restoring a snapshot will overwrite everything in the share without recovery. " +
        "Make sure you want to do this. If you are unsure, you can create a snapshot before restoring this one.",
        CombineEchoStyles(EchoStyles.RED, EchoStyles.BOLD))
    while gettingAnswer:
        ans = input("Are you sure you want to continue? (y/n): ")

        if ans.lower() == 'n':
            Echo("Restoration canceled.")
            exit(0)
        elif ans.lower() == 'y':
            Echo("continuing")
            Echo("Overwiting current share.", EchoStyles.CYAN)
            gettingAnswer = False
        pass
    pass

xml = XmlControls()

restore: Snapshot
try:
    restore:Snapshot = xml.snapshotList[restoreIndex]
except:
    Echo("Can't find a snapshot with ID: " + str(restoreIndex), EchoStyles.RED)

diskarray = GetDiskArray()
for disk in diskarray:
    snapPath = f"/mnt/{disk}/.snapshots/{restore.Share}/{restore.Name}"
    sharePath = f"/mnt/{disk}/{restore.Share}"

    # Remove current share
    out, err = RunCommand(f'rm -r "{sharePath}"')
    if len(err) > 0:
        print(err)
        Echo("Failed to remove " + sharePath, EchoStyles.RED)
        continue

    # Copy snapshot to share
    RunCommand(f"btrfs sub create {sharePath}")
    RunCommand(f"cp -r --reflink=always {snapPath}/. {sharePath}")

    pass
Echo(f'Successfully restored snapshot {EchoStyles.UNDERLINE}{restore.Name}{EchoStyles.CLEARUNDERLINE} '+
     f'for share {EchoStyles.UNDERLINE}{restore.Share}{EchoStyles.CLEARUNDERLINE}', EchoStyles.GREEN)
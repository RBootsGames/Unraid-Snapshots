import sys
from sys import argv
from additions.echo import Echo

from btrfs_share_checker import CheckShares
from btrfs_share_converter import ConvertShares
from create_snapshot import CreateSnapshot
from get_snapshots import ListSnapshots
from remove_snapshot import RemoveSnapshot
import mount_snapshot
import unmount_snapshot

def Usage():
    Echo("Usage:")
    Echo("snapshot <task> [arguments]...")
    Echo("  check   | This will check each share to see if it is capable of")
    Echo("          | creating snapshots for.")
    Echo("          |")
    Echo("  convert | This will convert a share to a btrfs sub volume.")
    Echo("          | This is required in order to create snapshots for a share")
    Echo("          | Use '-all' to convert all existing shares.")
    Echo("          |")
    Echo("  create  | This will create a snapshot for the share specified.")
    Echo("          |")
    Echo("  list    | This will return a list of all the existing snapshots.")
    Echo("          |")
    Echo("  remove  | This will remove the snapshot and it's data based on the")
    Echo("          | ID passed through. Run 'list' to find out what the IDs are.")
    Echo("          | If you use '-y' at the end it won't ask for confirmation.")
    Echo("          |")
    # Echo("  restore | This doesn't work right now")
#    Echo("  restore | This will restore the data from a snapshot to it's original")
#    Echo("          | share.\\e[31;1m This will overwrite the entire share, not just\\e[0m")
#    Echo("          | \\e[31;1mthe files that are affected. You may want to create an\\e[0m")
#    Echo("          | \\e[31;1madditional snapshot of the share if you are unsure.\\e[0m")
    # Echo("          |")
    Echo("  mount   | This will mount a copy of a snapshot as a new share.")
    Echo("          |")
    Echo("  unmount | Unmount a previously mounted snapshot.")
    sys.exit()


if len(argv) == 1:
    Usage()

args = [None,None,None,None]

for a in range(1, len(argv)):
    args[a-1] = argv[a]

command = args[0].lower()

if command == "check":
    CheckShares()
elif command == "convert":
    ConvertShares(args[1])
elif command == "create":
    CreateSnapshot(args[1], args[2], args[3])
elif command == "list":
    ListSnapshots()
elif command == "remove":
    RemoveSnapshot(args[1], args[2])
elif command == "mount":
    if args[1] == "list":
        mount_snapshot.ListMounts()
        sys.exit()
    try:
        snapID = int(args[1])
    except: mount_snapshot.Usage()

    readOnly = not (args[2] == "-w" or args[3] == "-w")
    mount_snapshot.MountSnapshot(snapID, args[2], readOnly)
    pass
elif command == "unmount":
    if args[1] == None or not args[1].isdigit():
        unmount_snapshot.Usage()

    unmount_snapshot.UnmountSnapshot(int(args[1]))
    pass
else:
    Usage()
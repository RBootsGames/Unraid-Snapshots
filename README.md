# Unraid-Snapshots
Helps to create and manage snapshot with Unraid. (Must be using btrfs for the filesystem.)

## features

- Create snapshots of full shares
- Mount snapshots for easier browsing of the files
- See list of all existing snapshots
- Delete snapshots using their IDs


## How to use

Running the snapshot command will show a list of available commands.
Your disks need to be using btrfs as the filesystem because this utilizes features only available using btrfs.

### `snapshot check`
This command will check each share on each disk to see if it is setup for creating snapshots.

### `snapshot convert <share name/-all>`
Run this to convert existing shares to a btrfs subvolume. You can convert one share by passing in the share name as an argument, or all of them by using `-all`.

### `snapshot create <share name> [retention period] [snapshot name]`
Creates a snapshot of a share by passing the name of a share as an argument. You can optionally add a retention period or name for the snapshot. If the snapshot name already exists, it will add a number to it.
Note: Snapshots are not automatically deleted after the retention period has passed. You will need to run `snapshot remove retention` to remove snapshots older than their retention period.

### `snapshot list`
Prints a list of all existing snapshots with their share name and IDs.

### `snapshot remove <ID/'retention'>`
Removes the snapshot associated with the given ID or you can remove snapshots that are passed their retention period using `snapshot remove retention`. This will prompt confirmation by default but it can be skipped by adding `-y` at the end of the command.

### `snapshot mount <ID/list> [mountpoint name] [-w]`
Mounts a snapshot. Use a custom name for the mount point if you don't like the default name it provides. By default, snapshots are mounted as read-only unless -w is provided at the end of the command. Run `snapshot mount list` to get a list of all currently mounted snapshots.

### `snapshot unmount <ID>`
Unmounts a snapshot that was previously mounted.

#### Extra note
**If you add another disk to your array, you will need to run `snapshot convert` again. This is because when Unraid creates a new directory on the new drive it won't create a btrfs sub volume, which is required to make the snapshots work.**

## Building

Build the project by running `pyinstaller --onefile snapshot.py`
You need to have python 3 and pyinstaller installed in order to build the project. This needs to be built on Linux in order build it for Unraid. You can also build the project using Windows WSL.


## Installation Instructions

All you need to do is run the install script and it will create a symlink to the snapshot file in /usr/bin/. It will get uninstalled after a reboot like this though. I recommend installing the User Scripts app (also on the Community Apps page) and creating a script that will run the snapshot installer on the array's first start.
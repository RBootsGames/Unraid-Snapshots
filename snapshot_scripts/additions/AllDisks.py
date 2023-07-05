import os

def GetDiskArray(appendMnt=False):
    diskArray = os.listdir("/mnt")
    removers = []
    i=0
    while i < len(diskArray):
        if not (("disk" in diskArray[i] or "cache" in diskArray[i]) and not "disks" in diskArray[i] and os.path.exists(f"/mnt/{diskArray[i]}")):
            removers.append(i)
        if appendMnt:
            diskArray[i] = f"/mnt/{diskArray[i]}"
        
        i+=1
        pass
    
    removers.reverse()
    for r in removers:
        del diskArray[r]
    diskArray.reverse()
    return diskArray

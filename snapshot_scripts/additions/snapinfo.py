from os import path, listdir
from datetime import datetime, timedelta
from additions.AllDisks import GetDiskArray
from xml.etree.ElementTree import Element, SubElement

class Snapshot:
    def __init__(self, _index, _share, _date, _name, _retention):
        self.Index = _index
        self.Share = _share
        if _name == "":
            self.Name = _date
        else:
            self.Name = _name
        self.Date = _date
        self.RetentionDuration = 0
        self.SetRetentionDuration(_retention)
        pass

    def SetRetentionDuration(self, _duration=""):
        haveDigit = ''.join(i for i in _duration if i.isdigit())
        if haveDigit == "":
            _duration = "0"

        if "m" in _duration:
            _duration = ''.join(i for i in _duration if i.isdigit() or i == '.')
            self.RetentionDuration = str(_duration)+"m"
        elif "y" in _duration:
            _duration = ''.join(i for i in _duration if i.isdigit() or i == '.')
            self.RetentionDuration = str(_duration)+"y"
        elif "w" in _duration:
            _duration = ''.join(i for i in _duration if i.isdigit() or i == '.')
            self.RetentionDuration = str(_duration)+"w"
        else:
            _duration = ''.join(i for i in _duration if i.isdigit() or i == '.')
            self.RetentionDuration = str(_duration)+"d"

            if _duration == "0d" or _duration == "0" or _duration == "":
                self.RetentionDuration = "inf"
        pass

    def AsElement(self):
        snapshot = Element('snapshot')
    
        snap_Index = SubElement(snapshot, 'index')
        snap_Share = SubElement(snapshot, 'share')
        snap_Name = SubElement(snapshot, 'name')
        snap_Time = SubElement(snapshot, 'snapshot_time')
        snap_Retention = SubElement(snapshot, 'retention_time')

        snap_Index.text = str(self.Index)
        snap_Share.text = self.Share
        snap_Name.text = self.Name
        snap_Time.text = self.Date
        snap_Retention.text = self.RetentionDuration

        return snapshot

    def CheckPastRetention(self):
        if self.RetentionDuration == "inf": return False
        
        format = "%Y-%m-%d_%H:%M:%S"
        timestamp = datetime.strptime(self.Date, format)
        ret = timedelta()
        timeSpan = ''.join(i for i in self.RetentionDuration if i.isdigit() or i == '.')
        timeType = ''.join(i for i in self.RetentionDuration if i.isalpha())

        if "y" in timeType.lower():
            ret = timedelta(days=(float(timeSpan)*365))
        elif "m" in timeType.lower():
            ret = timedelta(days=(float(timeSpan)*30))
        else:
            ret = timedelta(days=float(timeSpan))

        delDate = timestamp + ret
        if delDate <= datetime.now():
            return True
        else:
            return False
        pass

    def GetSnapshotPath(self, allDiskPaths=False):
        if allDiskPaths:
            diskArray = GetDiskArray()
            paths = []

            # print(diskArray)
            for disk in diskArray:
                possiblePath = f"/mnt/{disk}/.snapshots/{self.Share}/{self.Name}"

                if path.exists(possiblePath):
                    paths.append(possiblePath)

            return paths
        else:
            return f"/mnt/user/.snapshots/{self.Share}/{self.Name}"
        pass

    def GetMountableName(self):
        return f"{self.Share}_{self.Name.replace(':', '-')}"

    def GetMountNameFromConfig(self):
        return self.IsMounted(True)[1]
    
    """Returns True or False if it is mounted and returns the mount name"""
    def IsMounted(self, getMountName=False):
        allcfgs = list(filter(lambda cfg: cfg.endswith(".cfg"), listdir("/boot/config/shares")))
        cfgLocations = "/boot/config/shares/"
        
        for cfg in allcfgs:
            with open(cfgLocations+cfg, "r") as fil:
                line = fil.readline()
                while line:
                    if 'shareComment="Mount for:' in line:
                        mountFor = line.replace('shareComment="Mount for:', '').replace('"','').strip()
                        if mountFor == self.GetMountableName():
                            if getMountName:
                                return True, cfg.replace(".cfg","")
                            else:
                                return True
                            
                    elif 'shareComment=' in line: # not a snapshot
                        break
                    line = fil.readline()

        if getMountName:
            return False, None
        else:
            return False

        mountPath = f"/mnt/user/{self.Share}_{self.Name.replace(':', '-')}"
        return path.exists(mountPath)
        pass

    pass
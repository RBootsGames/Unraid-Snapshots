import xml.etree.ElementTree as ET
import operator
from os import path
from xml.dom import minidom
from datetime import datetime
from additions.snapinfo import Snapshot
from additions.AllDisks import GetDiskArray

class XmlControls:

    def __init__(self, autoLoad = True):
        # create the file structure
        self.xmlPath = "/boot/config/snapshot-data.xml"
        self.snapshotData = ET.Element('snapshot_list')
        self.snapIndex = 0
        self.snapshotList = [] # array of Snapshot() objects
        

        if autoLoad:
            self.LoadXml()
        pass


    # load data to list of Snapshot(s)
    def LoadXml(self): #, justDisk: bool = False
        if not path.exists(self.xmlPath):
            return
        ##### Read and load the xml file #####
        tree = ET.parse(self.xmlPath)
        root = tree.getroot()
        xmlSnapshotList = root.findall('snapshot')
        if len(xmlSnapshotList) == 0:
            return
            
        for elem in xmlSnapshotList:
            index = 0
            share = 0
            name = 0
            time = 0
            retention = 0
            
            for snap in elem:
                if snap.tag == "index":
                    index = snap.text
                    if int(index) >= self.snapIndex:
                        self.snapIndex = int(index)+1
                elif snap.tag == "share":
                    share = snap.text
                elif snap.tag == "name":
                    name = snap.text
                elif snap.tag == "snapshot_time":
                    time = snap.text
                elif snap.tag == "retention_time":
                    retention = snap.text
                    pass
                pass

            shot = Snapshot(index, share, time, name, retention)
            self.snapshotData.append(shot.AsElement())
            self.snapshotList.append(shot)
            pass
        pass

    def GetMountedSnapshots(self):
        return list(filter(lambda ss: ss.IsMounted(), self.snapshotList))
    
    # create a new XML file with the results
    def SaveXml(self):
        xmlstr = minidom.parseString(ET.tostring(self.snapshotData)).toprettyxml(indent="    ")
        with open(self.xmlPath, "w") as myfile:
            myfile.write(xmlstr)
            myfile.close()
        pass


    def CheckName(self, newName):
        list = [x for x in self.snapshotList if newName.lower() in x.Name.lower()]

        if len(list) == 0:
            return newName.replace(' ', '_')
        else:
            num = 0
            for s in list:
                value = int(f"0{s.Name}".replace(newName, ''))
                if value >= num:
                    num = value +1

            return f"{newName.replace(' ', '_')}{str(num).zfill(3)}"
        pass

    def GetSortedShare(self):
        sort = sorted(self.snapshotList, key=operator.attrgetter('Share'))
        master = []

        last = sort[0].Share
        tempList = []
        for snap in sort:
            if snap.Share == last:
                tempList.append(snap)
            else:
                master.append(tempList)
                tempList = []
                last = snap.Share
                tempList.append(snap)
            pass

        master.append(tempList)

        # print(master)
        return master
        # pass

    def AddSnapshot(self, share, timestamp, retention, name):
        # global snapIndex
        # global snapshotData
        # time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        if name == "":
            name = timestamp
        if retention == "":
            retention = "0d"
        
        snap = Snapshot(self.snapIndex, share, timestamp, name, retention)
        self.snapshotData.append(snap.AsElement())
        self.snapshotList.append(snap)
        self.snapIndex +=1
        # print(f"new snapshot for {share}")
        pass

    def RemoveSnapshot(self, remover):
        index = None
        
        if type(remover) == ET.Element:
            try:
                index = self.snapshotData.getchildren().index(remover)
                self.snapshotData.remove(remover)
            except:
                return False
        elif type(remover) == int:
            index = remover
            if index < 0 or index >= len(self.snapshotData):
                return False
            del self.snapshotData[index]

        while index < len(self.snapshotData):
            for snap in self.snapshotData[index]:
                if snap.tag == 'index':
                    snap.text = str(index)
                    break
            index += 1

        return True

    pass
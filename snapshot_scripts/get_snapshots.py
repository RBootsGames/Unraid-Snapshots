from additions.snapinfo import Snapshot
from additions.xml_controls import XmlControls
from additions.echo import Echo, EchoStyles, CombineEchoStyles

import os


xml = XmlControls()

if len(xml.snapshotData) == 0:
    Echo("No snapshots found.", EchoStyles.RED)
    exit(0)
    
shareSort = xml.GetSortedShare()

l_ID = 5
l_Name = 25
l_Date = 22
l_Ret = 5

for share in shareSort:
    l_Share = len(share[0].Share)
    
    print()
    Echo(f"{share[0].Share}", EchoStyles.BOLD)
    Echo(f"{'ID'.ljust(l_ID)}{'Name'.ljust(l_Name)}{'Snap Date'.ljust(l_Date)}{'Retention'.ljust(l_Ret)}", EchoStyles.UNDERLINE)
    for s in share:
        s: Snapshot
        Echo(f"{s.Index.ljust(l_ID)}{s.Name.ljust(l_Name)}{s.Date.ljust(l_Date)}{s.RetentionDuration.ljust(l_Ret)}")
    pass

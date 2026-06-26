"""
Scan the xml of the data_managers
To know what it consumes and where
it writes
"""

import xml.etree.ElementTree as ET
import os.path
from pathlib import Path

tools_iuc_path="/home/delislel/Documents/mygit/tools-iuc"
output_path="sync/dm_iuc.tsv"

fo = open(output_path, 'w')
fo.write("dm_dir\tdm_id\toutput_table\tinput_table\n")

# Get the datamanager list
# ls data_managers/*/data_manager/*xml
dm_list = {}
for xml_file in Path(tools_iuc_path).glob('data_managers/*/data_manager/*xml'):
    # xml_file = "/home/delislel/Documents/mygit/tools-iuc/data_managers/data_manager_bowtie2_index_builder/data_manager/bowtie2_index_builder.xml"
    dir = os.path.dirname(os.path.dirname(xml_file))
    dir_name = os.path.basename(dir)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    if root.tag != "tool":
        continue
    dm_id = root.attrib.get('id')
    # Get the from
    from_table = []
    for e in root:
        if e.tag == "inputs":
            for p in e:
                if p.tag == "param":
                    for o in p:
                        if o.tag == "options":
                            if 'from_data_table' in o.attrib:
                                from_table.append(o.get('from_data_table'))

    # Get the output tables
    out_tables = []
    dm_conf = os.path.join(os.path.dirname(os.path.dirname(xml_file)), "data_manager_conf.xml")
    tree = ET.parse(dm_conf)
    root = tree.getroot()
    dm = root[0]
    for output_dt in dm:
        out_tables.append(output_dt.get('name'))
    
    fo.write(f"{dir_name}\t{dm_id}\t{','.join(out_tables)}\t{','.join(from_table)}\n")

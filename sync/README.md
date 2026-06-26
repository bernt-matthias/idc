# Sync

The goal of this directory is to list all the indices used on the main instances and hopefully compare them.

## Scripts

There is one script that can be used to list all the indices available per table using as input all the tool_data_table_conf.xml (default are the 4 from CVMFS including the brc and vgp).

```bash
python sync/tool_data_table_conf_to_yaml.py -o sync/cvmfs_20260626.yml &> sync/cvmfs_20260626.log
```

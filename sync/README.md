# Sync

The goal of this directory is to list all the indices used on the main instances and hopefully compare them.

## Scripts

### Generate a big yaml per table from tool_data_table_conf

There is one script that can be used to list all the indices available per table using as input all the tool_data_table_conf.xml (default are the 4 from CVMFS including the brc and vgp).

```bash
python sync/tool_data_table_conf_to_yaml.py -o sync/cvmfs_20260626.yml &> sync/cvmfs_20260626.log
```

### Get data_manager - table connection

There is a script to get all the data_managers from iuc and the input/output tables.
The path to tools-iuc is hard coded, please change it if you want to use it.

```bash
python sync/tools_iuc_to_table_connection.py 
```

The output is [here](./dm_iuc.tsv).

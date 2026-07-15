# How to generate hashes for your database and compare it to other Galaxy instances?

## Prerequisites

- You need to have a ssh access to a linux machine which has read access to all indices.
- You need to have python/venv installed on this machine.
- You need to have some space to write the results.

## Step by step procedure

### Get all scripts

The easiest way is to clone the repository:

```bash
script_directory=$PWD
git clone -b datatable_sync https://github.com/lldelisle/idc.git
script_directory=$PWD/idc/sync/
```

Alternatively, you can download each script independently:

```bash
script_directory=$PWD
wget "https://raw.githubusercontent.com/lldelisle/idc/refs/heads/datatable_sync/sync/tool_data_table_conf_to_yaml.py"
wget "https://raw.githubusercontent.com/lldelisle/idc/refs/heads/datatable_sync/sync/all_fasta_files_to_refget_store.py"
wget "https://raw.githubusercontent.com/lldelisle/idc/refs/heads/datatable_sync/sync/requirements.txt"
wget "https://raw.githubusercontent.com/lldelisle/idc/refs/heads/all_tables_content_add_hashes.py"
```

### Get the list of all indices available to users

1. Identify your table config files (`tool_data_table_conf`). The easiest is to open the config file of your galaxy instance (`galaxy.yml`) and check in `galaxy.tool_data_table_config_path`.
2. Run the first python script to get the big yaml input of all other scripts:

```bash
tool_data_table="<first.xml> <second.xml> ..."
output_basename=<your instance name>_$(date -I)
# For CVMFS
# tool_data_table="/cvmfs/data.galaxyproject.org/byhand/location/tool_data_table_conf.xml /cvmfs/data.galaxyproject.org/managed/location/tool_data_table_conf.xml /cvmfs/brc.galaxyproject.org/config/tool_data_table_conf.xml /cvmfs/vgp.galaxyproject.org/config/tool_data_table_conf.xml"
# output_basename=CVMFS_$(date -I)
python ${script_directory}/tool_data_table_conf_to_yaml.py --tool_data_table_conf ${tool_data_table} -o "${output_basename}.yml"
```

### Get the digests of all indices

This step can be really long as the instance can have a lot of indices and each of them can be large so computing a digest of each of them is long.

```bash
python ${script_directory}/all_tables_content_add_hashes.py -i "${output_basename}.yml" -o "${output_basename}" -log info
```

### Generate Refgetstore instance from all FASTA tables (or just compute the hashes)

If you have enough space, we recommande to generate a Refgetstore instance as you will be able to efficiently retrieve sequences and genomes, metadata for identifying and comparing reference genomes, coordinate systems, genome browser compatibility and more.

If you prefer to first simply generate hashes use the option `--no-store`.

This step requires some dependencies.

```bash
option=""
# option="--no-store"
uv venv .venv
# Or python -m venv .venv
. .venv/bin/activate
uv pip install -r requirements.txt
# Or pip install -r requirements.txt
python ${script_directory}/all_fasta_files_to_refget_store.py ${option} "${output_basename}.yml" "${output_basename}"
```

### Share your results

All you need is to zip/tar the directory named `${output_basename}` and give it back to Lucille or Matthias.

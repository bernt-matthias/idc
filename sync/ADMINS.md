# How to generate hashes for your database and compare it to other Galaxy instances?

For the moment these are instructions mainly for EU admins.

## Prerequisites

- You need to run the procedure from a machine that has read access to all indices and has write access to a working directory.
- You need to have python/venv installed on this machine.
- You need to have some space to write the results (we estimate to 600GB for the CVMFS refgetstore).

## Step by step procedure

### Get all scripts

The easiest way is to clone the repository:

```bash
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

The estimated output of this step is up to 30MB for CVMFS and less than 1MB for EU (this is the same script as I ran with José during the Cofest, just one more key per entry = the path of the loc file).

1. Identify your table config files (`tool_data_table_conf`). The easiest is to open the config file of your galaxy instance (`galaxy.yml`) and check in `galaxy.tool_data_table_config_path`.
2. Run the first python script to get the big yaml input of all other scripts:

```bash
tool_data_table="<first.xml> <second.xml> ..."
output_basename=<your instance name>_$(date -I)
# For EU
tool_data_table=/opt/galaxy/config/tool_data_table_conf.xml
output_basename=usegalaxy_eu_$(date -I)
python ${script_directory}/tool_data_table_conf_to_yaml.py --tool_data_table_conf ${tool_data_table} -o "${output_basename}.yml"

# For CVMFS
tool_data_table_cvmfs="/cvmfs/data.galaxyproject.org/byhand/location/tool_data_table_conf.xml /cvmfs/data.galaxyproject.org/managed/location/tool_data_table_conf.xml /cvmfs/brc.galaxyproject.org/config/tool_data_table_conf.xml /cvmfs/vgp.galaxyproject.org/config/tool_data_table_conf.xml"
output_basename_cvmfs=CVMFS_$(date -I)
python ${script_directory}/tool_data_table_conf_to_yaml.py --tool_data_table_conf ${tool_data_table_cvmfs} -o "${output_basename_cvmfs}.yml"
```

### Get the digests of all indices

The estimated output of this step should not be more than 10GB.

This step can be really long as the instance can have a lot of indices and each of them can be large so computing a digest of each of them is long.

By default this script uses 8 threads to compute checksums for the files referred by one data table entry. The number of threads can be set with `--threads` (default is 8). The actual CPU usage will be much smaller (at least on network storage, i.e. you can use it to hide IO time).

```bash
mkdir ${output_basename}
python ${script_directory}/all_tables_content_add_hashes.py -i "${output_basename}.yml" -o "${output_basename}" -log info

# For CVMFS
mkdir ${output_basename_cvmfs}
python ${script_directory}/all_tables_content_add_hashes.py -i "${output_basename_cvmfs}.yml" -o "${output_basename_cvmfs}" -log info

```

### Generate Refgetstore instance from all FASTA tables (or just compute the hashes)

If you have enough space, we recommend to generate a Refgetstore instance as you will be able to efficiently retrieve sequences and genomes, metadata for identifying and comparing reference genomes, coordinate systems, genome browser compatibility and more. We think that the estimated size of a Refgetstore is about 25/35% of the size of the fasta files. For CVMFS, we estimate to 400-600GB.

If you prefer to first simply generate hashes use the option `--no-store`.

This step requires some dependencies.

```bash
uv venv .venv
# Or python -m venv .venv
. .venv/bin/activate
uv pip install -r requirements.txt
# Or pip install -r requirements.txt
python ${script_directory}/all_fasta_files_to_refget_store.py --no-store "${output_basename}.yml" "${output_basename}"

# For CVMFS
python ${script_directory}/all_fasta_files_to_refget_store.py "${output_basename_cvmfs}.yml" "${output_basename_cvmfs}"
```

### Share your results

We will provide you a s3 bucket to put the 2 directories.

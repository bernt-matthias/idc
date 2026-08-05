# Sync

The goal of this directory is to list all the indices used on the main instances and hopefully compare them.

## Requirements

Python requirements are listed in the `requirements.txt` file. It is recommended to use `uv` to install the dependencies in a virtual environment, e.g.:

1. [Install uv](https://github.com/snarky/uv#installation)
2. Run the following commands:

```bash
cd sync
uv venv .venv
. .venv/bin/activate
uv pip install -r requirements.txt
```

## Scripts

### Generate a big yaml per table from tool_data_table_conf

There is one script that can be used to list all the indices available per data table using as input all the tool_data_table_conf.xml files (default are the 4 from CVMFS including the brc and vgp).

```bash
python sync/tool_data_table_conf_to_yaml.py -o sync/cvmfs_20260715.yml &> sync/cvmfs_20260715.log
```

One can use `--tool_data_table_conf` to specifiy the tool_data_table_conf.xml files to be considered. 

José ran the command for the usegalaxy.eu and the result is [here](./usegalaxy_eu_20260626.yaml).

### Generate hashes and manifest of all indices listed in the tables

Take all_tables_content yaml file and add hash and manifest (contents + hashes). Output yaml per data table.

```bash
python sync/all_tables_content_add_hashes.py -i sync/test.yml -o sync/test_hashes
```

### Get data_manager - table connection

There is a script to get all the `data_manager`s from iuc and the input/output data tables.
The path to tools-iuc is hard coded, please change it if you want to use it.

```bash
python sync/tools_iuc_to_table_connection.py 
```

The output is [here](./dm_iuc.tsv).

### Generate datatable entry hashes and manifests

`python sync/all_tables_content_add_hashes.py -i YAML_FILE -o OUT_DIRECTORY/ [--threads THREADS]` takes the yaml file that has been created with `tool_data_table_conf_to_yaml` and adds to each entry: 

- manifest, i.e. the (sorted) list of all files in the data table entry with size, file hash, info if its a symlink
- and a hash digest of the manifest

The output is one yaml file per data table. The given number of threads will be used to process the files in the manifest in parallel (the global manifest is computed in a single thread). This may help to hide slow IO.

The manifest contains the following: if the data table entry

- refers to a directory: then the manifest contains all files contained (recursively) in the directory
- refers to a file: then the manifest contains all file paths containing the filename as prefix
- is a file prefix: then the manifest contains all file paths that have this prefix
- is a comma separated list: the manifest is computed as the concatenation of the manifests of the list elements


### Generate Refgetstore instance from all FASTA tables - including "GA4GH refget: sequence collections"-compatible digests and chromLen info ++
Background info: https://refget.databio.org/

Used to generate a refgetstore (See: https://refgenie.org/refget/refgetstore-explained/) from all available fasta files.

```bash
python sync/all_fasta_files_to_refget_store.py sync/cvmfs_20260626.yml /path/to/refget_output_20260626/
```

Note: the option '--no-store' can be used to skip generating the Refgetstore and only generate the summary files (currently only JSON).

For each reference genome, the following output is generated:

#### JSON file 
Summary files with "GA4GH refget: sequence collections"-compatible digests, as well as overview of sequences, lengths, and names. E.g.:

_/path/to/refget_output_20260626/json/Araly.json:_
```json
{
  "level_0": "l89Tr5HaZx15ici2hCjfxuzyPd_pVO2M",
  "level_1": {
    "names": "3V0VCjf1TJhSwmy5mSL74Cy86pB6H-IY",
    "lengths": "xsKk_SHSYpPTP7N5A6bG202Wn0Tvh0hn",
    "sequences": "MNdUu4DfiQbTPy5DU7vCJoVSxQD5Qc92",
    "name_length_pairs": "eM-TewfJx_bpnWagwnnPt4HokRi9E-tn",
    "sorted_name_length_pairs": "AYTR0ln2-yvYlf0olj21uiYYUcYd2JtE",
    "sorted_sequences": "09FMt4b0-sJhgHcdtgJAoAn-YHuXEPEs"
  },
  "level_2": {
    "names": [
      "scaffold_1",
      "scaffold_2",
      (...)
    ],
    "lengths": [
      33132539,
      19320864,
      (...)
    ],
    "sequences": [
      "SQ.nVPkmXGwi5WlIoN0HP1HtwTP0gppbptW",
      "SQ.8a8KcjrqyGNPOC5UmLP0hiqn6xVOpRiq",
      (...)
    ]
  },
  "aliases": {
    "galaxy_unique_build_id": "Araly1",
    "galaxy_dbkey": "Araly1",
    "galaxy_name": "Arabidopsis lyrata: Araly1",
    "galaxy_loc_file": "!cvmfs!data.galaxyproject.org!byhand!location!all_fasta.loc",
    "galaxy_tool_data_table_conf": "!cvmfs!data.galaxyproject.org!byhand!location!tool_data_table_conf.xml"
  }
}
```

#### YAML file
A summary YAML file is generated with digests and aliases for all the reference genomes that have been processed:

_/path/to/refget_output_20260626/yaml/all_fasta.yml:_
```yaml
Araly1:
  level_0: l89Tr5HaZx15ici2hCjfxuzyPd_pVO2M
  level_1:
    names: 3V0VCjf1TJhSwmy5mSL74Cy86pB6H-IY
    lengths: xsKk_SHSYpPTP7N5A6bG202Wn0Tvh0hn
    sequences: MNdUu4DfiQbTPy5DU7vCJoVSxQD5Qc92
    name_length_pairs: eM-TewfJx_bpnWagwnnPt4HokRi9E-tn
    sorted_name_length_pairs: AYTR0ln2-yvYlf0olj21uiYYUcYd2JtE
    sorted_sequences: 09FMt4b0-sJhgHcdtgJAoAn-YHuXEPEs
  level_2_peek:
    sequence_count: 702
    first_name: scaffold_1
    first_length: 33132539
    first_sequence: SQ.nVPkmXGwi5WlIoN0HP1HtwTP0gppbptW
  aliases:
    galaxy_unique_build_id: Araly1
    galaxy_dbkey: Araly1
    galaxy_name: 'Arabidopsis lyrata: Araly1'
    galaxy_loc_file: '!cvmfs!data.galaxyproject.org!byhand!location!all_fasta.loc'
    galaxy_tool_data_table_conf: '!cvmfs!data.galaxyproject.org!byhand!location!tool_data_table_conf.xml'```
```

#### RGSI file
Similar content as the JSON file, but in tabular format:

_/path/to/refget_output_20260626/rgsi/Araly.rgsi:_

```tsv
##seqcol_digest=l89Tr5HaZx15ici2hCjfxuzyPd_pVO2M
##names_digest=3V0VCjf1TJhSwmy5mSL74Cy86pB6H-IY
##sequences_digest=MNdUu4DfiQbTPy5DU7vCJoVSxQD5Qc92
##lengths_digest=xsKk_SHSYpPTP7N5A6bG202Wn0Tvh0hn
##name_length_pairs_digest=eM-TewfJx_bpnWagwnnPt4HokRi9E-tn
##sorted_name_length_pairs_digest=AYTR0ln2-yvYlf0olj21uiYYUcYd2JtE
##sorted_sequences_digest=09FMt4b0-sJhgHcdtgJAoAn-YHuXEPEs
#name	length	alphabet	sha512t24u	md5	description
scaffold_1	33132539	dna3bit	nVPkmXGwi5WlIoN0HP1HtwTP0gppbptW	b50eceb9392744674ff950669156ed8c	
scaffold_2	19320864	dna3bit	8a8KcjrqyGNPOC5UmLP0hiqn6xVOpRiq	bf9836478cee70e09fc4b28702e6fae0	
(...)
```

#### Refgetstore

_`/path/to/refget_output_20260626/store/`_

A flat-file Refgetstore instance containing all the sequences and genome information using an optimized storage structure, as [defined here](https://refgenie.org/refget/reference/refgetstore-format/).

This works as a basis for efficient retrieval of sequences and genomes, metadata for identifying and comparing reference genomes, coordinate systems, genome browser compatibility and more. Based on this file structure, a web page + API for exploring supported genome browsers can easily be launched. See examples here: https://refget.databio.org/explore

Front-end implementation that can easily be installed on top of the Refgetstore output from this script is available here: https://github.com/refgenie/refget/tree/master/frontend

The Refgetstore can be used as basis for comparing reference genomes across different Galaxy instances, as well as to align with source repositories (once their contents are indexed in a GA4GH Refget: sequence collections implementation near you!)

### Refget: Sequence collections API on top of Refgetstore

An extended version of the API which is defined as part of the [GA4GH Refget: Sequence Collections standard](https://ga4gh.github.io/refget/seqcols/#3-api-a-server-api-specification-for-retrieving-and-comparing-sequence-collections) can be installed on top of the Refgetstore by running e.g. the following:

```
sync/run_seqcolapi_from_refget_store.sh /path/to/refget_output_20260626/store/ 8100
```

This will first clone the refget repository available at "https://github.com/refgenie/refget.git under `sync/refget_clone` unless it already exists, before starting the API server

### Generate a sample yaml with cvmfs paths to have a good idea of what is inside and do tests

The paths are hard-written relative to the idc root.

```bash
python sync/generate_test_all_tables_content_yaml.py
```

The output is [here](./test.yml).

I could then run the refget_store with the option `--no-store` on the test:

```bash
python sync/all_fasta_files_to_refget_store.py sync/test.yml sync/test_dig/ &> sync/test_dig.log
```

The output is [here](./test_dig/).


### Generate a yml with the content of the tables but fasta centric

The final yml file is:

The first level is dbkey (from the `__dbkeys__` table it takes the `len_path`), the second level is the 'value' field of the 'all_fasta' table in the associated dbkey value.

In this first version, I assumed that the 'value' of the tables depending on the all_fasta table would match between them but it seems not the case.

For example, in the EU db, 'hg18' has no dbkey entry (but is probably listed in the builds.txt), the value ine the all_fasta is 'hg18full' but in the bowtie2_indexes table the dbkey is hg18 and the value is hg18...

Another example, for hg38, there is hg38full and hg38canon but for the picard_indexes or rnastar_index it is hg38 and we do not know which one.

Sometimes there are some typos, for example in CVMFS in the bowtie2 index is 'galgal4' and 'galGal4' with names 'Chicken (Nov 2011, Gallus gallus)' and 'Chicken (Gallus gallus): galGal4' respectively.

It would be more safe to rely on the output of the postgres query if possible. 

Despite this, I ran this first version on the 2 yml I have and inspected the log files.

```bash
python sync/all_tables_content_to_fasta_based_yaml.py -i sync/cvmfs_20260715.yml -o sync/cvmfs_20260715_perdbkey.yml -log info 2> sync/cvmfs_20260715_perdbkey.log
python sync/all_tables_content_to_fasta_based_yaml.py -i sync/usegalaxy_eu_20260626.yaml -o sync/usegalaxy_eu_20260626_perdbkey.yml -log info 2> sync/usegalaxy_eu_20260626_perdbkey.log
```

## CVMFS inspection

### Fasta files

@sveinugu found some path to fasta that do not exists:

```txt
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/ce6/seq/c6.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/panTro1/seq/panTro1canon.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/droYak1/seq/droYak1.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/fr1/seq/fr1.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/eriEur1/seq/eriEur1.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/lMaj5/seq/lMaj5.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/ornAna1/seq/ornAna1.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/ornAna1/seq/ornAna1.fa does not exist, skipping import...
ERROR: Fasta file /Users/Shared/cvmfs/data.galaxyproject.org/byhand/rn3/seq/rn3canon.fa does not exist, skipping import...
```

In addition, the refget store raised an error for:

```bash
Processing /data/dnb01/cvmfs_hashes/usegalaxy_eu_CVMFS_20260715/rgsi/taeGut2.fa...
Traceback (most recent call last):
  File "/data/dnb01/cvmfs_hashes/idc/sync/all_fasta_files_to_refget_store.py", line 249, in <module>
    main(
  File "/data/dnb01/cvmfs_hashes/idc/sync/all_fasta_files_to_refget_store.py", line 47, in main
    import_fasta_all(
  File "/data/dnb01/cvmfs_hashes/idc/sync/all_fasta_files_to_refget_store.py", line 123, in import_fasta_all
    collection, new = store.add_sequence_collection_from_fasta(local_fasta_path)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
OSError: Error importing FASTA: Invalid UTF-8 in FASTA header
```

#### ce6

`/cvmfs/data.galaxyproject.org/byhand/ce6/seq/c6.fa`

This is a typo and should be `/cvmfs/data.galaxyproject.org/byhand/ce6/seq/ce6.fa`

#### panTro1

`/cvmfs/data.galaxyproject.org/byhand/panTro1/seq/panTro1canon.fa`

This should be `/cvmfs/data.galaxyproject.org/byhand/panTro1/seq/panTro1.fa`

#### droYak1

`/cvmfs/data.galaxyproject.org/byhand/droYak1/seq/droYak1.fa` could maybe reconstituted from what is in `/cvmfs/data.galaxyproject.org/byhand/droYak1/tmp` or with [nibFrag](https://genome.ucsc.edu/goldenpath/help/blatSpec.html#nibFragUsage).

#### fr1

There is a `chrUn.nib` in the `/cvmfs/data.galaxyproject.org/byhand/fr1/seq/` we could probably use [nibFrag](https://genome.ucsc.edu/goldenpath/help/blatSpec.html#nibFragUsage) to retrieve the fasta.

#### eriEur1

There is a `/cvmfs/data.galaxyproject.org/byhand/eriEur1/eriEur1.2bit` to be converted back to fasta...

#### lMaj5

There is a lot of nib files to be converted in `/cvmfs/data.galaxyproject.org/byhand/lMaj5/seq/`.

#### ornAna1

There are a lot of places where this supposely existing fasta is symlinked:

```bash
$ ls -alh /cvmfs/data.galaxyproject.org/byhand/ornAna1/*/*fa
lrwxrwxrwx 1 cvmfs cvmfs   17 May 17  2014 /cvmfs/data.galaxyproject.org/byhand/ornAna1/bowtie_index/ornAna1.fa -> ../seq/ornAna1.fa
lrwxrwxrwx 1 cvmfs cvmfs   17 May 17  2014 /cvmfs/data.galaxyproject.org/byhand/ornAna1/bwa_index/ornAna1.fa -> ../seq/ornAna1.fa
lrwxrwxrwx 1 cvmfs cvmfs   17 May 17  2014 /cvmfs/data.galaxyproject.org/byhand/ornAna1/picard_index/ornAna1.fa -> ../seq/ornAna1.fa
-rw-r--r-- 1 cvmfs cvmfs 5.7G Jun  9  2009 /cvmfs/data.galaxyproject.org/byhand/ornAna1/quality_scores/ornAna1.quals.fa
lrwxrwxrwx 1 cvmfs cvmfs   17 May 17  2014 /cvmfs/data.galaxyproject.org/byhand/ornAna1/sam_index/ornAna1.fa -> ../seq/ornAna1.fa
```

According to the fa.fai the width of lines was 50bp.

We can get the fasta back from the bowtie index with `bowtie-inspect -a 50 /cvmfs/data.galaxyproject.org/byhand/ornAna1/bowtie_index/ornAna1`.

```bash
$ apptainer exec -B /cvmfs/ /cvmfs/singularity.galaxyproject.org/all/bowtie\:1.3.1--py312hf8dbd9f_10 bowtie-inspect -a 50 /cvmfs/data.galaxyproject.org/byhand/ornAna1/bowtie_index/ornAna1 | head
>chr1
GTGGCCTAGTGTAAAGAGCACAGCCCTGGGAGTCAGAGGTCGTGGGTCCG
AATTCCAGCTCTGCCACTTGACTGCTGCGTGACCTTGGACAAGTCACTTC
CCTTCTCCGAGCCTCATCTGGAAAGTGGGGATTGAGATCGTGATCCCAAC
GTGGGGCGGGGACTGTGCCCACCCCGATTTGCTGGTATCCACCCCGGCGC
TTAGGACAGTGCCCGGCACGTAGGAAGCGCTTAACAAATACCATCATTAT
TATTACTGTATTTTTGAGTAGGACAGGAGAAGGCCTTGGCACCCACCTTT
AGAAAGGAGGGGAAAAAAACCCGATTAAGTCACAGTCCAGAGTGTAACTC
AGACACCCGGGAAAGATTCTAGAGTAAATGGTTGGGAGTGTGTGCATCAT
CTCTGTAAAGTCTGGGTTGTAAAAAATAATTCTTTGAAAAGAGATCCTCT
```

Or get it back from [UCSC](https://hgdownload.soe.ucsc.edu/goldenPath/ornAna1/bigZips/ornAna1.fa.gz) but we need to check it matches the fai.

#### rn3

`/cvmfs/data.galaxyproject.org/byhand/rn3/seq/rn3canon.fa` should be replaced by `/cvmfs/data.galaxyproject.org/byhand/rn3/seq/rn3.fa`

#### taeGut2

@bernt-matthias identified the issue:

```bash
file /cvmfs/data.galaxyproject.org/managed/seq/taeGut2.fa 
/cvmfs/data.galaxyproject.org/managed/seq/taeGut2.fa: gzip compressed data, last modified: Wed Apr 16 16:40:59 2014, from Unix, original size modulo 2^32 1257492349
```

It seems that the file is directly the fa.gz from UCSC:
```bash
$ md5sum /cvmfs/data.galaxyproject.org/managed/seq/taeGut2.fa
4dfa1fa3a4eb7cf192ee483e4a28217d  /cvmfs/data.galaxyproject.org/managed/seq/taeGut2.fa
$ curl -s https://hgdownload.soe.ucsc.edu/goldenPath/taeGut2/bigZips/md5sum.txt| grep taeGut2.fa.gz
4dfa1fa3a4eb7cf192ee483e4a28217d  taeGut2.fa.gz
```

## Ideas/TODO

Keep in mind that the data_manager are run while we are working.

### Archeology

Before we move anything.

We need to write a postgres query to get the job details of all the data_manager to be submitted to both the eu and the org instance that is used for data management.

I (Lucille) think that the command is (if the database is called galaxy and if the schema is still working with 26.1...):
```bash
psql -d galaxy -c "COPY (SELECT  create_time, data_manager_id, job_parameter.job_id, name, value FROM job_parameter JOIN  data_manager_job_association ON job_parameter.job_id = data_manager_job_association.job_id) TO STDOUT WITH HEADER" > all_params_for_DM.tsv
```

EU ran this and the result is [here](./20260706_EU_all_params_for_DM.tsv). Unfortunately it seems that there were some manual modifications.

### all_fasta table

There are specificities for this table.

1. The idea is to calculate the Refget Seqcol digest on each fasta file on both instances
    a. Write a bash script that generate a single file per instance with all the digests of the all_fasta.
2. Identify the common digests (probably level 0)
    a. create a new loc file for EU with common that would link to cvmfs when available.
    b. remove from the original loc EU file the corresponding.
    c. if there are common values data should stay on EU.
3. Identify the totally different (= no seq common)
    a. list them into a new loc file that would go to CVMFS with the data moved
4. Build a list of things in the middle and open discussion

5. Refget store, this contains the fa so no store it twice.

### fasta related tables

0. For each fasta related table determine the way to find the files related (single file vs directory vs glob).

1. Get checksums (separately for the fasta and other files) and identify the matching/not matching.
2. Only potentially move the one that come from 'specific' fasta

### Other indices

0. For each table determine the way to find the files related (single file vs directory vs glob).
1. Get checksums and identify the matching/not matching.


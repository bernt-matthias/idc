# Sync

The goal of this directory is to list all the indices used on the main instances and hopefully compare them.

## Requirements

Python requirements are listed in the `requirements.txt` file.

## Scripts

### Generate a big yaml per table from tool_data_table_conf

There is one script that can be used to list all the indices available per table using as input all the tool_data_table_conf.xml (default are the 4 from CVMFS including the brc and vgp).

```bash
python sync/tool_data_table_conf_to_yaml.py -o sync/cvmfs_20260626.yml &> sync/cvmfs_20260626.log
```

José ran the command for the usegalaxy.eu and the result is [here](./usegalaxy_eu_20260626.yaml).

### Get data_manager - table connection

There is a script to get all the data_managers from iuc and the input/output tables.
The path to tools-iuc is hard coded, please change it if you want to use it.

```bash
python sync/tools_iuc_to_table_connection.py 
```

The output is [here](./dm_iuc.tsv).


### Generate Refgetstore instance from all FASTA tables - including "GA4GH refget: sequence collections"-compatible digests and chromLen info ++
Background info: https://refget.databio.org/

Used to generate a refgetstore (See: https://refgenie.org/refget/refgetstore-explained/) from all available fasta files.

```bash
python sync/tool_data_table_conf_to_yaml.py sync/cvmfs_20260626.yml output_20260626/ &> sync/refgetstore_20260626.log
```

For each reference genome, the following output is generated:

#### JSON file 
Summary files with "GA4GH refget: sequence collections"-compatible digests, as well as overview of sequences, lengths, and names. E.g.:

```
output_20260626/refget/json/Araly.json:

{
  "level_0": "l89Tr5HaZx15ici2hCjfxuzyPd_pVO2M",
  "level_1": {
    "lengths": "xsKk_SHSYpPTP7N5A6bG202Wn0Tvh0hn",
    "names": "3V0VCjf1TJhSwmy5mSL74Cy86pB6H-IY",
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
  "aliases": [
    [
      "galaxy_unique_build_id",
      "Araly1"
    ],
    [
      "galaxy_dbkey",
      "Araly1"
    ],
    [
      "galaxy_tool_data_table_conf",
      "/cvmfs/data.galaxyproject.org/byhand/location/tool_data_table_conf.xml"
    ],
    [
      "galaxy_name",
      "Arabidopsis lyrata: Araly1"
    ]
  ]
}
```

#### RGSI file
Similar content as the JSON file, but in tabular format:

```
output_20260626/refget/rgsi/Araly.rgsi:

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

`output_20260626/refget/store/`

A flat-file Refgetstore instance containing all the sequences and genome information using an optimized storage structure, as [defined here](https://refgenie.org/refget/reference/refgetstore-format/).

This works as a basis for efficient retrieval of sequences and genomes, metadata for identifying and comparing reference genomes, coordinate systems, genome browser compatibility and more. Based on this file structure, a web page + API for exploring supported genome browsers can easily be launched. See examples here: https://refget.databio.org/explore

Front-end implementation that can easily be installed on top of the Refgetstore output from this script is available here: https://github.com/refgenie/refget/tree/master/frontend

The Refgetstore can be used as basis for comparing reference genomes across different Galaxy instances, as well as to align with source repositories (once their contents are indexed in a GA4GH Refget: sequence collections implementation near you!)

## Ideas/TODO

Keep in mind that the data_manager are run while we are working so there are always no.

### Archeology

Before we move anything.

We need to write a postgres query to get the job details of all the data_manager to be submitted to both the eu and the org instance that is used for data management.

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


# Sync

The goal of this directory is to list all the indices used on the main instances and hopefully compare them.

## Requirements

Python requirements are listed in the `requirements.txt` file.

## Scripts

### Generate a big yaml per table from tool_data_table_conf

There is one script that can be used to list all the indices available per data table using as input all the tool_data_table_conf.xml files (default are the 4 from CVMFS including the brc and vgp).

```bash
python sync/tool_data_table_conf_to_yaml.py -o sync/cvmfs_20260626.yml &> sync/cvmfs_20260626.log
```

One can use `--tool_data_table_conf` to specifiy the tool_data_table_conf.xml files to be considered. 

José ran the command for the usegalaxy.eu and the result is [here](./usegalaxy_eu_20260626.yaml).

### Get data_manager - table connection

There is a script to get all the `data_manager`s from iuc and the input/output data tables.
The path to tools-iuc is hard coded, please change it if you want to use it.

```bash
python sync/tools_iuc_to_table_connection.py 
```

The output is [here](./dm_iuc.tsv).


### Generate Refgetstore instance from all FASTA tables - including "GA4GH refget: sequence collections"-compatible digests and chromLen info ++
Background info: https://refget.databio.org/

Used to generate a refgetstore (See: https://refgenie.org/refget/refgetstore-explained/) from all available fasta files.

```bash
python sync/tool_data_table_conf_to_yaml.py sync/cvmfs_20260626.yml /path/to/refget_output_20260626/ &> sync/refgetstore_20260626.log
```

For each reference genome, the following output is generated:

#### JSON file 
Summary files with "GA4GH refget: sequence collections"-compatible digests, as well as overview of sequences, lengths, and names. E.g.:

```
/path/to/refget_output_20260626/json/Araly.json:

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
/path/to/refget_output_20260626/rgsi/Araly.rgsi:

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

`/path/to/refget_output_20260626/store/`

A flat-file Refgetstore instance containing all the sequences and genome information using an optimized storage structure, as [defined here](https://refgenie.org/refget/reference/refgetstore-format/).

This works as a basis for efficient retrieval of sequences and genomes, metadata for identifying and comparing reference genomes, coordinate systems, genome browser compatibility and more. Based on this file structure, a web page + API for exploring supported genome browsers can easily be launched. See examples here: https://refget.databio.org/explore

Front-end implementation that can easily be installed on top of the Refgetstore output from this script is available here: https://github.com/refgenie/refget/tree/master/frontend

The Refgetstore can be used as basis for comparing reference genomes across different Galaxy instances, as well as to align with source repositories (once their contents are indexed in a GA4GH Refget: sequence collections implementation near you!)

### Generate refget seqcol digest for all FASTA

Highly inspired by the script above, the script `all_fasta_files_to_refget_seqcol_digest.py` takes as input the yaml output of `tool_data_table_conf_to_yaml.py` and generate a yaml file with contains all the digests (level 0, 1, 2) for each entry of the 'all_fasta' table.

This script requires the dependencies listed in `requirements.txt`.

```bash
python all_fasta_files_to_refget_seqcol_digest.py cvmfs_20260701.yml cvmfs_20260701_dig.yml
```

The output yaml is like:
```yaml
Amel_4.5:
  level_0: WVM-8x592B68KwfpbOcMBcAqeNz2ZZy0
  level_1:
    lengths: UzkbME4hSLXP0-L9KG6gXpQABvSeesda
    name_length_pairs: FJrASCKexRm7izae_hgpkkxf2yQ3fZ91
    names: aEK2wLGTcQ-QUcJo4LsteN7HJbE4BFVE
    sequences: bqcttuF_838R5VjLDpXleJQAx2NxFb7p
    sorted_name_length_pairs: y2EF8IlKTrlTsJg6YElzkVNWTLU7MyUa
    sorted_sequences: ItxZpRoS1VB8l9oPe9pdlkxsX2R-ekqg
  level_2:
    lengths:
    - 29893408
    - 15549267
    (...)
    names:
    - NC_007070.3
    - NC_007071.3
      (...)
    sequences:
    - SQ.9q0qXprsO7haivVB3EaU3-44101Q-kyx
    - SQ.eTdIWaBZiw-V4oomq8niOL7IRM245Ste
      (...)
  original_info:
    dbkey: Amel_4.5
    loc_file: /cvmfs/data.galaxyproject.org/managed/location/all_fasta_dbkeys.loc
    name: A. mellifera Nov. 2010 (GCF_000002195.4/Amel_4.5) (Amel_4.5)
    path: /cvmfs/data.galaxyproject.org/managed/seq/Amel_4.5.fa
    value: Amel_4.5
    xml_file: /cvmfs/data.galaxyproject.org/managed/location/tool_data_table_conf.xml
apiMel4:
  level_0: Z45sUmBk1p-HGz1MamiTs5LmH4oNPp4f
  level_1:
    lengths: cOFi1097Jk0uQG_WBsKDmq3-1BLqrydF
    name_length_pairs: xFLsw2hjVc2RjK5XJOeQPqUkbfAaa6vZ
    names: dc9JjlcTZm0EiOMZCPg8Pb8g_w1TQMnx
    sequences: A7uSqpdLpcZki6LC1QenI3g7qu6NK02R
    sorted_name_length_pairs: OVNLncQr0dTKG5a13uyASOoGiEd5Mn6z
    sorted_sequences: ItxZpRoS1VB8l9oPe9pdlkxsX2R-ekqg
  level_2:
    lengths:
    - 29893408
    - 12965953
      (...)
    names:
    - Group1
    - Group10
      (...)
    sequences:
    - SQ.9q0qXprsO7haivVB3EaU3-44101Q-kyx
    - SQ.oES2Cq62esSQPuI3CTXKyuQ1ENEeADTp
      (...)
  original_info:
    dbkey: apiMel4
    loc_file: /cvmfs/data.galaxyproject.org/managed/location/all_fasta_dbkeys.loc
    name: A. mellifera 04 Nov 2010 (Amel_4.5/apiMel4) (apiMel4)
    path: /cvmfs/data.galaxyproject.org/managed/seq/apiMel4.fa
    value: apiMel4
    xml_file: /cvmfs/data.galaxyproject.org/managed/location/tool_data_table_conf.xml
```

### Generate a sample yaml with cvmfs paths to have a good idea of what is inside and do tests

The paths are hard-written relative to the idc root.

```bash
python sync/generate_test_all_tables_content_yaml.py
```

The output is [here](./test.yml).

I could then run the refet_seqcol_digest on the test:

```bash
$ python sync/all_fasta_files_to_refget_seqcol_digest.py sync/test.yml sync/test_dig.yml 
Loading the big yaml file.
Done
Processing /cvmfs/data.galaxyproject.org/managed/seq/apiMel4.fa...
Added Z45sUmBk1p-HGz1MamiTs5LmH4oNPp4f (5321 seqs) from /cvmfs/data.galaxyproject.org/managed/seq/apiMel4.fa in 0.0s
Imported 1 file(s) in 1.1s (jobs=1)
Processing /cvmfs/data.galaxyproject.org/managed/seq/Amel_4.5.fa...
Added WVM-8x592B68KwfpbOcMBcAqeNz2ZZy0 (5321 seqs) from /cvmfs/data.galaxyproject.org/managed/seq/Amel_4.5.fa in 0.0s
Imported 1 file(s) in 1.1s (jobs=1)
```

The output is [here](./test_dig.yml).


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

I tried to get the fasta back from the bowtie index with `bowtie-inspect /cvmfs/data.galaxyproject.org/byhand/ornAna1/bwa_index/ornAna1.fa` but I got `Could not locate a Bowtie index corresponding to basename "/cvmfs/data.galaxyproject.org/byhand/ornAna1/bwa_index/ornAna1.fa"`. We can probably download it again from [UCSC](https://hgdownload.soe.ucsc.edu/goldenPath/ornAna1/bigZips/ornAna1.fa.gz).

#### rn3

`/cvmfs/data.galaxyproject.org/byhand/rn3/seq/rn3canon.fa` should be replaced by `/cvmfs/data.galaxyproject.org/byhand/rn3/seq/rn3.fa`


## Ideas/TODO

Keep in mind that the data_manager are run while we are working.

### Archeology

Before we move anything.

We need to write a postgres query to get the job details of all the data_manager to be submitted to both the eu and the org instance that is used for data management.

I (Lucille) think that the command is (if the database is called galaxy and if the schema is still working with 26.1...):
```bash
psql -d galaxy -c "COPY (SELECT  create_time, data_manager_id, job_parameter.job_id, name, value FROM job_parameter JOIN  data_manager_job_association ON job_parameter.job_id = data_manager_job_association.job_id) TO STDOUT WITH HEADER" > all_params_for_DM.tsv
```

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


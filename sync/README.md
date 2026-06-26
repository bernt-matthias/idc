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
  }
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




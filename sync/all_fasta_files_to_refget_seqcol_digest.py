# import json
import os
# import shutil
import sys
import yaml
from pathlib import Path
from typing import NamedTuple

from gtars.refget import RefgetStore

class FastaAllRecord(NamedTuple):
    dbkey: str
    name: str
    path: str
    value: str
    loc_file: str
    xml_file: str


def _read_fasta_all(cvmfs_yaml_path: Path) -> list[FastaAllRecord]:
    with open(cvmfs_yaml_path, 'r') as cvmfs_yaml_file:
        cvmfs_yaml = yaml.safe_load(cvmfs_yaml_file)

    out = []
    for el in cvmfs_yaml['all_fasta']:
        out.append(FastaAllRecord(**el))
    return out


def main(cvmfs_yaml_path: Path, output_path: Path, cvmfs_mount_prefix: Path):
    fasta_all = _read_fasta_all(cvmfs_yaml_path)
    unique_vals = set()
    for fasta_record in fasta_all:
        if fasta_record.value not in unique_vals:
            unique_vals.add(fasta_record.value)
        else:
            print(f"Duplicate unique_build_id value found: {fasta_record.value}")

    digest_fasta_all(
        fasta_all,
        cvmfs_mount_prefix,
        output_path
    )

def digest_fasta_all(
    fasta_all: list[FastaAllRecord],
    cvmfs_mount_prefix: Path,
    output_path: Path
):
    all_digests = {}
    for fasta_record in fasta_all:
        unique_build_id = fasta_record.value

        cvmfs_fasta_path = cvmfs_mount_prefix / Path(fasta_record.path).relative_to(
            cvmfs_mount_prefix.anchor
        )
        store = RefgetStore.in_memory()

        collection, new = store.add_sequence_collection_from_fasta(fasta_record.path)
        store.add_collection_alias('galaxy_unique_build_id', fasta_record.value, collection.digest)
        store.add_collection_alias('galaxy_dbkey', fasta_record.dbkey, collection.digest)
        store.add_collection_alias('galaxy_name', fasta_record.name, collection.digest)
        store.add_collection_alias('galaxy_loc_file', fasta_record.loc_file, collection.digest)
        store.add_collection_alias('galaxy_tool_data_table_conf', fasta_record.xml_file, collection.digest)

        all_digests[unique_build_id] = {
            "level_0": collection.digest,
            "level_1": {
                "lengths": collection.lengths_digest,
                "names": collection.names_digest,
                "sequences": collection.sequences_digest,
                "name_length_pairs": collection.name_length_pairs_digest,
                "sorted_name_length_pairs": collection.sorted_name_length_pairs_digest,
                "sorted_sequences": collection.sorted_sequences_digest,
            },
            "level_2": store.get_collection_level2(collection.digest),
            "aliases": store.get_aliases_for_collection(collection.digest),
        }

# >>> from refget.utils import fasta_to_seqcol_dict,  seqcol_digest, seqcol_dict_to_level1_dict
# >>> seqcol = fasta_to_seqcol_dict()
# >>> globald = seqcol_digest(seqcol)
# >>> collect = seqcol_dict_to_level1_dict(seqcol)
# >>> collect
# {'lengths': 'UzkbME4hSLXP0-L9KG6gXpQABvSeesda', 'names': 'aEK2wLGTcQ-QUcJo4LsteN7HJbE4BFVE', 'sequences': 'bqcttuF_838R5VjLDpXleJQAx2NxFb7p', 'sorted_name_length_pairs': 'y2EF8IlKTrlTsJg6YElzkVNWTLU7MyUa', 'sorted_sequences': 'bqcttuF_838R5VjLDpXleJQAx2NxFb7p'}

# >>> import gtars.refget
# >>> collect = gtars.refget.digest_fasta('/cvmfs/data.galaxyproject.org/managed/seq/Amel_4.5.fa')
# >>> collect.digest
# 'WVM-8x592B68KwfpbOcMBcAqeNz2ZZy0'
# >>> collect.sequences[0]
# SequenceRecord(name='NC_007070.3', length=29893408, sha512t24u='9q0qXprsO7haivVB3EaU3-44101Q-kyx', is_loaded=false)
# >>> collect.lvl1
# SeqColDigestLvl1(sequences='bqcttuF_838R5VjLDpXleJQAx2NxFb7p', names='aEK2wLGTcQ-QUcJo4LsteN7HJbE4BFVE', lengths='UzkbME4hSLXP0-L9KG6gXpQABvSeesda')

        with open(output_path, "w") as fo:
            yaml.dump(all_digests, fo)



if __name__ == "__main__":
    if 3 <= len(sys.argv) < 5:
        tool_data_table_yaml_path = Path(os.path.abspath(sys.argv[1]))
        output_path = Path(os.path.abspath(sys.argv[2]))
        cvmfs_mount_prefix = Path(sys.argv[3]) if len(sys.argv) == 4 else Path('/')

        main(tool_data_table_yaml_path, output_path, cvmfs_mount_prefix)
    else:
        print("Usage: all_fasta_files_to_refget_seqcol_digest.py tool_data_table_yaml_path output_path [cvmfs_prefix_path]")
        print("Arguments:")
        print("    tool_data_table_yaml_path: Path to the output yaml file from tool_data_table_conf_to_yaml.py")
        print("    output_path: Path to the output yaml file where the refget digests will be stored")
        print("    cvmfs_mount_prefix: Path prefix to where CVMFS is mounted, useful for testing on e.g. a Mac if (default: /)")


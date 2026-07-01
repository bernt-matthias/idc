import os
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


def _read_fasta_all(all_tables_content_yaml_path: Path) -> list[FastaAllRecord]:
    print("Loading the big yaml file.")
    with open(all_tables_content_yaml_path, 'r') as f:
        all_tables_content = yaml.safe_load(f)
    print("Done")

    out = []
    for el in all_tables_content['all_fasta']:
        out.append(FastaAllRecord(**el))
    return out


def main(all_tables_content_yaml_path: Path, output_path: Path, cvmfs_mount_prefix: Path):
    fasta_all = _read_fasta_all(all_tables_content_yaml_path)
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
            "original_info": fasta_record._asdict(),
        }
        
    with open(output_path, "w") as fo:
        yaml.dump(all_digests, fo)


if __name__ == "__main__":
    if 3 <= len(sys.argv) < 5:
        all_tables_content_yaml_path = Path(os.path.abspath(sys.argv[1]))
        output_path = Path(os.path.abspath(sys.argv[2]))
        cvmfs_mount_prefix = Path(sys.argv[3]) if len(sys.argv) == 4 else Path('/')

        main(all_tables_content_yaml_path, output_path, cvmfs_mount_prefix)
    else:
        print("Usage: all_fasta_files_to_refget_seqcol_digest.py all_tables_content_yaml_path output_path [cvmfs_prefix_path]")
        print("Arguments:")
        print("    all_tables_content_yaml_path: Path to the output yaml file from tool_data_table_conf_to_yaml.py")
        print("    output_path: Path to the output yaml file where the refget digests will be stored")
        print("    cvmfs_mount_prefix: Path prefix to where CVMFS is mounted, useful for testing on e.g. a Mac if (default: /)")

import json
import os
import shutil
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
    refget_store_path = output_path.joinpath("store")
    rgsi_output_path = output_path.joinpath("rgsi")
    json_output_path = output_path.joinpath("json")
    os.makedirs(rgsi_output_path, exist_ok=True)
    os.makedirs(json_output_path, exist_ok=True)

    print(f'Created/opened refgetstore at {refget_store_path}')
    store = RefgetStore.on_disk(refget_store_path)

    fasta_all = _read_fasta_all(cvmfs_yaml_path)
    unique_vals = set()
    for fasta_record in fasta_all:
        if fasta_record.value not in unique_vals:
            unique_vals.add(fasta_record.value)
        else:
            print(f"WARNING: Duplicate unique_build_id value found: {fasta_record.value}")


    os.chdir(rgsi_output_path)
    import_fasta_all(
        store,
        fasta_all,
        cvmfs_mount_prefix,
        rgsi_output_path,
        json_output_path,
    )


def import_fasta_all(
    store: RefgetStore,
    fasta_all: list[FastaAllRecord],
    cvmfs_mount_prefix: Path,
    rgsi_output_path: Path,
    json_output_path: Path,
):
    for fasta_record in fasta_all:
        unique_build_id = fasta_record.value

        cvmfs_fasta_path = cvmfs_mount_prefix / Path(fasta_record.path).relative_to(
            cvmfs_mount_prefix.anchor
        )
        local_fasta_path = rgsi_output_path.joinpath(
            unique_build_id + ".fa"
        )

        json_summary_path = json_output_path.joinpath(unique_build_id)

        if not os.path.exists(local_fasta_path):
            if not os.path.exists(cvmfs_fasta_path):
                print(f'WARNING: Fasta file {cvmfs_fasta_path} does not exist, skipping import...')
                continue
            print(f'Symlinking {local_fasta_path} to {cvmfs_fasta_path}...')
            local_fasta_path.symlink_to(cvmfs_fasta_path)
        elif os.path.exists(json_summary_path):
            print(f'JSON summary file {json_summary_path} already exists, skipping import...')
            continue

        collection, new = store.add_sequence_collection_from_fasta(local_fasta_path)
        store.add_collection_alias('galaxy_unique_build_id', fasta_record.value, collection.digest)
        store.add_collection_alias('galaxy_dbkey', fasta_record.dbkey, collection.digest)
        store.add_collection_alias('galaxy_name', fasta_record.name, collection.digest)
        store.add_collection_alias('galaxy_loc_file', fasta_record.loc_file, collection.digest)
        store.add_collection_alias('galaxy_tool_data_table_conf', fasta_record.xml_file, collection.digest)

        refget_metadata_blob = {
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

        with open(json_summary_path, "w") as refget_file:
            print(json.dumps(refget_metadata_blob, indent=2), file=refget_file)


if __name__ == "__main__":
    if 3 <= len(sys.argv) < 5:
        tool_data_table_yaml_path = Path(os.path.abspath(sys.argv[1]))
        output_path = Path(os.path.abspath(sys.argv[2]))
        cvmfs_mount_prefix = Path(sys.argv[3]) if len(sys.argv) == 4 else Path('/')

        main(tool_data_table_yaml_path, output_path, cvmfs_mount_prefix)
    else:
        print("Usage: all_fasta_files_to_refget_store tool_data_table_yaml_path output_path [cvmfs_prefix_path]")
        print("Arguments:")
        print("    tool_data_table_yaml_path: Path to the output yaml file from tool_data_table_conf_to_yaml.py")
        print("    output_path: Path to the output directory where the refget store and digest summaries will be created")
        print("    cvmfs_mount_prefix: Path prefix to where CVMFS is mounted, useful for testing on e.g. a Mac if (default: /)")


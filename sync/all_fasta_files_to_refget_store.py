import argparse
import json
import os
import yaml
from pathlib import Path
from typing import NamedTuple, Any

from gtars.refget import RefgetStore


class FastaAllRecord(NamedTuple):
    dbkey: str
    name: str
    path: str
    value: str
    loc_file: str
    xml_file: str


def main(cvmfs_yaml_path: Path, output_path: Path, cvmfs_mount_prefix: Path, no_store: bool):
    refget_store_path = output_path.joinpath("store")
    rgsi_output_path = output_path.joinpath("rgsi")
    json_output_path = output_path.joinpath("json")
    os.makedirs(rgsi_output_path, exist_ok=True)
    os.makedirs(json_output_path, exist_ok=True)

    if no_store:
        store = None
    else:
        print(f'Created/opened refgetstore at {refget_store_path}')
        store = RefgetStore.on_disk(refget_store_path)

    fasta_all = read_fasta_all_yaml(cvmfs_yaml_path)

    check_for_duplicate_genomes(fasta_all)

    import_fasta_all(
        fasta_all,
        cvmfs_mount_prefix,
        rgsi_output_path,
        json_output_path,
        store,
    )

def read_fasta_all_yaml(cvmfs_yaml_path: Path) -> list[FastaAllRecord]:
    print(f"Loading the big yaml file: {cvmfs_yaml_path}")

    with open(cvmfs_yaml_path, 'r') as cvmfs_yaml_file:
        cvmfs_yaml = yaml.safe_load(cvmfs_yaml_file)

    out = []
    for el in cvmfs_yaml['all_fasta']:
        out.append(FastaAllRecord(**el))
    return out


def check_for_duplicate_genomes(fasta_all: list[FastaAllRecord]):
    unique_vals = set()
    for fasta_record in fasta_all:
        if fasta_record.value not in unique_vals:
            unique_vals.add(fasta_record.value)
        else:
            print(f"WARNING: Duplicate unique_build_id value found: {fasta_record.value}")


def import_fasta_all(
    fasta_all: list[FastaAllRecord],
    cvmfs_mount_prefix: Path,
    rgsi_output_path: Path,
    json_output_path: Path,
    store: RefgetStore | None,
):
    os.chdir(rgsi_output_path)

    for fasta_record in fasta_all:
        unique_build_id = fasta_record.value

        cvmfs_fasta_path = cvmfs_mount_prefix / Path(fasta_record.path).relative_to(
            cvmfs_mount_prefix.anchor
        )
        local_fasta_path = rgsi_output_path.joinpath(
            unique_build_id + ".fa"
        )

        json_summary_path = json_output_path.joinpath(unique_build_id + ".json")

        if not os.path.exists(local_fasta_path):
            if not os.path.exists(cvmfs_fasta_path):
                print(f'WARNING: Fasta file {cvmfs_fasta_path} does not exist, skipping import...')
                continue
            print(f'Symlinking {local_fasta_path} to {cvmfs_fasta_path}...')
            local_fasta_path.symlink_to(cvmfs_fasta_path)
        elif os.path.exists(json_summary_path):
            print(f'JSON summary file {json_summary_path} already exists, skipping import...')
            continue

        if store is None:
            store = RefgetStore.in_memory()

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

        append_to_all_fasta_json_file(json_output_path, unique_build_id, refget_metadata_blob)
        write_single_genome_json_file(json_summary_path, refget_metadata_blob)


def write_single_genome_json_file(json_summary_path: Path, refget_metadata_blob: dict[str, Any]):
    print(f'Writing JSON summary file: {json_summary_path}')
    with open(json_summary_path, "w") as refget_file:
        print(json.dumps(refget_metadata_blob, indent=2), file=refget_file)


def append_to_all_fasta_json_file(json_output_path: Path, unique_build_id: str, refget_metadata_blob: dict[str, Any]):
    all_fasta_json_path = json_output_path.joinpath("all_fasta.json")
    print(f'Appending to all_fasta.json file: {all_fasta_json_path}')

    if os.path.exists(all_fasta_json_path):
        with open(all_fasta_json_path, "r") as all_fasta_file:
            all_fasta_json = json.loads(all_fasta_file.read())
    else:
        all_fasta_json = {}

    all_fasta_json[unique_build_id] = refget_metadata_blob

    with open(all_fasta_json_path, "w") as all_fasta_file:
        print(json.dumps(all_fasta_json, indent=2), file=all_fasta_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates Refgetstore instance from all FASTA tables - "
                    "including 'GA4GH refget: sequence collections'-compatible digests "
                    "and chromLen info."
    )

    parser.add_argument(
        "tool_data_table_yaml_path",
        type=Path,
        help="Path to the output yaml file created by `tool_data_table_conf_to_yaml.py`"
    )

    parser.add_argument(
        "output_path",
        type=Path,
        help="Path to the output directory where the refget store and digest summaries will be "
             "created."
    )

    parser.add_argument(
        "-c", "--cvmfs-mount-prefix",
        type=Path,
        default=Path('/'),
        help="Path prefix to where CVMFS is mounted, useful for testing on e.g. a Mac if (default: /)"
    )

    parser.add_argument(
        "-n", "--no-store",
        action="store_true",
        help="Do not create the Refgetstore."
    )

    args = parser.parse_args()
    main(args.tool_data_table_yaml_path, Path.absolute(args.output_path), args.cvmfs_mount_prefix, args.no_store)

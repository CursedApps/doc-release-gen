#!python3

import argparse
import os
import re
import shutil
import hashlib

from typing import List

link_re = re.compile(r"\[.+?\]\((.+?)\)")

def process_file(doc_path: str, export_path: str, folder: str, file_name: str) -> None:
    # get categories
    complete_path: str = os.path.join(folder, file_name)
    rel_path: str = os.path.relpath(complete_path, doc_path)

    new_file_name: str = "-".join(rel_path.split(os.path.sep))
    with open(os.path.join(export_path, new_file_name), 'w') as new_file:
        # read file
        with open(os.path.join(folder, file_name),'r') as file:
            lines: List[str] = file.readlines()
            for line in lines :
                for match in link_re.finditer(line) :
                    url: str = match.group(1)
                    if not url.startswith("http") :
                        asset_file : str = os.path.realpath(os.path.join(folder, url))
                        if os.path.exists(asset_file) :
                            asset_name, ext =  os.path.splitext(os.path.relpath(asset_file, doc_path))
                            final_name = "./assets/" + hashlib.md5(asset_name.encode()).hexdigest() + ext
                            final_path = os.path.join(export_path, final_name)
                            line = line.replace(url, final_name)
                            if not os.path.exists(final_path) :
                                shutil.copy(asset_file, final_path)
                new_file.writelines([line])
                

def process_folder(doc_path: str, export_path: str, folder: str) -> None :
    print(f"Processing {folder}")
    assert os.path.isdir(folder)
    files: List[str] = os.listdir(folder)

    for file in files:
        realpath: str = os.path.realpath(os.path.join(folder, file))
        if os.path.isdir(realpath) :
            process_folder(doc_path, export_path, realpath)
        elif os.path.isfile(realpath) and file.endswith(".md"):
            process_file(doc_path, export_path, folder, file)


if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument("doc_path", action="store", type=str, help="Path to documentation")
    parser.add_argument("export_path", action="store", type=str, help="Path to generated folder")

    args = parser.parse_args()

    export_path : str = os.path.realpath(args.export_path)
    export_assets_path : str = os.path.realpath(os.path.join(args.export_path, 'assets'))
    doc_path : str = os.path.realpath(args.doc_path)
    if not os.path.exists(export_assets_path) :
        os.makedirs(export_assets_path)

    process_folder(doc_path, export_path, doc_path)

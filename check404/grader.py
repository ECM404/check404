from __future__ import annotations
from os import system, listdir, chdir, mkdir, getcwd
from os.path import isdir, splitext
from zipfile import ZipFile
from check404.parser import get_glob_path
from check404.checker import check
import patoolib


def grader(zipfile: str = "./*.zip", output_dir: str = "./Notas"):
    zipfile = get_glob_path(zipfile)
    yml_path = f"{getcwd()}/**/*.yml"
    if isdir(output_dir):
        system(f"rm -rf {output_dir}")
    unzip(zipfile, output_dir)
    if not isdir(output_dir):
        exit(1)
    individual_zipfiles = listdir(output_dir)
    chdir(output_dir)
    for file in individual_zipfiles:
        student_name = file.split('_')[0]
        unzip(file, f"./{student_name}")
        system(f"rm '{file}'")
        if not isdir(f"./{student_name}"):
            continue
        chdir(f"./{student_name}")
        check(yml_path)
        chdir("..")


def unzip(zipfile: str, output_dir: str):
    _, file_extension = splitext(zipfile)
    if file_extension == ".zip":
        unzip_zip(zipfile, output_dir)
    else:
        unzip_generic(zipfile, output_dir)


def unzip_generic(zipfile: str, output_dir: str):
    if not isdir(output_dir):
        mkdir(output_dir)
    patoolib.extract_archive(zipfile, outdir=output_dir, verbosity=-1)


def unzip_zip(zipfile: str, output_dir: str):
    with ZipFile(zipfile, 'r') as zip_obj:
        zip_obj.extractall(output_dir)

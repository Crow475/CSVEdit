#!/usr/bin/python3
import os
import sys
import argparse
import interface

from csvgen import generate_file

argument_parser = argparse.ArgumentParser()

argument_parser.add_argument("file_name",
                             help="path to the file",
                             type=str
                            )
argument_parser.add_argument("-n", "--new",
                             help="create a new file instead of editing",
                             action="store_true"
                            )

arguments = argument_parser.parse_args()

parameters = {"filename" : arguments.file_name,
              "absolute_path" : os.path.abspath(arguments.file_name),
              "temp_file" : arguments.file_name + ".tmp",
              "new_file" : False,
              "read_only" : not os.access(arguments.file_name, os.W_OK),
              "cell_size" : 28,
              "key_mappings" : None,
             }

if arguments.new and not os.path.isfile(arguments.file_name):
    parameters["filename"] = parameters["temp_file"]
    generate_file(file_name = parameters["temp_file"], cell_text = "")
    parameters["new_file"] = True
    parameters["read_only"] = not os.access(parameters["temp_file"], os.W_OK)

try:
    interface.start(**parameters)
except FileNotFoundError:
    print(f"[Error] No such file: '{arguments.file_name}'")
    sys.exit(1)
except PermissionError:
    print(f"[Error] Access denied: '{arguments.file_name}'")
    sys.exit(2)
sys.exit(0)

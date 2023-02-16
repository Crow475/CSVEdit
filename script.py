#!/usr/bin/python3
import tables
import sys

new_table = tables.file_open(sys.argv[1])
new_table.insert_row(2)
tables.file_save(new_table, sys.argv[2])

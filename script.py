#! /usr/bin/env pyton3
import main as m
import sys

new_table = m.file_opener(sys.argv[1]) #pylint: disable=E1101
print(new_table)
print(new_table.column_count)
print(new_table.row_count)
new_table.add_row() #pylint: disable=E1101
print(new_table)
print(new_table.column_count)
print(new_table.row_count)
new_table.add_column() #pylint: disable=E1101
print(new_table)
print(new_table.column_count)
print(new_table.row_count)
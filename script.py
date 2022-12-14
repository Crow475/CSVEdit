#!/usr/bin/python3
import main as m
import sys

new_table = m.file_opener(sys.argv[1]) #pylint: disable=E1101
print(new_table)
print(new_table.column_count)
print(new_table.row_count)
print(new_table.max_len('B'))
new_table.add_row() #pylint: disable=E1101
print(new_table)
print(new_table.column_count)
print(new_table.row_count)
print(new_table.max_len('B'))
new_table.add_column() #pylint: disable=E1101
print(new_table)
print(new_table.column_count)
print(new_table.row_count)
print(new_table.max_len('B'))
print(new_table.get_cell('F', 1) is None)
print(new_table.set_cell('F', 1, '-'))
print(new_table)
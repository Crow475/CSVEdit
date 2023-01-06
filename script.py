#!/usr/bin/python3
import main as m
import sys

new_table = m.file_opener(sys.argv[1])
#new_table.add_row()
#new_table.add_column()
#new_table.set_cell(1, 1, 'B')
m.file_save(new_table, sys.argv[2])

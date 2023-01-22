#!/usr/bin/python3
import sys

def generate_file(file_name: str, number_of_collumns: int = 2, number_of_rows: int = 2, cell_text: str = 'text'):
    with open(file_name, 'w', encoding='utf-8') as file:
        for y in range(number_of_rows):
            for x in range(number_of_collumns):
                file.write(cell_text)
                if x < number_of_collumns - 1:
                    file.write(',')
            if y < number_of_rows - 1:
                file.write('\n')

generate_file(str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), str(sys.argv[4]))

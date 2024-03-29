"""
This module is a part of CSVEdit.
It contains a "Table" class that stores values of any type, and functions
that allow turning csv files into tables and vice versa.
"""
import csv
from quotesniff import sniff_quoting

# Symbols that sniffer can use as delimeters
# Default: ',;|\t'
valid_delimeters = ',;|\t'

def get_column(column):
    """
    Function that returns alpha name of a column
    from its numerical representation
    """

    if isinstance(column, str) and column.isalpha():
        return column
    result = []
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while column:
        column, remainder = divmod(column - 1, 26)
        result[:0] = alphabet[remainder]
    return ''.join(result)

class Table:
    """
    A class that stores values of any type in a table,
    """
    def __init__(self, column_count, row_count):
        # Creates an empty (filled with None values) table with
        # [row_count] rows and [column_count] columns and no dialect
        self.dialect = None
        self.column_count = column_count
        self.row_count = row_count
        self.columns = {}
        for column in range(1, self.column_count + 1):
            self.columns[get_column(column)] = [None for i in range(1, self.row_count + 1)]

    def get_cell(self, column, row: int):
        """Returns the value stored in a cell"""
        return self.columns[get_column(column)][row - 1]

    def set_cell(self, column, row: int, value):
        """Sets the value of a cell"""
        self.columns[get_column(column)][row  - 1] = value

    def add_column(self):
        """Adds an empty column to the right of the table"""
        new_column_letter = get_column(self.column_count + 1)
        self.columns[new_column_letter] = [None for i in range(1, self.row_count + 1)]
        self.column_count += 1

    def add_row(self):
        """Adds an empty row to the bottom of the table"""
        self.row_count += 1
        for column in range(1, self.column_count + 1):
            self.columns[get_column(column)].append(None)

    def insert_column(self, column_index: int):
        """ Inserts an empty column in the table at a given index """
        self.add_column()
        for index in reversed(range(column_index + 1, self.column_count)):
            temp_column = self.columns[get_column(index)]
            self.columns[get_column(index)] = self.columns[get_column(index + 1)]
            self.columns[get_column(index + 1)] = temp_column

    def insert_row(self, row_index: int):
        """ Inserts an empty row in the table at a given index """
        self.add_row()
        for index in reversed(range(row_index, self.row_count - 1)):
            temp_row = []
            for column in range(1, self.column_count + 1):
                temp_row.append(self.columns[get_column(column)][index])
            for column in range(1, self.column_count + 1):
                self.columns[get_column(column)][index] = self.columns[get_column(column)][index + 1]
            for column in range(1, self.column_count + 1):
                self.columns[get_column(column)][index + 1] = temp_row[column - 1]

    def remove_column(self, column_index: int):
        """Removes a column from a table at a given index"""
        for index in range(column_index, self.column_count):
            temp_column = self.columns[get_column(index)]
            self.columns[get_column(index)] = self.columns[get_column(index + 1)]
            self.columns[get_column(index + 1)] = temp_column
        self.columns.pop(get_column(self.column_count), None)
        self.column_count -= 1

    def remove_row(self, row_index: int):
        """Removes a row from a table at a given index"""
        for index in range(row_index - 1, self.row_count - 1):
            temp_row = []
            for column in range(1, self.column_count + 1):
                temp_row.append(self.columns[get_column(column)][index])
            for column in range(1, self.column_count + 1):
                self.columns[get_column(column)][index] = self.columns[get_column(column)][index + 1]
            for column in range(1, self.column_count + 1):
                self.columns[get_column(column)][index + 1] = temp_row[column - 1]
        for index in range(self.column_count):
            self.columns[get_column(index + 1)].pop(self.row_count - 1)
        self.row_count -= 1

    def column_is_empty(self, column):
        result = True
        for index in range(self.row_count):
            match self.get_cell(column, index + 1):
                case None | "" :
                    continue
                case _:
                    result = False
                    break
        return result

    def row_is_empty(self, row: int):
        result = True
        for index in range(self.column_count):
            match self.get_cell(index + 1, row):
                case None | "" :
                    continue
                case _:
                    result = False
                    break
        return result

    def max_len(self, column):
        """Returns the maximum length of the values a column"""
        longest = 1
        for value in self.columns[get_column(column)]:
            if len(str(value)) > longest:
                longest = len(str(value))
        return longest

    def __str__(self):
        # Crudely represents table as a string by
        # separating cells with '|' symbol
        return_string = ""
        for i in range(1, self.row_count + 1):
            return_string = return_string + " | "
            for j in range(1, self.column_count + 1):
                return_string = (return_string
                + str(self.get_cell(j, i)) + " | ")
            return_string = return_string + "\n"
        return return_string

def file_open(file_name):
    """Opens a csv file as a table object"""
    with open(file_name, encoding="utf-8") as file:
        # Determine the dialect of the file
        dialect = csv.Sniffer().sniff(file.readline(), delimiters=valid_delimeters)
        dialect.quoting = sniff_quoting(file_name, dialect)

        file.seek(0)

        filereader = csv.reader(file, dialect)

        # Determine the number of columns and rows in the file
        # to create a table based on it
        max_rows = 0
        max_columns = 0
        for row in filereader:
            if len(row) > max_columns:
                max_columns = len(row)
            max_rows = max_rows + 1

        # Create emty table and set its dialect
        return_table = Table(max_columns, max_rows)
        return_table.dialect = dialect

        file.seek(0)

        # Fill the table with data from the file
        current_row = 0
        for row in filereader:
            current_row += 1
            for column, value in enumerate(row):
                if value == "":
                    return_table.set_cell(column + 1, current_row, None)
                    continue
                return_table.set_cell(column + 1, current_row, value)

    return return_table

def file_save(table: Table, file_name):
    """Saves a table object as a csv file"""
    with open(file_name, "w", encoding="utf-8") as file:
        writer = csv.writer(file, dialect=table.dialect)
        for row in range (1, table.row_count + 1):
            row_out = []
            for column in range (1, table.column_count + 1):
                if table.get_cell(column, row) is None or table.get_cell(column, row) == 'None':
                    row_out.append('')
                else:
                    row_out.append(table.get_cell(column, row))
            writer.writerow(row_out)

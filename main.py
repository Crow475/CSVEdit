import csv
from quotesniff import sniff_quoting

# Default name of the dialect that is sniffed from a file
auto_dialect_name = 'default'

# Symbols that sniffer can use as delimeters
# Default: ',;|\t'
valid_delimeters = ',;|\t'

def get_column(column):
    """
    Function that returns alpha name of a column
    from its numerical representation
    """

    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if type(column) == str and column.isalpha():
        return column
    return alphabet[column - 1]

class Table:
    """
    A class that stores values of any type in a table,
    limited to 26 columns (for now)
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

class Pointer():
    """
    A class that defines a pointer for the interface.
    It has its own coordinates and methods of moving.
    """
    def __init__(self, column_number, row):
        # Creates a pointer with set coordinates
        self.column_number = column_number
        self.row = row
        self.update_column()

    def update_column(self):
        """Updates the column letter"""
        self.column = get_column(self.column_number)

    def right(self):
        """Moves the pointer one column right"""
        self.column_number += 1
        self.update_column()

    def left(self):
        """Moves the pointer one column left"""
        self.column_number -= 1
        self.update_column()

    def down(self):
        """Moves the pointer one row down"""
        self.row += 1

    def up(self):
        """Moves the pointer one row up"""
        self.row -= 1

def file_opener(file_name):
    """Opens a csv file as a table object"""
    with open(file_name, encoding="utf-8") as file:
        # Determine the dialect of the file and register it
        dialect = csv.Sniffer().sniff(file.readline(), delimiters=valid_delimeters)
        dialect.quoting = sniff_quoting(file_name, dialect)
        csv.register_dialect(auto_dialect_name, dialect)

        file.seek(0)

        filereader = csv.reader(file, dialect)

        # Determine the number of columns and row in the file
        # to create a table based on it
        max_rows = 0
        max_columns = 0
        for row in filereader:
            if len(row) > max_columns:
                max_columns = len(row)
            max_rows = max_rows + 1

        # Create emty table and set its dialect
        return_table = Table(max_columns, max_rows)
        return_table.dialect = csv.get_dialect(auto_dialect_name)

        file.seek(0)

        # Fill the table with data from the file
        current_row = 0
        for row in filereader:
            current_row += 1
            for column, value in enumerate(row):
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
        csv.unregister_dialect(auto_dialect_name)

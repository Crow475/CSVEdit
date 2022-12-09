import csv
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class table:
    def __init__(self, column_count, row_count):
        self.column_count = column_count
        self.row_count = row_count
        self.columns = {}
        for column in range(1, column_count + 1):
            column_alpha = alphabet[column - 1]
            self.columns[column_alpha] = [None for i in range(1, row_count + 1)]
    
    def get_cell(self, column: str, row: int):
        return self.columns[column][row - 1]

    def set_cell(self, column: str, row: int, value):
        self.columns[column][row  - 1] = value

    def __str__(self):
        return_string = ""
        for i in range(1, self.row_count + 1):
            return_string = return_string + " | "
            for j in range(1, self.column_count + 1):
                j_alpha = alphabet[j - 1]
                return_string = return_string + str(self.get_cell(j_alpha, i)) + " | "
            return_string = return_string + "\n"
        return return_string

def file_opener(file_name):
    with open(file_name, encoding="utf-8") as file:
        filereader = csv.reader(file)
        max_rows = 0
        max_columns = 0
        for row in filereader:
            if len(row) > max_columns:
                max_columns = len(row)
            max_rows = max_rows + 1

        return_table = table(max_columns, max_rows)

        file.seek(0)
        current_row = 0
        for row in filereader:
            current_row += 1
            for column, value in enumerate(row):
                column_alpha = alphabet[column]
                return_table.set_cell(column_alpha, current_row, value)
    
    return return_table

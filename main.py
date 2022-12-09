alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class table:
    def __init__(self, column_count, row_count):
        self.column_count = column_count
        self.row_count = row_count
        self.columns = {}
        for column in range(1, column_count + 1):
            column_alpha = alphabet[column]
            self.columns[column_alpha] = [None for i in range(1, row_count + 1)]

test_table = table(3, 4)


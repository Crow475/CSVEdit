import csv
import re

def sniff_quoting(file_name, dialect = None, quotechar = None, delimiter = None):
    quoted_values = []
    cells = []

    with open(file_name, encoding="utf-8") as file:
        if not dialect:
            if not delimiter:
                dialect = csv.Sniffer().sniff(file.readline())
            else:
                dialect = csv.Sniffer().sniff(file.readline(), delimiters=delimiter)
        if not quotechar:
            quotechar = dialect.quotechar
        if not delimiter:
            delimiter = dialect.delimiter

        file.seek(0)
        file_reader = csv.reader(file, dialect, delimiter=delimiter)
        for row in file_reader:
            for value in row:
                cells.append(value)

        file.seek(0)
        pattern = rf"{quotechar}([^{quotechar}]+){quotechar}"
        text = file.read()
        quoted_values = re.findall(pattern, text)
        with_delimiter = 0
        non_numeric = 0
        other = 0
        for value in quoted_values:
            if delimiter in value and not str(value).isdigit():
                with_delimiter += 1
                non_numeric += 1
            elif delimiter in value:
                with_delimiter += 1
            elif not str(value).isdigit():
                non_numeric += 1
            else:
                other += 1

    if len(cells) == len(quoted_values):
        return csv.QUOTE_ALL
    if len(quoted_values) == with_delimiter and len(quoted_values) != 0:
        return csv.QUOTE_MINIMAL
    if len(quoted_values) == non_numeric and len(quoted_values) != 0:
        return csv.QUOTE_NONNUMERIC
    if dialect.escapechar:
        return csv.QUOTE_NONE
    return csv.QUOTE_MINIMAL

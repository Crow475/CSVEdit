#!/usr/bin/python3
import os
import sys
import curses
import argparse

import tables
import inputfield

class Pointer:
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
        self.column = tables.get_column(self.column_number)

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

argument_parser = argparse.ArgumentParser()

argument_parser.add_argument("file_name", help="path to the file", type=str)
arguments = argument_parser.parse_args()

try:
    table = tables.file_opener(arguments.file_name)
except FileNotFoundError:
    print(f"[Error] No such file: '{arguments.file_name}'")
    sys.exit(1)
except PermissionError:
    print(f"[Error] Access denied: '{arguments.file_name}'")
    sys.exit(2)

read_only = not os.access(arguments.file_name, os.W_OK)
absolute_path = os.path.abspath(arguments.file_name)

def main(scr):
    scr.keypad(True)
    scr.clear()
    curses.curs_set(False)
    curses.halfdelay(1)

    table_height = table.row_count + 1
    table_width = table.column_count * 20 + table.column_count * 3

    selector = Pointer(1, 1)
    shown_collumns = []
    shown_rows = []
    x_shift = 0
    y_shift = 0
    address = f"({selector.column:>3}:{selector.row:<3})"

    mode = 'R'
    alert = None
    changes = False

    info = {'message':None,
            'mode':False
           }

    key_hint = {'edit':' [RETURN]:edit',
                'confirm':' [RETURN]:confirm',
                'quit':' [q]:quit',
                'cancel':' [esc]:cancel',
                'update':' [f5]:update',
               }

    row_width = len(str(table.row_count))
    max_cell_length = 28

    height, width = scr.getmaxyx()
    table_pad = curses.newpad(table_height, table_width)
    column_pad = curses.newpad(1, table_width + 2)
    if table_height > height - 2:
        row_pad = curses.newpad(table_height, row_width)
    else:
        row_pad = curses.newpad(height - 2, row_width)
    input_pad = curses.newpad(1, 255)
    input_win = curses.newwin(1, width - 9 - 2, height - 1, 2)

    def save_as():
        nonlocal info
        nonlocal alert
        info['message'] = "Save as: " + key_hint["confirm"] + key_hint["cancel"]
        info['mode'] = False
        alert = "?"
        update_all()
        file_path = inputfield.get_input(input_win, absolute_path, CancelReturnsNone= True)
        if file_path:
            try:
                tables.file_save(table, file_path)
            except PermissionError:
                show_error("Error: Access denied")
        info['message'] = None
        alert = None
        update_all()

    def show_error(message: str):
        nonlocal info
        nonlocal alert
        info['message'] = message + key_hint["confirm"]
        alert = "!"
        update_all()
        inputfield.get_input(input_win)
        info['message'] = None
        alert = None
        update_all()

    def show_prompt(message: str):
        nonlocal info
        nonlocal alert
        info["message"] = message + "[y/n]" + key_hint["cancel"]
        alert = "?"
        update_all()
        answer = inputfield.get_input(input_win)
        if str(answer).strip().lower() in ['yes', 'y']:
            info['message'] = None
            alert = None
            update_all()
            return True
        if str(answer).strip().lower() in ['no', 'n']:
            info['message'] = None
            alert = None
            update_all()
            return False
        info['message'] = None
        alert = None
        update_all()
        return None


    def get_quoting_ind(quoting):
        if quoting == 0:
            return 'M'
        if quoting == 1:
            return 'A'
        if quoting == 2:
            return 'L'
        if quoting == 3:
            return 'N'
        return ' '

    def update_info(info_message: str = None, show_mode: bool = False):

        info_mode = " Mode:"

        if read_only:
            info_keys = key_hint["quit"] + " "
        else:
            info_keys = key_hint["edit"] + key_hint["quit"] + " "

        if not info_message:
            info_message = info_keys
            show_mode = True

        if show_mode:
            info_spacer_len = (width-2)-(len(info_message) + len(info_mode) + row_width)
            if info_spacer_len > 0:
                info_message = f"{info_message}{' ':^{info_spacer_len}}{info_mode}"

        if len(info_message) >= width - 1:
            info_message = ' '

        info_win = curses.newwin(1, width - row_width, height - 2, row_width)
        info_win.addstr(0, 0, f"{info_message:<{width - row_width - 1}}", curses.A_REVERSE)
        info_win.noutrefresh()

    def update_table():
        table_pad.erase()
        shown_collumns.clear()
        shown_rows.clear()
        for y in range(table.row_count - y_shift):
            x_display = 0
            y = y + y_shift
            for x in range(table.column_count - x_shift):
                x = x + x_shift
                cell_display = table.get_cell(x + 1, y + 1)
                if cell_display is None or cell_display == '':
                    cell_display = "-"
                cell_display = str(cell_display).strip()
                if len(cell_display) > max_cell_length:
                    cell_display = cell_display[:max_cell_length - 3]
                    cell_display = cell_display + "..."
                cell_display = f" {cell_display:^{min(table.max_len(x + 1), max_cell_length)}} "
                if selector.column_number == x + 1 and selector.row == y + 1:
                    table_pad.addstr(y - y_shift, x_display, cell_display, curses.A_BLINK)
                else:
                    table_pad.addstr(y - y_shift, x_display, cell_display)
                x_display = x_display + min(table.max_len(x + 1), max_cell_length) + 2
                table_pad.addstr(y - y_shift, x_display, '|')
                x_display += 1
                if x_display < width - 3 and tables.get_column(x + 1) not in shown_collumns:
                    shown_collumns.append(tables.get_column(x + 1))
            if y < height - 3 + y_shift:
                shown_rows.append(y + 1)
        table_pad.noutrefresh(0, 0, 1, row_width, height - 3, width - 2)

    def update_indicator():
        indicator_win = curses.newwin(height - 2, 2, 1, width - 1)
        indicators = ''
        if alert:
            indicators += alert
        indicators += get_quoting_ind(table.dialect.quoting)
        indicators = f"{indicators:<{height - 3}}"
        for index, symbol in enumerate(indicators):
            indicator_win.addstr(index, 0, symbol, curses.A_REVERSE)
        if read_only:
            indicator_win.addstr(height - 3, 0, "R", curses.A_REVERSE + curses.A_UNDERLINE)
        else:
            indicator_win.addstr(height - 3, 0, mode, curses.A_REVERSE)
        indicator_win.noutrefresh()

    def update_columns():
        x_display = 0
        for x in range(table.column_count - x_shift):
            x = x + x_shift
            colum_len = min(table.max_len(x + 1), max_cell_length)
            column_name = f" {str(tables.get_column(x + 1)):^{colum_len}} |"
            column_pad.addstr(0, x_display, column_name, curses.A_REVERSE)
            x_display = x_display + colum_len + 3
        if x_display < width - 2:
            column_spacer = ' ' * ((width - 2) - x_display)
            column_pad.addstr(0, x_display, column_spacer, curses.A_REVERSE)
        column_pad.noutrefresh(0, 0, 0, row_width, 0, width - 2)

    def update_rows():
        for y in range(table.row_count - y_shift):
            y = y + y_shift
            row_pad.addstr(y - y_shift, 0, f"{str(y + 1):^{row_width}}", curses.A_REVERSE)
        if y + 1 < height - 3:
            row_spacer  = ' '
            for i in range(y + 1, height - 3):
                row_pad.addstr(i, 0, f"{row_spacer:^{row_width}}", curses.A_REVERSE)
        row_pad.noutrefresh(0, 0, 1, 0, height - 3, row_width)

    def update_x():
        x_win = curses.newwin(1, row_width, 0, 0)
        if x_shift > 0 and y_shift > 0:
            x_win.insstr(0, 0, f"{'X':^{row_width}}", curses.A_REVERSE)
        elif x_shift > 0:
            x_win.insstr(0, 0, f"{'<':^{row_width}}", curses.A_REVERSE)
        elif y_shift > 0:
            x_win.insstr(0, 0, f"{'^':^{row_width}}", curses.A_REVERSE)
        else:
            x_win.insstr(0, 0, f"{' ':^{row_width}}", curses.A_REVERSE)
        x_win.noutrefresh()

    def update_v():
        v_win = curses.newwin(1, row_width, height - 2, 0)
        if shown_rows[-1] != table.row_count:
            v_win.insstr(0, 0, f"{'V':^{row_width}}", curses.A_REVERSE)
        else:
            v_win.insstr(0, 0, f"{' ':^{row_width}}", curses.A_REVERSE)
        v_win.noutrefresh()

    def update_r():
        r_win = curses.newwin(1, 2, 0, width - 1)
        if shown_collumns[-1] != tables.get_column(table.column_count):
            r_win.insstr(0, 0, ">", curses.A_REVERSE)
        else:
            r_win.insstr(0, 0, " ", curses.A_REVERSE)
        r_win.noutrefresh()

    def update_input():
        nonlocal input_win

        input_pad.erase()
        value = str(table.get_cell(selector.column, selector.row))
        value = f"> {value}"
        input_length = width - 2 - len(address)
        if len(value) > input_length:
            value = value[:input_length - 3] + "..."
        input_pad.addstr(0, 0, value)
        input_win = curses.newwin(1, width - len(address) - 2, height - 1, 2)
        input_pad.noutrefresh(0, 0, height - 1, 0, height - 1, input_length)

    def update_address():
        address = f"({selector.column:>3}:{selector.row:<3})"
        address_win = curses.newwin(1, len(address), height - 1, width - len(address))
        address_win.insstr(0, 0, address, curses.A_REVERSE)
        address_win.noutrefresh()

    def update_all():
        update_table()
        update_x()
        update_v()
        update_r()
        update_info(info["message"], info["mode"])
        update_columns()
        update_rows()
        update_input()
        update_address()
        update_indicator()
        curses.flash()

    update_all()
    curses.doupdate()

    input_pad.move(0, 0)
    input_pad.keypad(True)

    while True:
        user_input = input_pad.getch()
        height, width = scr.getmaxyx()
        if user_input == curses.KEY_F5:
            update_all()
        if user_input == ord('q'):
            if changes:
                answer = show_prompt("Do you want to save changes to the file?")
                if answer is True:
                    save_as()
                    break
                if answer is False:
                    break
            else:
                break
        if user_input == ord('s'):
            save_as()
            changes = False
        if user_input == curses.KEY_RESIZE:
            height, width = scr.getmaxyx()
            update_all()
        if user_input == curses.KEY_RIGHT and selector.column_number < table.column_count:
            selector.right()
            if selector.column not in shown_collumns:
                x_shift += 1
            update_table()
            update_r()
            update_x()
            update_columns()
            update_address()
            update_input()
        if user_input == curses.KEY_LEFT and selector.column_number > 1:
            selector.left()
            if selector.column not in shown_collumns:
                x_shift -= 1
            update_table()
            update_r()
            update_x()
            update_columns()
            update_address()
            update_input()
        if user_input == curses.KEY_DOWN and selector.row < table.row_count:
            selector.down()
            if selector.row not in shown_rows:
                y_shift += 1
            update_table()
            update_v()
            update_x()
            update_rows()
            update_address()
            update_input()
        if user_input == curses.KEY_UP and selector.row > 1:
            selector.up()
            if selector.row not in shown_rows:
                y_shift -= 1
            update_table()
            update_v()
            update_x()
            update_rows()
            update_address()
            update_input()
        if user_input in (curses.KEY_ENTER, 10, 13):
            if not read_only and mode == 'R':
                mode = 'E'
                info["message"] = key_hint["confirm"] + key_hint["cancel"]
                info["mode"] = True
                update_info(info["message"], info["mode"])
                update_indicator()
                update_input()
                update_address()
                value = table.get_cell(selector.column, selector.row)
                value = inputfield.get_input(input_win, value)
                table.set_cell(selector.column, selector.row, value)
                changes = True
                info["message"] = None
                info["mode"] = False
                mode = 'R'
                update_all()
        curses.doupdate()

curses.wrapper(main)
sys.exit(0)

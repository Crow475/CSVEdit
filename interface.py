#!/usr/bin/python3
import curses
import sys
import os
import argparse
import main as m

argument_parser = argparse.ArgumentParser()

argument_parser.add_argument("file_name", help="path to the file", type=str)
arguments = argument_parser.parse_args()

try:
    table = m.file_opener(arguments.file_name)
except FileNotFoundError:
    print(f"[Error] No such file: '{arguments.file_name}'")
    sys.exit(1)
except PermissionError:
    print(f"[Error] Access denied: '{arguments.file_name}'")
    sys.exit(2)

read_only = not os.access(arguments.file_name, os.W_OK)

def main(scr):
    scr.keypad(True)
    scr.clear()
    curses.curs_set(False)

    row_width = len(str(table.row_count))

    height, width = scr.getmaxyx()
    table_pad = curses.newpad(100, 200)
    column_pad = curses.newpad(1, 200)
    row_pad = curses.newpad(100, row_width)
    input_pad = curses.newpad(1, 100)

    selector = m.Pointer(1, 1)
    shown_collumns = []
    shown_rows = []
    x_shift = 0
    y_shift = 0
    address = f"({selector.column:>3}:{selector.row:<3})"

    def update_info():
        if read_only:
            info_keys = " [q]:quit "
        else:
            info_keys = " [RETURN]:edit mode [q]:quit "
        info_mode = " Mode: R "
        if len(info_keys) + len(info_mode) >= width - 3:
            info_keys = ''
            info_mode = ''
        info_spacer_len = (width-3)-(len(info_keys)+len(info_mode))
        info_win = curses.newwin(2, width - 2, height - 2, 1)
        info_win.addstr(0, 0, f"{info_keys}{' ':^{info_spacer_len}}{info_mode}", curses.A_REVERSE)
        info_win.noutrefresh()

    def update_table():
        table_pad.clear()
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
                cell_display = cell_display.strip()
                cell_display = f" {str(cell_display):^{table.max_len(x + 1)}} "
                if selector.column_number == x + 1 and selector.row == y + 1:
                    table_pad.addstr(y - y_shift, x_display, cell_display, curses.A_BLINK)
                else:
                    table_pad.addstr(y - y_shift, x_display, cell_display)
                x_display = x_display + table.max_len(x + 1) + 2
                table_pad.addstr(y - y_shift, x_display, '|')
                x_display += 1
                if x_display < width - 3 and m.get_column(x + 1) not in shown_collumns:
                    shown_collumns.append(m.get_column(x + 1))
            if y < height - 3 + y_shift:
                shown_rows.append(y + 1)
        table_pad.noutrefresh(0, 0, 1, row_width, height - 3, width - 2)

    def update_columns():
        x_display = 0
        for x in range(table.column_count - x_shift):
            x = x + x_shift
            column_name = f" {str(m.get_column(x + 1)):^{table.max_len(x + 1)}} |"
            column_pad.addstr(0, x_display, column_name, curses.A_REVERSE)
            x_display = x_display + table.max_len(x + 1) + 3
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
        if shown_collumns[-1] != m.get_column(table.column_count):
            r_win.insstr(0, 0, ">", curses.A_REVERSE)
        else:
            r_win.insstr(0, 0, " ", curses.A_REVERSE)
        r_win.noutrefresh()

    def update_input():
        input_pad.clear()
        input_pad.addstr(0, 0, f"> {str(table.get_cell(selector.column, selector.row))}")
        input_pad.noutrefresh(0, 0, height - 1, 0, height - 1, width - 1 - len(address))

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
        update_info()
        update_columns()
        update_rows()
        update_input()
        update_address()

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
            break
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
        curses.doupdate()

curses.wrapper(main)
sys.exit(0)

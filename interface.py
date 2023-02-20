#!/usr/bin/python3
import os
import sys
import curses
import argparse

import tables
import inputfield
import visuals

key_hint = {'edit':' [RETURN]:edit',
            'confirm':' [RETURN]:confirm',
            'quit':' [q]:quit',
            'cancel':' [esc]:cancel',
            'update':' [f5]:update',
            }

max_cell_length = 28

argument_parser = argparse.ArgumentParser()

argument_parser.add_argument("file_name", help="path to the file", type=str)
argument_parser.add_argument("-n", "--new", help="create a new file instead of editing", action="store_true")
arguments = argument_parser.parse_args()

temp_file = arguments.file_name + ".tmp"

try:
    table = tables.file_open(arguments.file_name)
except FileNotFoundError:
    if not arguments.new:
        print(f"[Error] No such file: '{arguments.file_name}'")
        sys.exit(1)
    table = tables.file_create(temp_file)
except PermissionError:
    print(f"[Error] Access denied: '{arguments.file_name}'")
    sys.exit(2)

read_only = not os.access(arguments.file_name, os.W_OK)
if arguments.new:
    read_only = not os.access(temp_file, os.W_OK)
absolute_path = os.path.abspath(arguments.file_name)

def main(scr):
    scr.keypad(True)
    scr.clear()
    curses.curs_set(False)
    curses.halfdelay(1)

    table_height = table.row_count + 1
    table_width = table.column_count * max_cell_length + table.column_count * 3

    pointer = visuals.Pointer(1, 1)

    info = visuals.Info(default_message = key_hint["edit"] + key_hint["quit"] + " ")
    if read_only:
        info = visuals.Info(default_message = key_hint["quit"] + " ")

    shown_collumns = []
    shown_rows = []
    x_shift = 0
    y_shift = 0
    changes = False

    address = f"({pointer.column:>3}:{pointer.row:<3})"
    row_width = len(str(table.row_count))
    height, width = scr.getmaxyx()

    input_win = curses.newwin(1, width - 2, height - 1, 2)
    key_pad = curses.newpad(1, 1)

    def update_table_size():
        nonlocal table_height, table_width, row_width

        table_height = table.row_count + 1
        table_width = table.column_count * max_cell_length + table.column_count * 3
        row_width = len(str(table.row_count))

    def save_as():
        nonlocal info
        info.set_alert('?', "Save as: " + key_hint["confirm"] + key_hint["cancel"])
        update_all()
        file_path = inputfield.get_input(input_win, absolute_path, CancelReturnsNone= True)
        if file_path:
            try:
                tables.file_save(table, file_path)
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return 1
            except PermissionError:
                show_error("Error: Access denied")
                return 2
        info.reset_alert()
        update_all()
        return 0

    def show_error(message: str):
        nonlocal info
        info.set_alert('!', message + key_hint["confirm"])
        update_all()
        inputfield.get_input(input_win)
        info.reset_alert()
        update_all()

    def show_prompt(message: str):
        nonlocal info
        info.set_alert('?', message + "[y/n]" + key_hint["cancel"])
        update_all()
        answer = inputfield.get_input(input_win)
        if str(answer).strip().lower() in ['yes', 'y']:
            answer = True
        elif str(answer).strip().lower() in ['no', 'n']:
            answer = False
        else:
            answer = None
        info.reset_alert()
        update_all()
        return answer


    def get_quoting_ind(quoting):
        try:
            quoting_ind = ['M', 'A', 'L', 'N']
            return quoting_ind[quoting]
        except IndexError:
            return ' '

    def update_info(message: str = None, show_mode: bool = False):
        nonlocal info

        if message:
            info.message = message
            info.show_mode = show_mode

        message = info.message

        if info.show_mode:
            spacer_len = (width-2)-(len(info.message) + len(" Mode:") + row_width)
            if spacer_len > 0:
                message = f"{message}{' ':^{spacer_len}} Mode:"

        if len(message) >= width - 1:
            message = ' '

        info_win = curses.newwin(1, width - row_width, height - 2, row_width)
        info_win.addstr(0, 0, f"{message:<{width - row_width - 1}}", curses.A_REVERSE)
        info_win.noutrefresh()

    def update_table():
        table_pad = curses.newpad(max(table_height, height), max(table_width, width))
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
                if pointer.column_number == x + 1 and pointer.row == y + 1:
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
        if info.alert:
            indicators += info.alert
        indicators += get_quoting_ind(table.dialect.quoting)
        indicators = f"{indicators:<{height - 3}}"
        for index, symbol in enumerate(indicators):
            indicator_win.addstr(index, 0, symbol, curses.A_REVERSE)
        if read_only:
            indicator_win.addstr(height - 3, 0, "R", curses.A_REVERSE + curses.A_UNDERLINE)
        else:
            indicator_win.addstr(height - 3, 0, info.mode, curses.A_REVERSE)
        indicator_win.noutrefresh()

    def update_columns():
        column_pad = curses.newpad(1, max(table_width + 2, width - 1))
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
        row_pad = curses.newpad(max(table_height, height - 2), row_width)
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

        input_length = width - 2 - len(address)
        cell_pad = curses.newpad(1, input_length + 1)
        input_win = curses.newwin(1, input_length, height - 1, 2)
        cell_pad.erase()
        value = str(table.get_cell(pointer.column, pointer.row))
        value = f"> {value}"
        if len(value) > input_length:
            value = value[:input_length - 3] + "..."
        cell_pad.addstr(0, 0, value)
        cell_pad.noutrefresh(0, 0, height - 1, 0, height - 1, input_length)

    def update_address():
        address = f"({pointer.column:>3}:{pointer.row:<3})"
        address_win = curses.newwin(1, len(address), height - 1, width - len(address))
        address_win.insstr(0, 0, address, curses.A_REVERSE)
        address_win.noutrefresh()

    def update_all():
        scr.clear()
        update_table()
        update_x()
        update_v()
        update_r()
        update_info()
        update_columns()
        update_rows()
        update_input()
        update_address()
        update_indicator()
        curses.flash()

    def move(direction: str = None, repeat: int = 1):
        nonlocal x_shift, y_shift
        if direction == 'up':
            for _ in range(repeat):
                pointer.up()
                if pointer.row not in shown_rows:
                    y_shift -= 1
        elif direction == 'down':
            for _ in range(repeat):
                pointer.down()
                if pointer.row not in shown_rows:
                    y_shift += 1
        elif direction == 'left':
            for _ in range(repeat):
                pointer.left()
                if pointer.column not in shown_collumns:
                    x_shift -= 1
        elif direction == 'right':
            for _ in range(repeat):
                pointer.right()
                if pointer.column not in shown_collumns:
                    x_shift += 1
        update_table()
        update_r()
        update_v()
        update_x()
        update_columns()
        update_rows()
        update_input()
        update_address()

    update_all()
    curses.doupdate()

    key_pad.keypad(True)

    while True:
        user_input = key_pad.getch()
        height, width = scr.getmaxyx()
        if user_input == curses.KEY_F5:
            update_all()
        if user_input == ord('q'):
            if changes:
                answer = show_prompt("Do you want to save changes to the file?")
                if answer is True:
                    result = 2
                    while result == 2:
                        result = save_as()
                    if result == 1:
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
        if user_input == curses.KEY_RIGHT and pointer.column_number < table.column_count:
            move('right')
        if user_input == curses.KEY_LEFT and pointer.column_number > 1:
            move('left')
        if user_input == curses.KEY_DOWN and pointer.row < table.row_count:
            move('down')
        if user_input == curses.KEY_UP and pointer.row > 1:
            move('up')
        if user_input in [curses.KEY_HOME, curses.KEY_SHOME] and pointer.column_number > 1:
            move('left', pointer.column_number - 1)
        if user_input in [curses.KEY_END, curses.KEY_SEND] and pointer.column_number < table.column_count:
            move('right', table.column_count - pointer.column_number)
        if user_input == curses.KEY_PPAGE and pointer.row > 1:
            move('up', pointer.row - 1)
        if user_input == curses.KEY_NPAGE and pointer.row < table.row_count:
            move('down', table.row_count - pointer.row)
        if not read_only:
            if user_input in (curses.KEY_ENTER, 10, 13) and info.mode == 'R':
                info.mode = 'E'
                info.set_message(key_hint["confirm"] + key_hint["cancel"], True)
                update_info()
                update_indicator()
                update_input()
                update_address()
                value = table.get_cell(pointer.column, pointer.row)
                value = inputfield.get_input(input_win, value)
                table.set_cell(pointer.column, pointer.row, value)
                changes = True
                info.reset_messsage()
                info.mode = 'R'
                update_all()
            if user_input == curses.KEY_DC:
                table.set_cell(pointer.column, pointer.row, None)
                changes = True
                move()
            if user_input == ord('c'):
                table.insert_column(pointer.column_number)
                changes = True
                update_table_size()
                update_table()
                move('right')
            if user_input == ord('C'):
                table.insert_column(pointer.column_number - 1)
                changes = True
                update_table_size()
                update_table()
                move()
            if user_input == ord('v'):
                table.insert_row(pointer.row)
                changes = True
                update_table_size()
                update_table()
                move('down')
            if user_input == ord('V'):
                table.insert_row(pointer.row - 1)
                changes = True
                update_table_size()
                update_table()
                move()
        curses.doupdate()
try:
    curses.wrapper(main)
except Exception as exception:
    tables.file_save(table, temp_file)
    raise exception
if os.path.exists(temp_file):
    os.remove(temp_file)
sys.exit(0)

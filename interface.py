#!/usr/bin/python3
import curses
import sys
import main as m

table = m.file_opener(sys.argv[1])

def main(scr):
    scr.keypad(True)
    scr.clear()
    curses.curs_set(False)

    height, width = scr.getmaxyx()
    table_pad = curses.newpad(100, 200)
    column_pad = curses.newpad(1, 200)
    row_pad = curses.newpad(100, 1)
    x_win = curses.newwin(1, 2, 0, 0)
    v_win = curses.newwin(1, 2, height - 2, 0)
    r_win = curses.newwin(1, 2, 0, width - 1)
    info_win = curses.newwin(2, width - 3, height - 2, 1)

    info_keys = " [RETURN]:edit mode [Q]:quit "
    info_mode = " Mode: R "
    info_spacer_len = (width-3)-(len(info_keys)+len(info_mode))

    def update_info():
        info_win.addstr(0, 0, f"{info_keys}{' ':^{info_spacer_len}}{info_mode}", curses.A_REVERSE)
        info_win.noutrefresh()

    def update_table():
        for y in range(0, table.row_count):
            x_display = 0
            for x in range(table.column_count):
                x_alpha = m.alphabet[x]
                cell_display = table.get_cell(x_alpha, y + 1)
                if cell_display is None or cell_display == '':
                    table.set_cell(x_alpha, y + 1, '-')
                    cell_display = table.get_cell(x_alpha, y + 1)
                cell_display = cell_display.strip()
                cell_display = f" {str(cell_display):^{table.max_len(x_alpha)}} |" #pylint: disable=E1101
                table_pad.addstr(y, x_display, cell_display)
                x_display = x_display + table.max_len(x_alpha) + 3 #pylint: disable=E1101
        table_pad.noutrefresh(0, 0, 1, 1, height - 3, width - 2)

    def update_columns():
        x_display = 0
        for x in range(table.column_count):
            x_alpha  = m.alphabet[x]
            column_name = f" {str(x_alpha):^{table.max_len(x_alpha)}} |" #pylint: disable=E1101
            column_pad.addstr(0, x_display, column_name, curses.A_REVERSE)
            x_display = x_display + table.max_len(x_alpha) + 3 #pylint: disable=E1101
        if x_display < width - 2:
            column_spacer = ' ' * ((width - 2) - x_display)
            column_pad.addstr(0, x_display, column_spacer, curses.A_REVERSE)
        column_pad.noutrefresh(0, 0, 0, 1, 0, width - 2)

    def update_rows():
        for y in range(0, table.row_count):
            row_pad.addstr(y, 0, str(y + 1), curses.A_REVERSE)
        if y + 1 < height - 3:
            row_spacer  = ' '
            for i in range(y + 1, height - 3):
                row_pad.addstr(i, 0, row_spacer, curses.A_REVERSE)
        row_pad.noutrefresh(0, 0, 1, 0, height - 3, 1)

    def update_x():
        x_win.addstr(0, 0, "X", curses.A_REVERSE)
        x_win.noutrefresh()

    def update_v():
        v_win.addstr(0, 0, "V", curses.A_REVERSE)
        v_win.noutrefresh()

    def update_r():
        r_win.addstr(0, 0, ">", curses.A_REVERSE)
        r_win.noutrefresh()

    update_table()
    update_x()
    update_v()
    update_r()
    update_info()
    update_columns()
    update_rows()

    curses.doupdate()
    info_win.getch()

curses.wrapper(main)

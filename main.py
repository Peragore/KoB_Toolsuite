import time

import build_ticker
import threading
import PySimpleGUI as sg
from os import path
from threading import Thread
from collections import deque
tab_names = build_ticker.get_tab_names()
tab_names.insert(0, '')

col_1 = [[sg.Text('Mainstream Group'), sg.Combo(tab_names, default_value=tab_names[0], key='dropdown1'),
          sg.Text('Offstream Group'), sg.Combo(tab_names, default_value=tab_names[0], key='dropdown2')],
         [sg.Submit(button_text='Start', key='Start'), sg.Submit(button_text='Stop', key='Stop')],
         [sg.Text('Head to Head Generator')],
         [sg.Text('Player A'), sg.Combo([], size=(10, 1), key='playera_dropdown'),
          sg.Text('Player B'), sg.Combo([], size=(10,1), key='playerb_dropdown')],
         [sg.Submit(button_text='Generate Head to Head', key='H2HGen')],
         ]


layout = [
            [sg.Column(col_1)]
]

if __name__ == '__main__':
    window = sg.Window(title='KoB Toolsuite', layout=layout, margins=(50, 50))

    has_clicked = False
    while True:
        event, values = window.read(timeout=500)
        if event == sg.WIN_CLOSED:
            break
        if event == 'Stop':
            window[event].Update(button_color='black')
            window['Start'].Update(button_color='dark blue')
            has_clicked = False

        if event == 'Start':
            [player_a_names, player_b_names] = build_ticker.build_kob_ticker(values['dropdown1'], values['dropdown2'])

            window['playera_dropdown'].update(player_a_names[0], values=player_a_names)
            window['playerb_dropdown'].update(player_b_names[0], values=player_b_names)
            has_clicked = True

        if event == 'H2HGen':
            build_ticker.generate_head_to_head_graphics(values['playera_dropdown'], values['playerb_dropdown'])


    window.close()

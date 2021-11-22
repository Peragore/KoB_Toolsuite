import time

import build_ticker
import threading
import PySimpleGUI as sg
from os import path
from threading import Thread
from collections import deque
[tab_names, player_names] = build_ticker.get_tab_names()
tab_names.insert(0, '')

col_1 = [[sg.Checkbox('Playoffs', default=False, key='playoffs')],
         [sg.Text('AlphaX Group'), sg.Combo(tab_names, default_value=tab_names[1], key='dropdown1'),
          sg.Text('SDC Group'), sg.Combo(tab_names, default_value=tab_names[2], key='dropdown2')],
         [sg.Submit(button_text='Start', key='Start'), sg.Submit(button_text='Stop', key='Stop')],
         [sg.Text('Head to Head Generator')],
         [sg.Text('Player A'), sg.Combo(player_names, default_value= player_names[0],
                                        size=(10, 1), key='playera_dropdown'),
          sg.Text('Player B'), sg.Combo(player_names, default_value=player_names[0],
                                        size=(10,1), key='playerb_dropdown')],
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
        if has_clicked:
            if not values['playoffs']:
                if not results_thread.is_alive():
                    try:
                        results_thread = Thread(target=build_ticker.build_kob_ticker,
                                                kwargs={'mainstream_tab': values['dropdown1'],
                                                        'offstream_tab': values['dropdown2'],
                                                        'threaded': True},
                                                daemon=True)
                        results_thread.start()
                    except:
                        print('API calls exceeded')
            if values['playoffs']:
                if not bracket_thread.is_alive():
                    try:
                        bracket_thread = Thread(target=build_ticker.build_playoff_bracket, kwargs={'threaded': True},
                                                daemon=True)
                        bracket_thread.start()
                    except:
                        print('Api Calls exceeded')
        if event == 'Start':
            try:
                window['playera_dropdown'].update(player_names[0], values=player_names)
                window['playerb_dropdown'].update(player_names[0], values=player_names)

                results_thread = Thread(target=build_ticker.build_kob_ticker,
                                        kwargs={'mainstream_tab': values['dropdown1'], 'offstream_tab': values['dropdown2'],
                                                'threaded': True, 'playoffs': values['playoffs']},
                                        daemon=True)
                results_thread.start()

                if values['playoffs']:
                    bracket_thread = Thread(target=build_ticker.build_playoff_bracket, kwargs={'threaded': True},
                                            daemon=True)

                    bracket_thread.start()
                window[event].Update(button_color='black')
                window['Stop'].Update(button_color='dark blue')
            except:
                print('Must Select Both Groups')
            has_clicked = True

        if event == 'H2HGen':
            build_ticker.generate_head_to_head_graphics(values['playera_dropdown'], values['playerb_dropdown'])


    window.close()

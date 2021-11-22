import time
import urllib.parse

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from PIL import Image, ImageDraw, ImageFont
import requests
from os import path
from shutil import copyfile

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1TX2a7CHmrJaaNvytF_iVUGPAD9ALnRhIJXrVjJelTDk'
GROUP_NAMES = {'Group A': 'Group Kashim', 'Group B': 'Group DARKING',
               'Group C': 'Group hjpα', 'Group D': 'Group CynicalDeath'}
player_info = []

creds = None

old_group_data = []
old_ax_intermission = []
old_sdc_intermission = []
old_useful_lines = []

if os.path.exists('creds/token.pickle'):
    with open('creds/token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'creds/credentials.json', SCOPES)  # here enter the name of your downloaded JSON file
        creds = flow.run_local_server(port=8080)
    with open('creds/token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()

def get_tab_names():

    result_input = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = result_input['sheets']
    sheet_names = [x['properties']['title'] for x in sheets]

    global player_info
    player_info = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                     range='Player Info' + '!A2:E17').execute()
    player_values = player_info['values']
    player_values = [x[0] for x in player_values]

    return [[x for x in sheet_names if 'Group' in x and '-' not in x], player_values]


def build_kob_ticker(mainstream_tab='', offstream_tab='', threaded=False, playoffs=False):
    if threaded:
        time.sleep(2)

    if not playoffs:
        mainstream_group = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                              range=mainstream_tab+'!B6:E18').execute()
        mainstream_values = mainstream_group['values']
        mainstream_values = [x[0:-1] for x in mainstream_values if x != []]
        time.sleep(0.5)
        offstream_group = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=offstream_tab+'!B6:E18').execute()
        offstream_values = offstream_group['values']
        offstream_values = [x[0:-1] for x in offstream_values if x != []]

        time.sleep(0.5)

        group_names = [GROUP_NAMES[mainstream_tab], GROUP_NAMES[offstream_tab]]
        group_data = [mainstream_values[0:4], offstream_values[0:4]]
        global old_group_data
        if group_data != old_group_data:
            print('Remaking Results')
            generate_group_standings_img(group_names, group_data)

        mainstream_verbose_tab = mainstream_tab+' - Vetoes'
        verbose_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                             range=mainstream_verbose_tab).execute()
        verbose_data = verbose_sheet['values']
        cleaned_data = [x for x in verbose_data if x != []]
        cleaned_data = cleaned_data[2:len(cleaned_data)]
        p1 = []
        p2 = []
        p1_score = []
        p2_score = []
        for row in cleaned_data:
            if 'MAP 1' in row:
                p1.append(row[2])
                p2.append(row[4])
                p1_score.append(row[13])
                p2_score.append(row[14])
        global old_ax_intermission
        if [p1, p2, p1_score, p2_score] != old_ax_intermission:
            generate_intermission_img(p1, p2, p1_score, p2_score, 'alphax')
        time.sleep(0.5)
        old_ax_intermission = [p1, p2, p1_score, p2_score]

        offstream_verbose_tab = offstream_tab + ' - Vetoes'
        verbose_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                           range=offstream_verbose_tab).execute()
        verbose_data = verbose_sheet['values']
        cleaned_data = [x for x in verbose_data if x != []]
        cleaned_data = cleaned_data[2:len(cleaned_data)]
        p1 = []
        p2 = []
        p1_score = []
        p2_score = []
        for row in cleaned_data:
            if 'MAP 1' in row:
                p1.append(row[2])
                p2.append(row[4])
                p1_score.append(row[13])
                p2_score.append(row[14])
        global  old_sdc_intermission
        if old_sdc_intermission != [p1, p2, p1_score, p2_score]:
            generate_intermission_img(p1, p2, p1_score, p2_score, 'sdc')
        old_sdc_intermission = [p1, p2, p1_score, p2_score]
        # global old_group_data
        old_group_data = group_data


def generate_intermission_img(p1_list, p2_list, p1_score_list, p2_score_list, streamname):
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    fnt = ImageFont.truetype('fonts/MYRIADPRO-BOLDCOND.OTF', size=40)
    d = ImageDraw.Draw(img)
    start_y = 500
    counter = 0
    for p1 in p1_list:
        if p1 == '':
            p1 = 'TBD'
        if p2_list[counter] == '':
            p2_list[counter] = 'TBD'
        if counter % 2 == 0 and counter != 0:
            start_y += 195
        if counter % 2 != 0 and counter != 5:
            start_x = 453
        elif counter == 4:
            start_x = 290
        else:
            start_x = 120
        d.text((start_x, start_y), p1_score_list[counter], font=fnt, fill='#fde4a9')
        d.text((start_x + 50, start_y), p1, font=fnt, fill='#fde4a9')
        d.text((start_x, start_y+55), p2_score_list[counter], font=fnt, fill='#fde4a9')
        d.text((start_x + 50, start_y+55), p2_list[counter], font=fnt, fill='#fde4a9')
        counter += 1
    img.save('Broadcast Images/building folder/' + streamname + '_intermission_results.png')
    time.sleep(1)
    copyfile('Broadcast Images/building folder/' + streamname + '_intermission_results.png',
             'Broadcast Images/' + streamname + '_intermission_results.png')


def generate_group_standings_img(group_names, group_data):
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    img2 = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    fnt = ImageFont.truetype('fonts/MYRIADPRO-BOLDCOND.OTF', size=30)
    d = ImageDraw.Draw(img)
    d2 = ImageDraw.Draw(img2)

    flyin_start = 225
    name_start = 75
    match_start = 240
    counter = 0.
    d.text((40, 190), group_names[0], font=fnt, fill='#ff2d54')
    for result in group_data[0]:
        inner_counter = 0
        for data in result:
            if inner_counter > 0:
                d.text((match_start-15+inner_counter*80, flyin_start +5+ counter * 44), data, font=fnt,
                       fill=(253, 228, 169), anchor='mt')
            else:
                d.text((name_start, flyin_start+counter*45), data, font=fnt, fill=(253, 228, 169))
            inner_counter += 1
        counter += 1
    img.save('Broadcast Images/building folder/alphax_results_flyin.png')
    time.sleep(1)
    copyfile('Broadcast Images/building folder/alphax_results_flyin.png', 'Broadcast Images/alphax_results_flyin.png')
    flyin_start = 455
    counter = 0
    d2.text((40, 420), group_names[1], font=fnt, fill='#ff2d54')
    for result in group_data[1]:
        inner_counter = 0
        for data in result:
            if inner_counter > 0:
                d2.text((match_start-15+inner_counter*80, flyin_start +5+ counter * 44), data, font=fnt,
                       fill=(253, 228, 169), anchor='mt')
            else:
                d2.text((name_start, flyin_start+counter*45), data, font=fnt, fill=(253, 228, 169))
            inner_counter += 1
        counter += 1
    img2.save('Broadcast Images/building folder/sdc_results_flyin.png')
    time.sleep(1)
    copyfile('Broadcast Images/building folder/sdc_results_flyin.png', 'Broadcast Images/sdc_results_flyin.png')

def generate_head_to_head_graphics(player1, player2):

    swap_flag = False
    if path.exists('PlayerImages/'+str(player1)+'_right.png') and path.exists('PlayerImages/'+str(player2)+'_left.png'):
        swap_flag = True

    player_values = player_info['values']
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    player1_info = [x for x in player_values if player1.upper() in map(str.upper, x)]
    player2_info = [x for x in player_values if player2.upper() in map(str.upper, x)]

    if swap_flag:
        temp_player = player2
        player2=player1
        player1 = temp_player

        temp_info = player2_info
        player2_info = player1_info
        player1_info = temp_info

    header1_fontsize = 70
    header1_fnt = ImageFont.truetype('fonts/BUNKEN TECH SANS SC WIDE W01BD.TTF', size=header1_fontsize)
    while (header1_fnt.getsize(player1 + ' vs ' + player2)[0] > 820):
        header1_fontsize -= 1
        header1_fnt = ImageFont.truetype('fonts/BUNKEN TECH SANS SC WIDE W01BD.TTF', size=header1_fontsize)

    player_fnt = ImageFont.truetype('fonts/MYRIADPRO-BOLDCOND.OTF', size=40)
    d = ImageDraw.Draw(img)
    header_color = (253, 228, 169)
    player_color = (238, 230, 212)
    d.text((960, 150), player1 + ' vs ' + player2, font=header1_fnt, fill=header_color, anchor='mt')
    left_start = 850
    right_start = 1050
    counter = 0
    anchor_r = 'rt'
    anchor_l = 'lt'
    [player1_wins, player2_wins, p1_form, p2_form] = get_aligulac_data(player1, player2)
    for p1_info in player1_info[0][1:]:
        if counter == 2:
            player_fnt = ImageFont.truetype('fonts/MYRIADPRO-BOLDCOND.OTF', size=30)
        else:
            player_fnt = ImageFont.truetype('fonts/MYRIADPRO-BOLDCOND.OTF', size=40)
        d.text((left_start, 605 + counter*60), p1_info, font=player_fnt,
               fill=player_color, anchor=anchor_r)
        d.text((right_start, 605 + counter*60), player2_info[0][counter+1], font=player_fnt,
               fill=player_color, anchor=anchor_l)
        counter += 1

    d.text((left_start-40, 840), p1_form, font=player_fnt,
           fill=player_color, anchor=anchor_r)
    d.text((right_start+40, 840), p2_form, font=player_fnt,
           fill=player_color, anchor=anchor_l)
    d.text((left_start-40, 900), player1_wins+'-'+player2_wins, font=player_fnt,
           fill=player_color, anchor=anchor_r)
    d.text((right_start+40, 900), player2_wins+'-'+player1_wins, font=player_fnt,
           fill=player_color, anchor=anchor_l)

    try:
        player_left = Image.open('PlayerImages/'+player1+'_left.png')
    except:
        player_left = Image.open('PlayerImages/'+player1+'_right.png')
    try:
        player_right = Image.open('PlayerImages/'+player2+'_right.png')
    except:
        player_right = Image.open('PlayerImages/' + player2 + '_left.png')
    img.paste(player_left, (-50,0), player_left)
    img.paste(player_right, (1310, 0), player_right)
    img.save('Broadcast Images/building folder/head_to_head.png')
    time.sleep(1)
    copyfile('Broadcast Images/building folder/head_to_head.png', 'Broadcast Images/head_to_head.png')


def get_aligulac_data(player_1, player_2):
    params_h2h = {'apikey': 'tqYfLrmkYGPG4CZVjCvO'}
    api_h2h_url = 'http://aligulac.com/api/v1/match/'
    api_id_url = 'http://aligulac.com/search/json/'
    params_id1 = {'q': player_1}
    params_id2 = {'q': player_2}
    id1_json = requests.get(api_id_url, params_id1).json()['players']
    id2_json = requests.get(api_id_url, params_id2).json()['players']
    id1_data = [x['id'] for x in id1_json if x['tag'].casefold() == player_1.casefold()][0]
    id2_data = [x['id'] for x in id2_json if x['tag'].casefold() == player_2.casefold()][0]

    params_h2h['pla__in'] = str(id1_data)+','+str(id2_data)
    params_h2h['plb__in'] = str(id1_data) + ',' + str(id2_data)
    params_h2h['limit'] = '100'
    params_str = urllib.parse.urlencode(params_h2h, safe=',')
    h2h_data = requests.get(api_h2h_url, params=params_str).json()
    player1_wins = 0
    player2_wins = 0
    for result in h2h_data['objects']:
        if result['game'].casefold() == 'lotv':
            if int(result['sca']) > int(result['scb']):
                if result['pla']['tag'].casefold() == player_1.casefold():
                    player1_wins += 1
                else:
                    player2_wins += 1
            elif int(result['sca']) < int(result['scb']):
                if result['plb']['tag'].casefold() == player_2.casefold():
                    player2_wins += 1
                else:
                    player1_wins += 1

    params_form = {'apikey': 'tqYfLrmkYGPG4CZVjCvO'}
    api_form_url = 'http://aligulac.com/api/v1/player/set/'+str(id1_data)+';'+str(id2_data)+'/'
    form_data = requests.get(api_form_url, params_form).json()

    p1_form = form_data['objects'][0]['form'][form_data['objects'][1]['race']]
    p2_form = form_data['objects'][1]['form'][form_data['objects'][0]['race']]

    p1_form = p1_form[0]/(p1_form[1]+p1_form[0])*100
    p2_form = p2_form[0]/(p2_form[1]+p2_form[0])*100

    p1_form = '{:.2f}%'.format(p1_form)
    p2_form = '{:.2f}%'.format(p2_form)
    return [str(player1_wins), str(player2_wins), p1_form, p2_form]


def build_playoff_bracket(threaded=False):
    start_time = time.time()

    if threaded:
        time.sleep(2)
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    fnt = ImageFont.truetype('fonts/MYRIADPRO-BOLDCOND.OTF', size=40)
    d = ImageDraw.Draw(img)
    header_color = (253, 228, 169)

    quarterfinals = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                       range='Quarterfinals - Vetoes!C8:O36').execute()
    time.sleep(1)
    useful_lines = [x for x in quarterfinals['values'] if len(x) == 13 and 'RED ' not in x]
    global old_useful_lines
    if old_useful_lines != useful_lines:
        loop_counter = 0
        counter = 0
        quarterfinals_left = 335
        quarterfinals_top = 185
        for match in useful_lines:
            if loop_counter == 2:
                quarterfinals_top = 670
                counter = 0

            if loop_counter == 3:
                counter=0
                quarterfinals_top = 855
            player1 = match[0]
            player2 = match[2]
            if player1 == '':
                player1 = 'TBD'
            if player2 == '':
                player2 = 'TBD'
            score_1 = match[-2]
            score_2 = match[-1]
            d.text((quarterfinals_left, quarterfinals_top+180*counter), score_1, font=fnt,
                   fill=header_color, anchor='mm')
            d.text((quarterfinals_left, quarterfinals_top+55+180*counter), score_2, font=fnt,
                   fill=header_color, anchor='mm')
            d.text((quarterfinals_left+60, quarterfinals_top+180*counter), player1, font=fnt,
                   fill=header_color, anchor='lm')
            d.text((quarterfinals_left+60, quarterfinals_top+55+180*counter), player2, font=fnt,
                   fill=header_color, anchor='lm')
            loop_counter += 1
            counter += 1

            semis_finals = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                              range='Semifinals + Finals!C8:O36').execute()
            time.sleep(0.5)
            useful_lines = [x for x in semis_finals['values'] if len(x) == 13 and 'RED ' not in x]
            player1 = []
            player2 = []
            score_1 = []
            score_2 = []

            for match in useful_lines:
                player1.append(match[0])
                player2.append(match[2])

                score_1.append(match[-2])
                score_2.append(match[-1])
            d.text((845, 275), score_1[0], font=fnt,
                   fill=header_color, anchor='mm')
            d.text((845, 330), score_2[0], font=fnt,
                   fill=header_color, anchor='mm')
            d.text((910, 275), player1[0], font=fnt,
                   fill=header_color, anchor='lm')
            d.text((910, 330), player2[0], font=fnt,
                   fill=header_color, anchor='lm')

            d.text((845, 765), score_1[1], font=fnt,
                   fill=header_color, anchor='mm')
            d.text((845, 820), score_2[1], font=fnt,
                   fill=header_color, anchor='mm')
            d.text((910, 765), player1[1], font=fnt,
                   fill=header_color, anchor='lm')
            d.text((910, 820), player2[1], font=fnt,
                   fill=header_color, anchor='lm')

            d.text((1360, 520), score_1[2], font=fnt,
                   fill=header_color, anchor='mm')
            d.text((1360, 575), score_2[2], font=fnt,
                   fill=header_color, anchor='mm')
            d.text((1420, 520), player1[2], font=fnt,
                   fill=header_color, anchor='lm')
            d.text((1420, 575), player2[2], font=fnt,
                   fill=header_color, anchor='lm')

        img.save('Broadcast Images/building folder/bracket.png')
        time.sleep(1)
        copyfile('Broadcast Images/building folder/bracket.png', 'Broadcast Images/bracket.png')
    old_useful_lines = useful_lines

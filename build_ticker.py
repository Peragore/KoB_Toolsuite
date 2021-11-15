from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from PIL import Image, ImageDraw, ImageFont


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1TX2a7CHmrJaaNvytF_iVUGPAD9ALnRhIJXrVjJelTDk'
GROUP_NAMES = {'Group A':'Group CynicalDeath', 'Group B': 'Group DARKING',
               'Group C': 'Group hjpα', 'Group D': 'Group Kashim', '':''}

def get_tab_names():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    values_input = result_input.get('values', [])
    sheets = result_input.get('sheets', '')
    sheet_names = [x.get("properties", {}).get("title") for x in sheets]
    return sheet_names[1:len(sheet_names)]

def build_kob_ticker(mainstream_tab = '', offstream_tab = ''):
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    mainstream_group = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                          range=mainstream_tab+'!B6:D9').execute()
    mainstream_values = mainstream_group.get('values', [])

    offstream_group = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                         range=offstream_tab+'!B6:D9').execute()
    offstream_values = offstream_group.get('values', [])
    player_a = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                          range=mainstream_tab+'!B14:B18').execute()
    player_a_values = player_a.get('values', [])
    player_a_values = [x for y in player_a_values for x in y]
    player_b = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                          range=mainstream_tab+'!E14:E18').execute()
    player_b_values = player_b.get('values', [])
    player_b_values = [x for y in player_b_values for x in y]

    group_names = [GROUP_NAMES[mainstream_tab], GROUP_NAMES[offstream_tab]]
    group_data = [mainstream_values, offstream_values]
    generate_group_standings_img(group_names, group_data)

    mainstream_verbose_tab = mainstream_tab+' - Vetoes'
    verbose_sheet = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                         range=mainstream_verbose_tab).execute()
    verbose_data = verbose_sheet.get('values', [])
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
    generate_intermission_img(p1, p2, p1_score, p2_score)

    return [player_a_values, player_b_values]
    print('test')


def generate_intermission_img(p1_list, p2_list, p1_score_list, p2_score_list):
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    fnt = ImageFont.truetype('MYRIADPRO-BOLDCOND.OTF', size=40)
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
    img.save('intermission_results.png')

def generate_group_standings_img(group_names, group_data):
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    img2 = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    fnt = ImageFont.truetype('MYRIADPRO-BOLDCOND.OTF', size=30)
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
    img.save('mainstream_flyin.png')

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
    img2.save('offstream_flyin.png')

def generate_head_to_head_graphics(player1, player2):
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    player_info = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                          range='Player Info'+'!A2:E17').execute()
    player_values = player_info.get('values', [])
    img = Image.new('RGBA', (1920, 1080), color=(0, 0, 0, 0))
    player1_info = [x for x in player_values if player1.upper() in map(str.upper, x)]
    player2_info = [x for x in player_values if player2.upper() in map(str.upper, x)]
    header1_fontsize = 70
    header1_fnt = ImageFont.truetype('BUNKEN TECH SANS SC WIDE W01BD.TTF', size=header1_fontsize)
    while (header1_fnt.getsize(player1 + ' vs ' + player2)[0] > 820):
        header1_fontsize -= 1
        header1_fnt = ImageFont.truetype('BUNKEN TECH SANS SC WIDE W01BD.TTF', size=header1_fontsize)

    player_fnt = ImageFont.truetype('MYRIADPRO-BOLDCOND.OTF', size=40)
    d = ImageDraw.Draw(img)
    header_color = (253, 228, 169)
    player_color = (238, 230, 212)
    d.text((960, 150), player1 + ' vs ' + player2, font=header1_fnt, fill=header_color, anchor='mt')
    left_start = 850
    right_start = 1050
    counter = 0
    for p1_info in player1_info[0][1:]:
        if counter == 2:
            player_fnt = ImageFont.truetype('MYRIADPRO-BOLDCOND.OTF', size=30)
        else:
            player_fnt = ImageFont.truetype('MYRIADPRO-BOLDCOND.OTF', size=40)
        d.text((left_start, 605 + counter*60), p1_info, font=player_fnt, fill=player_color, anchor='rt')
        d.text((right_start, 605 + counter*60), player2_info[0][counter+1], font=player_fnt, fill=player_color, anchor='lt')
        counter += 1
    player_left = Image.open('PlayerImages/'+player1+'.png')
    player_right = Image.open('PlayerImages/'+player2+'.png')
    img.paste(player_left)
    img.paste(player_right, (1310, 0))
    img.save('head_to_head.png')


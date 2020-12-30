from __future__ import print_function
import calendar
import os.path
import pickle
from creds import *
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle. https://developers.google.com/sheets/api/guides/authorizing
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SheetTransformer:
    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds).spreadsheets()
        print('Sheet Transformer built successfully using token.pickle')

    def lookup(self, spread_id, name=None, sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        n_rows = sheet.get('properties').get('gridProperties').get('rowCount') if name else HEADER_ROWS
        n_cols = sheet.get('properties').get('gridProperties').get('columnCount')
        title = sheet.get('properties').get('title')
        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A1:{self.column_to_letter(n_cols)}{n_rows}').execute()
        values = result.get('values', [])
        if not values:
            raise Exception('Error, no values found.')

        member_row = None
        if name:
            for r in values:
                if r[0].upper().strip() == name.upper().strip():
                    member_row = r
                    break
            if member_row == None:
                raise Exception(f'Error, project member {name} not found.')

        summary = ''
        for i, project in enumerate(values[0]):
            if project == '':
                continue
            member_status = ''
            if member_row:
                member_status = ': ❌' if i >= len(member_row) or member_row[i] == '' else f': {member_row[i].strip()}'
                if member_status == ': x':
                    member_status = ': ✅'

            summary = summary + f'{project} (due {values[1][i]}){member_status}\n'
        return summary

    def checkoff(self, spread_id, assignment, name, val='y', sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        n_rows = sheet.get('properties').get('gridProperties').get('rowCount')
        n_cols = sheet.get('properties').get('gridProperties').get('columnCount')
        title = sheet.get('properties').get('title')
        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A1:{self.column_to_letter(n_cols)}{n_rows}').execute()
        values = result.get('values', [])
        if not values:
            raise Exception('Error, no values found.')

        old_val = ''
        member_row = None
        for row, r in enumerate(values):
            if r[0].upper().strip() == name.upper().strip():
                member_row = row + 1
        if member_row == None:
            raise Exception(f'Error, project member **{name}** not found.')

        assignment_col = None
        for col, a in enumerate(values[0]):
            if a.upper().strip() == assignment.upper().strip():
                if col < len(values[member_row - 1]):
                    old_val = values[member_row - 1][col]
                assignment_col = self.column_to_letter(col + 1)
                break
        if assignment_col == None:
            raise Exception(f'Error, assignment **{assignment}** not found.')

        self.service.values().update(spreadsheetId=spread_id,
                                     valueInputOption='RAW',
                                     range=f'{title}!{assignment_col}{member_row}:{assignment_col}{member_row}',
                                     body={
                                         'range': f'{title}!{assignment_col}{member_row}:{assignment_col}{member_row}',
                                         'values': [[val]],
                                     }).execute()
        return old_val

    #todo: add fancy formatting (percents, colors, dates, etc.)
    def add_assignment(self, spread_id, assignment, deadline, sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        sheet_id = sheet.get('properties').get('sheetId')
        title = sheet.get('properties').get('title')

        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A1:1').execute()
        assignments = result.get('values')
        new_col_index = len(assignments[0]) if assignments else PROJECT_COL_INDEX
        new_col = self.column_to_letter(new_col_index + 1)

        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A:A').execute()
        members = result.get('values')
        n_members = len(members) - HEADER_ROWS if members else 0
        percent= f'=({n_members}-COUNTBLANK({new_col}{HEADER_ROWS+1}:{new_col}{HEADER_ROWS+n_members}))/{n_members}'

        self.service.values().clear(spreadsheetId=spread_id, range=f'{title}!{new_col}:{new_col}').execute()
        self.service.values().update(spreadsheetId=spread_id,
                                     valueInputOption='USER_ENTERED',
                                     range=f'{title}!{new_col}:{new_col}',
                                     body={
                                         'range': f'{title}!{new_col}:{new_col}',
                                         'values': [[assignment, deadline, percent]],
                                         'majorDimension': 'COLUMNS',
                                     }).execute()

        # Add pretty formatting (colors/number formatting)
        percent_range = {
            'sheetId': sheet_id,
            'startRowIndex': PERCENT_ROW_INDEX,
            'endRowIndex': PERCENT_ROW_INDEX + 1,
            'startColumnIndex': new_col_index,
            'endColumnIndex': new_col_index + 1,
        }
        checkoff_range = {
            'sheetId': sheet_id,
            'startRowIndex': HEADER_ROWS,
            'endRowIndex': HEADER_ROWS + n_members,
            'startColumnIndex': new_col_index,
            'endColumnIndex': new_col_index + 1,
        }
        requests = [{
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [percent_range],
                    'gradientRule': {
                        'minpoint': {
                            'color': {'red': 0.96, 'green': 0.8, 'blue': 0.8},
                            'type': 'NUMBER',
                            'value': '0'
                        },
                        'midpoint': {
                            'color': {'red': 1.0, 'green': 0.9, 'blue': 0.6},
                            'type': 'NUMBER',
                            'value': '0.5'
                        },
                        'maxpoint': {
                            'color': {'red': 0.72, 'green': 0.88, 'blue': 0.8},
                            'type': 'NUMBER',
                            'value': '1.0'
                        }
                    }
                },
                'index': 0
            }
        }, {
            'repeatCell': {
                'range': percent_range,
                'cell': {
                  'userEnteredFormat': {
                    'numberFormat': {
                      'type': 'PERCENT',
                      'pattern': '#0%'
                    }
                  }
                },
                'fields': 'userEnteredFormat.numberFormat'
              }
        }, {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [checkoff_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'BLANK',
                        },
                        'format': {
                            'backgroundColor': {'red': 0.96, 'green': 0.8, 'blue': 0.8}
                        }
                    }
                },
                'index': 1
            }
        }]
        body = {
            'requests': requests
        }
        response = self.service.batchUpdate(spreadsheetId=spread_id, body=body).execute()
        return

    def change_deadline(self, spread_id, assignment, deadline, sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        title = sheet.get('properties').get('title')

        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A1:{HEADER_ROWS}').execute()
        header = result.get('values')

        old_deadline = ''
        assignment_col = None
        for col, a in enumerate(header[0]):
            if a.upper().strip() == assignment.upper().strip():
                if DATE_ROW_INDEX < len(header) and col < len(header[DATE_ROW_INDEX]):
                    old_deadline = header[DATE_ROW_INDEX][col]
                assignment_col = self.column_to_letter(col + 1)
                break
        if assignment_col == None:
            raise Exception(f'Error, assignment **{assignment}** not found.')

        date_row = DATE_ROW_INDEX + 1
        self.service.values().update(spreadsheetId=spread_id,
                                     valueInputOption='USER_ENTERED',
                                     range=f'{title}!{assignment_col}{date_row}:{assignment_col}{date_row}',
                                     body={
                                         'range': f'{title}!{assignment_col}{date_row}:{assignment_col}{date_row}',
                                         'values': [[deadline]],
                                     }).execute()
        return old_deadline

    def get_lab_hours_by_name(self, spread_id, name, sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        title = sheet.get('properties').get('title')

        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}').execute()
        values = result.get('values')

        hours = []
        col = FIRST_LH_COL_INDEX + 1
        while col < len(values[FIRST_LH_ROW_INDEX]):
            day = values[FIRST_LH_ROW_INDEX][col]
            times = []
            row = FIRST_LH_ROW_INDEX + 1
            while row < len(values):
                time = values[row][FIRST_LH_COL_INDEX]
                if name.upper().strip() in values[row][col].upper().strip():
                    times.append(time)
                row = row + 1
            if times:
                hours.append(f'{day}: {times[0] if len(times) == 1 else ", ".join(times)}')
            col = col + 1
        return hours

    def get_lab_hours_by_time(self, spread_id, time, sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        title = sheet.get('properties').get('title')

        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}').execute()
        values = result.get('values')

        h = time.hour if time.hour < 12 else time.hour % 12
        if h == 0:
            h = 12
        hour = f'{h}am' if time.hour < 12 else f'{h}pm'
        day_of_week = calendar.day_name[time.weekday()]

        shift_str = ''
        col = None
        for c, day in enumerate(values[FIRST_LH_ROW_INDEX]):
            if day_of_week in day:
                col = c
                break
        row = None
        for r, shift in enumerate(values):
            if shift and shift[FIRST_LH_COL_INDEX].startswith(hour):
                row = r
                shift_str = f'{day_of_week} {shift[FIRST_LH_COL_INDEX].strip()}'
                break
        if not col or not row or col >= len(values[row]):
            raise Exception("No lab hours found for the current time.")
        else:
            return shift_str, values[row][col]

    # helper function to convert numerical column to letter column (Google Sheets format)
    def column_to_letter(self, column):
        temp = 0
        letter = ''
        while column > 0:
            temp = (column - 1) % 26
            letter = chr(int(temp) + 65) + letter
            column = (column - temp - 1) / 26
        return letter
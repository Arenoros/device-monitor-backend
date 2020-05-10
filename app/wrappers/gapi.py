import gspread
import pprint
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient.discovery

class GoogleApi:
    def __init__(self, cred_file, scopes):
        self.cred = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scopes)
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scopes)
        httpAuth = creds.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)
        self.service = responce = service.spreadsheets().values()

    def readTable(self, table, range, dimension = 'ROWS'):
        return self.service.get(
            spreadsheetId = table,
            range=range,
            majorDimension=dimension
        ).execute()

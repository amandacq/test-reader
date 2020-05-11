import os
from google.oauth2 import service_account
from apiclient import discovery


class SheetsPublisher:
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def publish(self, values):
        app_name = os.environ.get("APP_NAME")
        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("CREDENTIALS_PATH"), scopes=self.SCOPES)

        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = os.environ.get("SPREADSHEET_ID")
        last_column = chr(64 + len(values[0]))
        batch_update_values_request_body = {
            'value_input_option': 'RAW',
            'data': [{
                'majorDimension': "ROWS",
                'range': f"{app_name}!A1:{last_column}{len(values) + 1}",
                'values': values
            }]
        }

        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

        sheet_exists = self.__sheet_exists(app_name, sheet_metadata)
        self.__create_sheet(app_name, service, sheet_exists, spreadsheet_id)
        request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                              body=batch_update_values_request_body)
        request.execute()

    @staticmethod
    def __create_sheet(app_name, service, sheet_exists, spreadsheet_id):
        if not sheet_exists:
            request_create = {
                'requests': [
                    {
                        'addSheet': {
                            'properties': {
                                'title': app_name
                            }
                        }
                    }
                ]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_create).execute()

    @staticmethod
    def __sheet_exists(app_name, sheet_metadata):
        sheet_exists = False
        sheets = sheet_metadata.get('sheets', '')
        for sheet in sheets:
            if sheet['properties']['title'] == app_name:
                sheet_exists = True
                break
        return sheet_exists

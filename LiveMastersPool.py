import requests
from bs4 import BeautifulSoup
import pandas as pd
from dataclasses import dataclass
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

@dataclass
class LiveMastersPool:
    input: pd.DataFrame
    google_drive_key_file: str
        
    def get_espn_live_updates(self) -> dict:
        
        headers = requests.utils.default_headers()
        headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        })
        page = requests.get('https://www.espn.com/golf/leaderboard', headers=headers)

        soup = BeautifulSoup(page.text, 'html.parser')
        data = []
        rows = soup.find_all(class_ = 'Table__TR')
        for row in rows:
            cols = row.find_all(class_ = 'Table__TD')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
            
        scores = {}
        thru = {}
        for player in data:
            if len(player) > 5:
                if player[3] == "E":
                    score = 0
                elif player[3] == "CUT":
                    score = 100
                elif player[3].startswith("+"):
                    score = int(player[3].strip("+"))
                else:
                    score = int(player[3])
                thru[player[2].lower()] = player[5]
                scores[player[2].lower()] = score
        return scores, thru 
    
    def report_scores(self, input: pd.DataFrame) -> pd.DataFrame:    
        groups = ["A", "B", "C1", "C2", "D1", "D2", "E"]
        scores, thru = self.get_espn_live_updates()
        for golf_group in groups:
            input[f"SCORE {golf_group}"] = input[f"GOLFER {golf_group}"].str.lower().map(scores)
            input[f"THRU {golf_group}"] = input[f"GOLFER {golf_group}"].str.lower().map(thru)
        return input
    
    def get_scoreboard(self):
        results = self.report_scores(self.input)
        for i in range(1,8):
            results[f"{i}"] = results[["SCORE A", "SCORE B", "SCORE C1", "SCORE C2", "SCORE D1", "SCORE D2", "SCORE E"]].apply(lambda row: row.nsmallest(i).iat[-1], axis=1)

        results["SCORE"] = results["1"] + results["2"] + results["3"] + results["4"] + results["5"]
        results = results.sort_values(by=["SCORE", "1" , "2", "3", "4", "5", "6", "7"])
        results["RANK"] = results["SCORE"].rank(method="first")
        output = results.sort_values(by=["RANK"])
        return output

    def get_google_client(self):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.google_drive_key_file, scope)
        client = gspread.authorize(creds)
        return client
    
    def update_google_sheets(self):
        print(f"Updating google sheets at {datetime.now()}")
        client = self.get_google_client()
        sh = client.open("Live Masters")
        df = self.get_scoreboard()
        df['SCORE'] = df['SCORE'].apply(lambda x: x if int(x) < 50 else "CUT")
        df.replace({100: "CUT", 0: "E"}, inplace=True)
        df["RANK"] = df["RANK"].replace({"CUT": 100})
        cols = ['GOLFER A', 'SCORE A', 'THRU A', 'GOLFER B', 'SCORE B', 'THRU B', 'GOLFER C1', 'SCORE C1', 'THRU C1', 'GOLFER C2', 'SCORE C2', 'THRU C2', 'GOLFER D1', 'SCORE D1', 'THRU D1', 'GOLFER D2', 'SCORE D2', 'THRU D2', 'GOLFER E', 'SCORE E', 'THRU E'] 
        scoreboard = ["RANK", "ENTRANT", "SCORE", "1", "2", "3", "4", "5", "6", "7"] + cols
        df = df[scoreboard]
        master_wksh = sh.worksheet("Masters")
        master_wksh.update([df.columns.values.tolist()] + df.values.tolist())
        self.resize_sheet(sh)
        
    def resize_sheet(self, sh):
        sheetId = sh.worksheet("Masters")._properties['sheetId']
        body = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheetId,
                            "dimension": "COLUMNS",
                            "startIndex": 0,  # Please set the column index.
                            "endIndex": 27  # Please set the column index.
                        }
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": sheetId,
                        "dimension": "COLUMNS",
                        "startIndex": 4,
                        "endIndex": 11
                    },
                    "properties": {
                        "pixelSize": 50
                    },
                    "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                        "sheetId": sheetId,
                        "dimension": "COLUMNS",
                        "startIndex": 11,
                        "endIndex": 32
                    },
                    "properties": {
                        "pixelSize": 150
                    },
                    "fields": "pixelSize"
                    }
                }
            ]
        }
        sh.batch_update(body)
    
        
if __name__ == "__main__":
    input_df = pd.read_csv("teams.csv")
    google_drive_key_file = "/path/to/keyfile"
    pool = LiveMastersPool(input=input_df, google_drive_key_file=google_drive_key_file)
    pool.update_google_sheets()


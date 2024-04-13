### Liver Masters Pool Web Scraper

Pre-req:

1. Set up google sheets and drive apis:

[Example Guide](https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/)

Once set up download the google drive key file and replace line 135:

`    google_drive_key_file = "/path/to/keyfile"  `


Make sure to update sheet name and worksheet name in google sheets (line 74 and line 82)


2. Input csv (teams.csv) with following schema headers:

```
ENTRANT,GOLFER A,GOLFER B,GOLFER C1,GOLFER C2,GOLFER D1,GOLFER D2,GOLFER E
devine12,Scottie Scheffler,Will Zalatoris,Cameron Young,Max Homa,Nicolai Højgaard,Adrian Meronk,Thorbjørn Olesen
```


```
ENTRANT    :    Who submitted the master pool
GOLFER A   :    Group A Golfer
GOLFER B   :    Group B Golfer
GOLFER C1  :    Group C Golfer (pick 1)
GOLFER C2  :    Group C Golfer (pick 2)
GOLFER D1  :    Group D Golfer (pick 1)
GOLFER D2  :    Group D Golfer (pick 2)
GOLFER E   :    Group E Golfer
```






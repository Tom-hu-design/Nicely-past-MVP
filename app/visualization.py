import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine('sqlite:///app/userdata.sqlite3', echo=False)

def Calculate(RawScore):
    Output = -0.42*np.power(RawScore, 4)+0.49*np.power(RawScore, 3)+0.112*np.power(RawScore, 2)+0.8083
    return Output

def CalScore(row):
    CScoreRaw = row['Optimism']+row['Joy']-row['Anger']-row['Sadness']
    ScoreOut = np.round(float(Calculate(CScoreRaw)), 4)
    ScoreFinal = 100*ScoreOut
    return ScoreFinal

def process(data):
    process = []
    for e in data:
        rawscore = str(e)
        Newdf = rawscore.split(' ')
        process.append(float(Newdf[1]))
    return process

def processtext(raw):
    CScoreRaw = raw[1]+raw[2]-raw[0]-raw[3]
    ScoreOut = np.round(float(Calculate(CScoreRaw)), 4)
    ScoreFinal = 100*ScoreOut
    return ScoreFinal

def graphplot(dataframe):
    print("Data processing start...")
    df = dataframe

    Nlist = ["sentiment1", "sentiment2", "sentiment3", "sentiment4"]

    results = []

    for e in Nlist:
        Newdf = df[e].str.split(' ', expand=True)
        results.append(Newdf)

    timedata = []

    for item in dataframe["time"]:
        date = str(item)
        TimeStamp = date.split('+')
        timedata.append(TimeStamp)

    timeresult = pd.DataFrame(timedata)

    NameMap = pd.concat([(results[i][1])for i in range(4)], axis = 1)
    NameMap = NameMap.set_axis(['Anger', 'Joy', 'Optimism', 'Sadness'], axis='columns')

    Graphing = NameMap.astype(float)
    Graphing['AveDailyScore'] = Graphing.apply(CalScore, axis=1)
    PlotData = pd.concat([Graphing, timeresult[0]], axis=1, ignore_index=True)
    Database = pd.concat([dataframe[["user_name", "id", "text"]],PlotData], axis=1, ignore_index=True)
    Database = Database.set_axis(['user_name', 'Tweet_id', 'content', 'Anger', 'Joy', 'Optimism', 'Sadness', 'AveDailyScore', 'Tweet_time'],
    axis='columns')

    # Graphing = PlotData.astype(float)
    # Graphing.plot.barh(stacked=True)

    # Graphing.plot.area(stacked=False,figsize=(10, 5))

    # Graphing['AveDailyScore'] = round(Graphing.apply(CalScore, axis=1), 4)

    # fig = Graphing.plot(y="AveDailyScore", figsize=(10, 5))
    # fig.set_ylim([0, 100])

    # EmotionScore = Database['AveDailyScore'].mean()

    # Graphing.sort_values(by=['AveDailyScore'], ascending=True)
    # ranking the emotions score

    # resultsBelow = Database['AveDailyScore'][Database['AveDailyScore']<60].count()
    # plt.show()
    
    print("Done processing...")

    return Database.to_sql('user_tweets', engine, if_exists = "append", index = False)

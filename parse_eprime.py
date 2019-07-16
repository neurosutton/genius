# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import glob as glob
from itertools import dropwhile

def create_df_triangle:
    triParams = paradigm_params()
    triParams = 14
    triParams.cols = ['clipType','stimulus','RT','ACC']
    triParams.stimuli = ['Action','Random', 'ToM']
    triParams.recodeDict = {'Action':'friendly',
              'Random':'random',
              'ToM':'sneaky'}
    triParams.taskDir = r'/Users/bmohl/Documents/legget/asd_triangle'

return(df)

#set up the params

def analyze_behav(params): #enter the

for stim in stimuli:
    print(clip)
    with open(rawData[0], 'r', encoding='utf-16') as f:
        dropped = dropwhile(lambda ln: "Movie" not in ln, f) #To advance to the first trial
        f = list(dropped)
        for n in range(0,params.nAvgs):
            dropped = dropwhile(lambda ln: clip not in ln, f)
            f = list(dropped)
            stimulus = f[0].split() #list the generator object and then take the first element
            dropped = dropwhile(lambda ln: "TaskPrompt.ACC:" not in ln, f)
            f = list(dropped)
            acc = f[0].split()
            dropped = dropwhile(lambda ln: "TaskPrompt.RT:" not in ln, f)
            f = list(dropped)
            rt = f[0].split()
            newInfo = {'clipType':[recode.get(clip)],'stimulus':[stimulus[1]],
                    'RT' : [rt[1]], 'ACC': [acc[1]] }#get the value for the type of clip
            df = df.append(pd.DataFrame.from_dict(newInfo))
df = df[['clipType','stimulus','ACC','RT']]

df.to_csv(taskDir + "/data/" + subj + '_cleanBehav.csv')
print(df)

class paradigm_params:

    def __init__(self, task,nAvgs,cols, stimuli, recodeDict,taskDir):
    self.task = ""
    self.nAvgs = 100 #The number of repeated stimuli or blocks, default is 100 to have overkill
    self.cols = ""
    self.stimuli = ""
    self.recodeDict = {}
    self.taskDir = ""

    def find_subj(self):
        rawData = glob.glob(self.taskDir+"/data/*txt")
        subj = rawData[0].split('-')[1:2]
        subj =''.join(subj)
    return(subj,rawData)

    def make_df(self):
        df = pd.DataFrame(columns=self.cols)
    return(df)

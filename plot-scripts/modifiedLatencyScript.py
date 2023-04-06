# sample command to run this script: sudo python3 plot-scripts/modifiedLatencyScript.py --number-of-switches 10
#!/usr/bin/python3

import os
import logging

import argparse
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd

consLogs = []

prodCount = 0
consCount = 0
extraLatencyMessage = 0
latencyYAxis = []

def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf()   

def clearExtraLogs():
    os.system("sudo rm "+logDir+"/latency-log.txt")
    os.system("sudo rm -rf "+logDir+"/cons-latency-logs/")

def getProdDetails(prodId):
    global prodCount
    global consLogs

    latencyLog = open(logDir+"/latency-log.txt", "a")
    
    with open(logDir+'/prod/prod-'+str(prodId)+'.log') as f:
        for line in f:
            if "Topic: topic-" in line:
#                 msgProdTime = line.split(",")[0]
                msgProdTime = line.split(" INFO:Topic:")[0]
                topicSplit = line.split("topic-")
                topicId = topicSplit[1].split(";")[0]
                msgIdSplit = line.split("Message ID: ")
                msgId = msgIdSplit[1].split(";")[0]
                
                prodCount+=1

                if prodId < 10:
                    formattedProdId = "0"+str(prodId)
                else:
                    formattedProdId = str(prodId)

                for consId in range(switches):
                    if formattedProdId+"-"+msgId+"-topic-"+topicId in consLogs[consId].keys():
                        msgConsTime = consLogs[consId][formattedProdId+"-"+msgId+"-topic-"+topicId]

                        prodTime = datetime.strptime(msgProdTime, "%Y-%m-%d %H:%M:%S,%f")
                        consTime = datetime.strptime(msgConsTime, "%Y-%m-%d %H:%M:%S,%f")
                        latencyMessage = consTime - prodTime

                        latencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId+1)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
                        latencyLog.write("\n")    #latencyLog.write("\r\n")

                        # Write to the consumer latency log
                        consLatencyLog = open(logDir+"/cons-latency-logs/latency-log-cons-"+ str(consId+1) + ".txt", "a")
                        consLatencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
                        consLatencyLog.write("\n")    #latencyLog.write("\r\n")
                        consLatencyLog.close()

        print("Prod " + str(prodId) + ": " + str(datetime.now()))

    latencyLog.close()
                

def initConsStruct(switches):
    global consLogs

    for consId in range(switches):
        newDict = {}
        consLogs.append(newDict)
    
def readConsumerData():
    for consId in range(1, switches+1):
        f = open(logDir+'cons/cons-'+str(consId)+'.log')

        for lineNum, line in enumerate(f,1):         #to get the line number

            if "Prod ID: " in line:
                lineParts = line.split(" ")
                prodID = lineParts[4][0:-1]
                msgID = lineParts[7][0:-1]
                topic = lineParts[11][0:-1]
                consLogs[consId-1][prodID+"-"+msgID+"-"+topic] = lineParts[0] + " " + lineParts[1]
        f.close()
                
def latencyLog(consId, prodId, msgProdTime, msgConsTime, topicId, msgId, latencyMessage):
    latencyLog = open(logDir+"/latency-log.txt", "a")

    latencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
    latencyLog.write("\n")    #latencyLog.write("\r\n")
    latencyLog.close()
        
def plotLatencyScatter():
    lineXAxis = []
#     latencyYAxis = []
    global latencyYAxis
    with open(logDir+"/latency-log.txt", "r") as f:
        for lineNum, line in enumerate(f,1):         #to get the line number
            lineXAxis.append(lineNum)
            if "Latency of this message: " in line:
                firstSplit = line.split("Latency of this message: 0:")
                latencyYAxis.append(float(firstSplit[1][0:2])*60.0 + float(firstSplit[1][3:5]))
 
def plotLatencyCDF():
    global latencyYAxis
    
    latYAxis2 = []
    for lat in latencyYAxis:
        if lat <= 35:
            latYAxis2.append(lat)
    return latYAxis2    
      
parser = argparse.ArgumentParser(description='Script for measuring latency for each message.')
parser.add_argument('--number-of-switches', dest='switches', type=int, default=0, help='Number of switches')
parser.add_argument('--log-dir', dest='logDir', type=str, help='Producer log directory')

args = parser.parse_args()

switches = args.switches
# logDir = args.logDir
logDirStr = 'logs/messages-scenario-29/,logs/messages-scenario-30/'
logDirList = logDirStr.split(',')
lat = {}

for index, logDir in enumerate(logDirList):
    print('Log directory: '+logDir)
    os.system("sudo rm "+logDir+"latency-log.txt"+"; sudo touch "+logDir+"latency-log.txt")  
    os.makedirs(logDir+"cons-latency-logs", exist_ok=True)

    print(datetime.now())

    initConsStruct(switches)
    readConsumerData()

    for prodId in range(switches):
        getProdDetails(prodId+1)

    plotLatencyScatter()
    
    latYAxis2 = plotLatencyCDF()
    lat[index] = latYAxis2
    
    clearExtraLogs()

hist_kwargs = {"linewidth": 2,
              "edgecolor" :'salmon',
              "alpha": 0.4, 
              "color":  "w",
              "label": "Histogram",
              "cumulative": True}
kde_kwargs = {'linewidth': 3,
              'color': "blue",
              "alpha": 0.7,
              'label':'Kernel Density Estimation Plot',
              'cumulative': True}
sns.ecdfplot(lat[0])
sns.ecdfplot(lat[1])

# Add labels
plt.title('CDF of Latency')
plt.xlabel('Latency(s)', fontsize=22, fontweight='bold', labelpad=10)
plt.ylabel('Density', fontsize=22, fontweight='bold')
plt.ylim(bottom=0)
plt.legend(title="CDF", loc='upper right', fontsize=18, markerscale=2.0, labels=['Tuned', 'Ununed'])

plt.savefig("plots/CDF.pdf",bbox_inches="tight")
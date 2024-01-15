# command: sudo python3 code/PT-kafkaLatencyCDF.py
#!/usr/bin/python3

import os
import logging

import argparse
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd

consLogs = []
prodCount = 0
consCount = 0
extraLatencyMessage = 0

def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf()   

def reinitialization():
    global consLogs
    global prodCount
    global consCount
    global extraLatencyMessage

    consLogs = []
    prodCount = 0
    consCount = 0
    extraLatencyMessage = 0
       
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
                
                #print("producer: "+str(prodId)+" time: "+msgProdTime+" topic: "+topicId+" message ID: "+msgId)
                prodCount+=1

                if prodId < 10:
                    formattedProdId = "0"+str(prodId)
                else:
                    formattedProdId = str(prodId)

                for consId in range(switches):
                    #print(formattedProdId+"-"+msgId+"-topic-"+topicId)
                    if formattedProdId+"-"+msgId+"-topic-"+topicId in consLogs[consId].keys():
                        msgConsTime = consLogs[consId][formattedProdId+"-"+msgId+"-topic-"+topicId]

                        prodTime = datetime.strptime(msgProdTime, "%Y-%m-%d %H:%M:%S,%f")
                        consTime = datetime.strptime(msgConsTime, "%Y-%m-%d %H:%M:%S,%f")
                        latencyMessage = consTime - prodTime

                        #print(latencyMessage)
                        latencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId+1)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
                        latencyLog.write("\n")    #latencyLog.write("\r\n")

                        # Write to the consumer latency log
                        # consLatencyLog = open(logDir+"/cons-latency-logs/latency-log-cons-"+ str(consId+1) + ".txt", "a")
                        # consLatencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
                        # consLatencyLog.write("\n")    #latencyLog.write("\r\n")
                        # consLatencyLog.close()

        print("Prod " + str(prodId) + ": " + str(datetime.now()))

    latencyLog.close()
                

def initConsStruct(switches):
    global consLogs

    for consId in range(switches):
        newDict = {}
        consLogs.append(newDict)
    
def readConsumerData():

    #print("Start reading cons data: " + str(datetime.now()))
    for consId in range(1, switches+1):
        #print(logDir+'cons/cons-'+str(consId)+'.log')
        f = open(logDir+'/cons/cons-'+str(consId)+'.log')

        for lineNum, line in enumerate(f,1):         #to get the line number
            #print(line)

            if "Prod ID: " in line:
                lineParts = line.split(" ")
                #print(lineParts)

                prodID = lineParts[4][0:-1]
                #print(prodID)

                msgID = lineParts[7][0:-1]
                #print(msgID)

                topic = lineParts[11][0:-1]
                #print(topic)

                #print(prodID+"-"+msgID+"-"+topic)
                consLogs[consId-1][prodID+"-"+msgID+"-"+topic] = lineParts[0] + " " + lineParts[1]

        f.close()
        
def plotLatencyScatter():
    lineXAxis = []
    latencyYAxis = []
    with open(logDir+"/latency-log.txt", "r") as f:
        for lineNum, line in enumerate(f,1):         #to get the line number
            lineXAxis.append(lineNum)
            if "Latency of this message: " in line:
                firstSplit = line.split("Latency of this message: 0:")
                latencyYAxis.append(float(firstSplit[1][0:2])*60.0 + float(firstSplit[1][3:5]))

    return latencyYAxis
                            
def combinedCDFPlot(switches, logDir, label):
    os.system("sudo rm "+logDir+"/latency-log.txt"+"; sudo touch "+logDir+"/latency-log.txt")  

    print(datetime.now())

    initConsStruct(switches)
    readConsumerData()

    for prodId in range(switches):
        getProdDetails(prodId+1)

    latencyYAxis = plotLatencyScatter()
    return latencyYAxis

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for measuring latency for each message.')
    parser.add_argument('--number-of-switches', dest='switches', type=int, default=10, help='Number of switches')

    args = parser.parse_args()
    switches = args.switches

    # provide log directory for Kafka low latency scenario
    logDir = "../logs/kafka/scenario-30"
    label1 = 'Kafka-w/o-parameter-tuning'
    latencyYAxis1 = combinedCDFPlot(switches, logDir, label1)
    
    #Discard outliers (i.e., cut dataset at the 95th percentile)
    df = pd.DataFrame(latencyYAxis1, columns=["lat"])
    #print("Size: "+str(df.size))
    df = df[df["lat"] < df["lat"].quantile(.75)]
    #print("Size: "+str(df.size))
    #print(df.head())
    
    sns.ecdfplot(df.lat.tolist())
    print('Generated plot for '+label1)

    # reinitialization
    reinitialization()

    # provide log directory for Kafka high latency scenario
    logDir = "../logs/kafka/scenario-28"
    label2 = 'Kafka-w/-parameter-tuning'
    latencyYAxis2 = combinedCDFPlot(switches, logDir, label2)

    #Discard outliers (i.e., cut dataset at the 95th percentile)
    df = pd.DataFrame(latencyYAxis2, columns=["lat"])
    #print("Size: "+str(df.size))
    df = df[df["lat"] < df["lat"].quantile(.80)]
    #print("Size: "+str(df.size))
    #print(df.head())

    sns.ecdfplot(df.lat.tolist())
    print('Generated plot for '+label2)

    plt.title('CDF of Latency')
    plt.xlabel('Latency(s)')
    plt.ylabel('Density')
    plt.legend([label1,label2])
    plt.savefig("../results/PT-kafkaLatencyCDF.pdf", format='pdf', bbox_inches="tight")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

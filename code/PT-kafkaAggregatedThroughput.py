# command: sudo python3 PT-kafkaAggregatedThroughput.py
#!/usr/bin/python3

import os
import logging

import argparse

import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import numpy as np
import textwrap

interval = 5
inputBarDraw = 0

font = FontProperties()
font.set_family('serif')
font.set_name('Liberation Serif')
font.set_size(12)

matplotlib.rcParams['pdf.fonttype'] = 42   # for ACM submission
matplotlib.rcParams['ps.fonttype'] = 42
    
def clearExistingPlot():
    # clear the previous figure
    plt.close()
    plt.cla()
    plt.clf()    
    
def processMessageInput():
    mSizeParams = args.mSizeString.split(',')
    msgSize = 0
    if mSizeParams[0] == 'fixed':
        msgSize = int(mSizeParams[1])
    elif mSizeParams[0] == 'gaussian':
        msgSize = int(gauss(float(mSizeParams[1]), float(mSizeParams[2])))

    if msgSize < 1:
        msgSize = 1
    
    return msgSize

#to get bandwidth list for a specific port in a specific switch
def getStatsValue(switch,portNumber, portFlag):
    count=0
    dataList = []
    bandwidth =  [0]
    txFlag = 0
    maxBandwidth = -1.0
    
    with open(logDirectory+'bandwidth-log'+str(switch)+'.txt') as f:
        
        for line in f:
            if portNumber >= 10:
                spaces = " "
            else:
                spaces = "  "
            if "port"+spaces+str(portNumber)+":" in line: 
                
                if portFlag == 'tx pkts':
                    line = f.readline()
                    
                elif portFlag == 'tx bytes':
                    line = f.readline()
                    txFlag = 1           
                if txFlag == 1:
                    newPortFlag = "bytes"
                    data = line.split(newPortFlag+"=")
                else:
                    data = line.split(portFlag+"=")

                data = data[1].split(",")
                dataList.append(int(data[0]))
                if count>0: 
                    individualBandwidth = (dataList[count]-dataList[count-1])/interval
                    bandwidth.append(individualBandwidth)
                    if individualBandwidth > maxBandwidth:
                        maxBandwidth = individualBandwidth
                count+=1

    return bandwidth,count, maxBandwidth
         
# aggregated plot for all switches
def aggregatedPlot(x,y, yLabel, label, color, ls, lw):      
    plt.plot(x,y, label = label, color=color, linestyle=ls, linewidth=lw)
    
    plt.xlabel('Time (s)', fontsize=22, fontweight='bold', labelpad=10)
    # Split the ylabel into multiple lines if it's too long
    yLabel = '\n'.join(textwrap.wrap(yLabel, 16))
    plt.ylabel(yLabel, fontsize=22, fontweight='bold', labelpad=10)
    
    plt.xlim([0,410])
    plt.ylim([0, 8])
    
    plt.xticks(np.arange(0,401, step=100))
    plt.yticks(np.arange(0,8.1, step=2))
    
    ax = plt.gca()
    ax.xaxis.set_tick_params(labelsize=18, pad=5)
    ax.yaxis.set_tick_params(labelsize=18, pad=5)
    
    #plt.title("Aggregated Bandwidth for rx bytes("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)")

    plt.legend(frameon=False, loc='upper left', fontsize=18)

#checking input vs output to measure control traffic overhead
def overheadCheckPlot(portFlag, msgSize,label):    
    allBandwidth = []
    countX = 0
    
    portParams = args.switchPorts.split(',')
    for ports in portParams:
        portId, switchId = parseInput(ports)
    
        bandwidth, occurrence, maxBandwidth = getStatsValue(switchId,portId, portFlag)
        
        if countX == 0:
            countX = occurrence
        
        if len(bandwidth)<countX:
            for k in range(countX-len(bandwidth)):
                bandwidth.append(0)                    #filling with 0's to match up the length
            
        allBandwidth.append(bandwidth)

    bandwidthSum = []
    bandwidthSumLeaderLess = []

    for i in range(countX):
        valWithLeader = 0
        for j in range(args.switches):
            valWithLeader = valWithLeader+allBandwidth[j][i]

        bandwidthSum.append(valWithLeader)        
        
    newBandwidthSum = [x / 1000000 for x in bandwidthSum]
    newBandwidthSumLeaderLess = [x / 1000000 for x in bandwidthSumLeaderLess]
    
    #Discard outliers
    if label == 'w/ tuning':
        count = len([x for x in newBandwidthSum if x >= 0.5])
        newBandwidthSum = [x for x in newBandwidthSum if x < 0.5]
        countX = countX - count
    elif label == 'w/o tuning':
        count = len([x for x in newBandwidthSum if x >= 7.0])
        newBandwidthSum = [x for x in newBandwidthSum if x < 7.0]
        countX = countX - count
    timeList = list(range(0,countX*interval,interval))
    
    return timeList, newBandwidthSum, newBandwidthSumLeaderLess

#for aggregated plot of all host entry ports
def plotAggregatedBandwidth(label):   
    msgSize = processMessageInput()
    timeList, newBandwidthSum, newBandwidthSumLeaderLess = overheadCheckPlot("bytes", msgSize, label)
    return timeList, newBandwidthSum, newBandwidthSumLeaderLess
       
#parsing the sigle port        
def parseInput(portSwitchId):
    portParams = portSwitchId.split('-')
    switchId = portParams[0].split('S')[1]
    portId = portParams[1].split('P')[1]

    return int(portId), int(switchId)
    
# if __name__ == '__main__': 
parser = argparse.ArgumentParser(description='Script for plotting individual port log.')
parser.add_argument('--number-of-switches', dest='switches', type=int, default=10,
                help='Number of switches')
parser.add_argument('--switch-ports', dest='switchPorts', type=str, default='S1-P1,S2-P1,S3-P1,S4-P1,S5-P1,S6-P1,S7-P1,S8-P1,S9-P1,S10-P1', help='Plot bandwidth vs time in a port wise and aggregated manner')
parser.add_argument('--port-type', dest='portType', default="access-port", type=str, help='Plot bandwidth for access/trunc ports')
parser.add_argument('--message-size', dest='mSizeString', type=str, default='fixed,1000', help='Message size distribution (fixed, gaussian)')
parser.add_argument('--message-rate', dest='mRate', type=float, default=30.0, help='Message rate in msgs/second')
parser.add_argument('--ntopics', dest='nTopics', type=int, default=2, help='Number of topics')
parser.add_argument('--replication', dest='replication', type=int, default=10, help='Replication factor')
parser.add_argument('--nzk', dest='nZk', type=int, default=0, help='Kafka/Kraft')

args = parser.parse_args()

clearExistingPlot()

logDirectory = "../logs/kafka/scenario-30/bandwidth/"
label = 'w/o tuning'
timeList, newBandwidthSum, newBandwidthSumLeaderLess = plotAggregatedBandwidth(label=label)
aggregatedPlot(timeList, newBandwidthSum, "Bandwidth demand (Mbytes/s)", label, color='blue', ls='dashed', lw=3.0)
print("Aggregated plot created for kafka w/o tuning (scenario 30).")

logDirectory = "../logs/kafka/scenario-28/bandwidth/"
label = 'w/ tuning'
timeList, newBandwidthSum, newBandwidthSumLeaderLess = plotAggregatedBandwidth(label=label)
aggregatedPlot(timeList, newBandwidthSum, "Bandwidth demand (Mbytes/s)", label, color='red', ls='solid', lw=3.0)
print("Aggregated plot created for kafka w/ tuning (scenario 28).")                      

plt.savefig("../results/PT-kafkaAggregatedThroughput.pdf", format='pdf', bbox_inches="tight")

















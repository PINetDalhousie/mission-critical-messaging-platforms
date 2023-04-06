# smaple command to run this script: sudo python3 plot-scripts/bandwidthPlotScript.py --port-type access-port --message-rate 30 --ntopics 2
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

interval = 5
inputBarDraw = 0

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

# plot input data rate in one horizontal line for all/individual host ports
def plotInputDataRate(msgSize, mRate, countX, switches):
    dataRate = msgSize * mRate * switches
    dataRateList = [dataRate] * countX
    return dataRateList

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
def aggregatedPlot(portFlag,x,y, yLeaderLess, yLabel, msgSize, countX): 

    newXValues = []
    newYValues = []

    for i in range(len(y)):
        # discarding outliers
        if args.switches == 10 and y[i] <= 8:
            newXValues.append(x[i])
            newYValues.append(y[i])
        elif args.switches == 20 and y[i] <= 40:
            newXValues.append(x[i])
            newYValues.append(y[i])
     
    # plt.plot(newXValues,newYValues, label = "output (with leader)")

    # dataRateList = plotInputDataRate(msgSize, args.mRate, countX, args.switches)
    # dataRateList = [x / 1000000 for x in dataRateList]

    # plt.xlabel('Time (s)')
    # plt.ylabel(yLabel)
    
    # plt.ylim(bottom=0)

    return newXValues, newYValues

    
#checking input vs output to measure control traffic overhead
def overheadCheckPlot():
    # clearExistingPlot()  

    msgSize = processMessageInput()
    portFlag = "bytes"
    
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
        
    timeList = list(range(0,countX*interval,interval))


    newBandwidthSum = [x / 1000000 for x in bandwidthSum]
    newBandwidthSumLeaderLess = [x / 1000000 for x in bandwidthSumLeaderLess]
    newXValues, newYValues = aggregatedPlot(portFlag,timeList, newBandwidthSum, newBandwidthSumLeaderLess, "Throughput (Mbps)", msgSize, countX)   

    return newXValues, newYValues
       
#parsing the sigle port        
def parseInput(portSwitchId):
    portParams = portSwitchId.split('-')
    switchId = portParams[0].split('S')[1]
    portId = portParams[1].split('P')[1]

    return int(portId), int(switchId)


# if __name__ == '__main__': 
parser = argparse.ArgumentParser(description='Script for plotting individual port log.')
# parser.add_argument('--number-of-switches', dest='switches', type=int, default=0,
#                 help='Number of switches')
# parser.add_argument('--switch-ports', dest='switchPorts', type=str, help='Plot bandwidth vs time in a port wise and aggregated manner')
parser.add_argument('--port-type', dest='portType', default="access-port", type=str, help='Plot bandwidth for access/trunc ports')
parser.add_argument('--message-size', dest='mSizeString', type=str, default='fixed,10', help='Message size distribution (fixed, gaussian)')
parser.add_argument('--message-rate', dest='mRate', type=float, default=1.0, help='Message rate in msgs/second')
parser.add_argument('--ntopics', dest='nTopics', type=int, default=1, help='Number of topics')
# parser.add_argument('--replication', dest='replication', type=int, default=1, help='Replication factor')
# parser.add_argument('--log-dir', dest='logDir', type=str, help='Producer log directory')

args = parser.parse_args()


# create switchPorts for switch 10 and 20
switchList = [10,20]
band10 ={}
band20 ={}
for i in switchList:
    args.switches = i
    args.replication = i
    switchPorts = ""
    portCount = 1
    for pc in range(args.switches-1):
        switchPorts = switchPorts +"S"+str(pc+1)+"-P1,"
    switchPorts = switchPorts +"S"+str(args.switches)+"-P1"
    args.switchPorts = switchPorts

    if i == 10:
        logDirectory = "logs/bandwidth-scenario-30/"
        newXValues, newYValues = overheadCheckPlot()      #for aggregated plot   
        band10["X"] = newXValues
        band10["Y"] = newYValues
    else:
        logDirectory = "logs/bandwidth-scenario-31/"
        newXValues, newYValues = overheadCheckPlot()      #for aggregated plot   
        band20["X"] = newXValues
        band20["Y"] = newYValues

    
plt.plot(band10["X"],band10["Y"], label = "10")
plt.plot(band20["X"],band20["Y"], label = "20")
plt.xlabel('Time (s)', fontsize=22, fontweight='bold', labelpad=10)
plt.ylabel('Throughput (Mbps)', fontsize=22, fontweight='bold')

plt.ylim(bottom=0)
plt.legend(title="Nodes", loc='upper left', frameon=False, fontsize=18, markerscale=2.0)

ax = plt.gca()
ax.xaxis.set_ticks(np.arange(0, 451, 150))
ax.xaxis.set_tick_params(labelsize=18)
ax.yaxis.set_ticks(np.arange(0, 31, 5))
ax.yaxis.set_tick_params(labelsize=18)

ax.set_ylim([0, 30])
ax.set_xlim([0, 450])

plt.savefig("plots/"+"aggregated-rx-bytes.pdf",bbox_inches="tight")
print("Aggregated plot created.")
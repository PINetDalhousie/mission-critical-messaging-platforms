# command: sudo python3 scripts/combinedThroughput.py
#!/usr/bin/python3

import os
import logging

import argparse

import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

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
def aggregatedPlot(portFlag,x,y, yLeaderLess, yLabel, msgSize, countX, label):      
    plt.plot(x,y, label = label)
    
    plt.xlabel('Time (sec)')
    plt.ylabel(yLabel)
    
    plt.ylim([0, 140])
    plt.ylim(bottom=0)

    if portFlag=="bytes":
        plt.title("Aggregated Bandwidth for rx bytes("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)")
    else:
        plt.title("Aggregated Bandwidth for " + portFlag+"("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)") 

    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

#checking input vs output to measure control traffic overhead
def overheadCheckPlot(portFlag, msgSize,scenario, label):    
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
    
    if portFlag=="rx pkts" or portFlag=="tx pkts":
        aggregatedPlot(portFlag,timeList, bandwidthSum, bandwidthSumLeaderLess, "Throughput (pkts/sec)", msgSize, countX, label)
    else:
        newBandwidthSum = [x / 1000000 for x in bandwidthSum]
        newBandwidthSumLeaderLess = [x / 1000000 for x in bandwidthSumLeaderLess]
        aggregatedPlot(portFlag,timeList, newBandwidthSum, newBandwidthSumLeaderLess, "Throughput (Mbytes/sec)", msgSize, countX, label)    
    
    if portFlag=="bytes" and scenario==31:
        plt.savefig("plots/Kafka-rMQ-aggregated-throughput",bbox_inches="tight")
    # else:    
    #     plt.savefig(logDirectory+args.portType+" aggregated "+portFlag+"("+str(args.switches)+" nodes "+str(args.nTopics)+" topics "+str(args.replication)+" replication)",bbox_inches="tight")         

#for aggregated plot of all host entry ports
def plotAggregatedBandwidth(scenario, label):   
    msgSize = processMessageInput()
    overheadCheckPlot("bytes", msgSize, scenario, label)
       
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
parser.add_argument('--message-rate', dest='mRate', type=float, default=3.0, help='Message rate in msgs/second')
parser.add_argument('--ntopics', dest='nTopics', type=int, default=2, help='Number of topics')
parser.add_argument('--replication', dest='replication', type=int, default=10, help='Replication factor')
parser.add_argument('--nzk', dest='nZk', type=int, default=0, help='Kafka/Kraft')
parser.add_argument('--log-dir', dest='logDir', type=str, default='logs/kafka/scenario-30', help='Producer log directory')

args = parser.parse_args()

logDirectory = args.logDir + "/bandwidth/"

clearExistingPlot()
plotAggregatedBandwidth(scenario=30, label='10-node-Kafka')      #for aggregated plot    
print("Aggregated plot created for kafka 10 node scenario (scenario 30).")

# task C: 20 node Kafka aggregated plot
logDirectory = args.logDir.replace("kafka/scenario-30", "rMQ/10node-link-lat-1ms-msg-rate-30")
logDirectory = logDirectory + "/bandwidth/"
plotAggregatedBandwidth(scenario=0, label='10-node-rMQ')      #for aggregated plot    

args.switches = 20
args.switchPorts = "S1-P1,S2-P1,S3-P1,S4-P1,S5-P1,S6-P1,S7-P1,S8-P1,S9-P1,S10-P1,S11-P1,S12-P1,S13-P1,S14-P1,S15-P1,S16-P1,S17-P1,S18-P1,S19-P1,S20-P1"
args.replication = 20
logDirectory = args.logDir.replace("scenario-30", "scenario-31")
logDirectory = logDirectory + "/bandwidth/"
plotAggregatedBandwidth(scenario=31, label='20-node-Kafka')      #for aggregated plot    
print("Aggregated plot for all created.")                       
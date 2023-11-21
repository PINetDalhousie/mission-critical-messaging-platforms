# mission-critical-messaging-platforms
This project takes help from two other repositories:
- [Military Coordination Applition using Apache Kafka](https://github.com/PINetDalhousie/amnis-data-sync)
- [Military Coordination Applition using RabbitMQ](https://github.com/PINetDalhousie/amnis-data-sync-rabbitmq)

## Plot generation
1. To get the kafka and rMQ combined aggregated throughput plot, run:
    sudo python3 scripts/combinedThroughput.py

2. To get the kafka and rMQ combined latency CDF plot, run:
    sudo python3 scripts/combinedCDF.py

3. In terms of Parameter Tuning, to get the kafka latency CDF plot, run:
    sudo python3 scripts/PT-kafkaLatencyCDF.py

4. In terms of Parameter Tuning, to get the kafka aggregated throughput plot, run:
    sudo python3 scripts/PT-kafkaAggregatedThroughput.py

# mission-critical-messaging-platforms
This project takes help from two other repositories:
- [Case study with Apache Kafka](https://github.com/PINetDalhousie/amnis-data-sync)
- [Case study with RabbitMQ](https://github.com/PINetDalhousie/amnis-data-sync-rabbitmq)

## Dependency

We tested the plot generating codes over Ubuntu 20.04.6 and is based on Python 3.8.10.

> `cd mission-critical-messaging-platforms`


> `python3 -m venv .env`


> `source .env/bin/activate`


> `pip install -r requirements.txt`


## Plot generation
1. To get the Kafka and rMQ combined aggregated throughput plot, run:
    sudo python3 scripts/combinedThroughput.py

2. To get the Kafka and rMQ combined latency CDF plot, run:
    sudo python3 scripts/combinedCDF.py

3. In terms of Parameter Tuning, to get the Kafka latency CDF plot, run:
    sudo python3 scripts/PT-kafkaLatencyCDF.py

4. In terms of Parameter Tuning, to get the Kafka aggregated throughput plot, run:
    sudo python3 scripts/PT-kafkaAggregatedThroughput.py

## Additional Results
Additional evaluation plots that stated in the [paper](https://www.techrxiv.org/doi/full/10.36227/techrxiv.171340979.91183191) can be found under the [results](https://github.com/PINetDalhousie/mission-critical-messaging-platforms/tree/main/results) directory along with a description.

## Security Analysis
RQ1. Which security mechanisms are available on data streaming platforms?

=> Attackers are increasingly targeting mission-critical systems. As a result, there has been an uptick in novel defenses for hardening these systems. Although security is still not a primary concern on most data streaming platforms, the support for different security mechanisms on them is expanding quickly. As part of our analysis, we briefly summarize the security mechanisms available on COTS data streaming platforms as a way to identify: i) common flaws not covered by the deployed solutions; and ii) potential misuses of the available security modules. Most existing data streaming platforms center their security efforts around three main services: authentication, authorization, and data encryption. For authentication, Kafka and rMQ support the Simple Authentication and Security Layer (SASL) framework. Although they differ in their natively supported SASL authentication mechanisms, a large group of authentication protocols, including LDAP, Kerberos, and OAuth2, is available through external plug-ins. Regarding authorization, both Kafka and rMQ use access control lists (ACLs) to control which users are allowed to perform certain operations on given resources. However, none of the tools have native support for specifying complex policies such as the ones used to manage user groups and require external modules to deploy, e.g., role- or attribute-based access control (a.k.a. RBAC and ABAC policies, respectively). Finally, Kafka and rMQ provide data encryption by means of the TLS protocol where both tools support version 1.3. None of the security mechanisms mentioned above are enabled on the platforms we studied by default. Therefore, users must explicitly configure and activate them according to their needs and preferences.


RQ2. What kind of misuses are data streaming platform security mechanisms mostly susceptible to?

=> Given our experience deploying different data streaming platforms in highly secure environments, we share some lessons learned regarding configuration mistakes. The most common issue is the fact that current platforms are not secure by default, meaning the user must explicitly set a security mechanism to enforce policies other than "no action". For example, Kafka's data encryption approach requires platform operators to explicitly set TLS listeners on each broker otherwise traffic will flow in plaintext. Moreover, operators must *also* remember to delete any existing plaintext listener, which are automatically initialized. A second main challenge we faced was properly configuring an ACL. Since none of the analyzed tools provide a high-level description language for specifying access control policies, operators may end up having to set permissions at an extremely fine granularity, which makes the process cumbersome and error-prone, especially in large-scale scenarios. Furthermore, there is no way to validate a deployed configuration other than exhaustive (i.e., brute force) testing.

## Configurable parameter list
  The following table provides an overview of the parameters available for tuning in the Apache Kafka case study:
  |     Simulation Argument     |     Description                                                                                                                              |     Acceptable Value(s)                                                                                                                                                                                            |     Usage Restrictions                                                                                           |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
|     replication             |     Replication factor                                                                                                                       |     Integer value >0. Default=1                                                                                                                                                                                       |     N/A                 
|     acks                    |     Controls how many replicas must receive the record before producer   considers successful write.                                         |     Acceptable integer values include 0, 1, 2 (2=all). Default=1                                                                                                                                                   |     N/A                                                                                                          |
|     compression             |     Compression algorithm used to compress data sent to brokers.                                                                             |     Acceptable string values include gzip, snappy, lz4, None. Default=‘None’                                                                                                                                       |     N/A                                                                                                          |
|     batch-size              |     When multiple records are sent to the same partition, the producer   will batch them together (bytes)                                    |     Integer value >=0. Default=16384                                                                                                                                                                                   |     N/A                                                                                                          |
|     linger                  |     Controls the amount of time (in ms) to wait for additional messages   before sending the current batch                                   |     Integer value >=0. Default=0                                                                                                                                                                                       |     N/A                                                                                                          |
|     request-timeout         |     Controls how long producer waits for a reply from server when sending   data                                                             |     Integer value >=0. Default=30000                                                                                                                                                                                   |     N/A                                                                                                          |
|     fetch-min-bytes         |     Minimum amount of data consumer needs to receive from the broker when   fetching records (bytes)                                         |     Integer value >=0. Default=1                                                                                                                                                                                       |     N/A                                                                                                          |
|     fetch-max-wait          |     How long the broker will wait (in ms) before sending data to consumer                                                                    |     Integer value >=0. Default=500                                                                                                                                                                                     |     N/A                                                                                                          |
|     session-timeout         |     Time (in ms) a consumer can be out of contact with brokers while   still considered alive.                                               |     Integer value  in the allowable   range as configured in the broker configuration by   group.min.session.timeout.ms (default  6000ms) and group.max.session.timeout.ms (default   1800000ms). Default=10000    |     N/A                                                                                                          |
|     replica-max-wait        |     Max wait time for each fetcher request issued by follower replicas     |     Integer value >=0 but less than the replica.lag.time.max.ms (default 30000ms). Default=500                                                                                                                                                                                     |     N/A                                                                                                          |
|     replica-min-bytes       |     Minimum bytes expected for each fetch response                                                                                           |     Integer value >=0. Default=1                                                                                                                                                                                       |     N/A                                                                                                          |
|     offsets-replication     |     The replication factor for the offsets topic                                                                                             |     Integer value >=0. Default = 1                                                                                                                                                                                 |     Kafka with Zookeeper only, no support for KRaft                                                              |
|     ssl                     |     Enable encryption using SSL                                                                                                              |     N/A. Specify attribute to enable                                                                                                                                                                               |     KRaft only, no support for Kafka with Zookeeper. Not supported by   Java Consumer                            |
|     auth                    |     Enable authentication                                                                                                                    |     N/A. Specify attribute to enable                                                                                                                                                                               |     KRaft only, no support for  Kafka   with Zookeeper                                                           |


## Research
If you find our work relevant to your research, please consider citing:

```bibtex
@article{missionCriticalStreamingPlatforms2024,
  title={Are data streaming platforms ready for a mission critical world?},
  author={Ifath, Md Monzurul Amin and Neves, Miguel and Bremner, Brandon and White, Jeff and Szeredi, Tomas and Haque, Israat},
  journal={Authorea Preprints},
  year={2024},
  publisher={Authorea}
}
```

## Contact

Md. Monzurul Amin Ifath (monzurul.amin@dal.ca)

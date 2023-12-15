using System.Linq;
using common.Model;
using Prometheus;

namespace common.Prometheus
{

    /// <summary>
    /// 
    /// </summary>
    public class PrometheusConsumerStatisticsHandler : PrometheusStatisticsHandler
    {
        private readonly Gauge TotalNumberOfMessagesConsumed;
        private readonly Gauge TotalNumberOfMessageBytesConsumed;
        private readonly Gauge NumberOfOpsWaitinInQueue; // Gauge
        private readonly Gauge TotalNumberOfResponsesReceivedFromKafka;
        private readonly Gauge TotalNumberOfBytesReceivedFromKafka;
        private readonly Gauge RebalanceAge; // Gauge
        private readonly Gauge TotalNumberOfRelabalance; // Gauge assign or revoke

        //PER BROKER (add Broker NodeId as label)
        private readonly Gauge TotalNumberOfResponsesReceived;
        private readonly Gauge TotalNumberOfBytesReceived;
        private readonly Gauge TotalNumberOfReceivedErrors;
        private readonly Gauge NumberOfConnectionAttemps; // Including successful, failed and name resolution failures
        private readonly Gauge NumberOfDisconnects;
        private readonly Gauge BrokerLatencyAverageMs;

        // Per Topic (add topic name as label)			
        private readonly Gauge BatchSizeAverageBytes;
        private readonly Gauge BatchMessageCountsAverage;

        // Per partition(topic brokder id PartitionId as label)

        private readonly Gauge ConsumerLag; // Gauge
        private readonly Gauge TotalNumberOfMessagesconsumed; // Gauge
        private readonly Gauge TotalNumberOfBytesConsumed; // Gauge

        public PrometheusConsumerStatisticsHandler(string[] labelNames = null, string[] labelValues = null) : base(labelNames, labelValues)
        {
            TotalNumberOfMessagesConsumed = Metrics.CreateGauge("kafka_consumed_total", "Total number of messages consumed, not including ignored messages (due to offset, etc), from Kafka brokers.", GeneralLevelLabelNames);
            TotalNumberOfMessageBytesConsumed = Metrics.CreateGauge("kafka_bytes_consumed_total", "Total number of bytes received from Kafka brokers.", GeneralLevelLabelNames);
            NumberOfOpsWaitinInQueue = Metrics.CreateGauge("kafka_ops_waiting_queue_total", "Number of ops (callbacks, events, etc) waiting in queue for application to serve with rd_kafka_poll().", GeneralLevelLabelNames);
            TotalNumberOfResponsesReceivedFromKafka = Metrics.CreateGauge("kafka_responses_received_total", "Total number of responses received from Kafka brokers.", GeneralLevelLabelNames);
            TotalNumberOfBytesReceivedFromKafka = Metrics.CreateGauge("kafka_bytes_received_total", "Total number of bytes received from Kafka brokers.", GeneralLevelLabelNames);
            
            RebalanceAge = Metrics.CreateGauge("kafka_rebalance_age", "Time elapsed since last rebalance (assign or revoke) (milliseconds).", GeneralLevelLabelNames);
            TotalNumberOfRelabalance = Metrics.CreateGauge("kafka_rebalance_total", "Total number of rebalances (assign or revoke).", GeneralLevelLabelNames);


            //PER BROKER (add Broker NodeId as label)
            TotalNumberOfResponsesReceived = Metrics.CreateGauge("kafka_broker_responses_total", "Total number of responses received.", BrokerLevelLabelNames);
            TotalNumberOfBytesReceived = Metrics.CreateGauge("kafka_broker_responses_byte_total", "Total number of bytes received.", BrokerLevelLabelNames);
            TotalNumberOfReceivedErrors = Metrics.CreateGauge("kafka_broker_error_total", "Total number of receive errors.", BrokerLevelLabelNames);
            NumberOfConnectionAttemps = Metrics.CreateGauge("kafka_broker_connection_total", "Number of connection attempts, including successful and failed, and name resolution failures.", BrokerLevelLabelNames);
            NumberOfDisconnects = Metrics.CreateGauge("kafka_broker_disconnection_total", "Number of disconnects (triggered by broker, network, load-balancer, etc.).", BrokerLevelLabelNames);
            BrokerLatencyAverageMs = Metrics.CreateGauge("kafka_broker_latency_average_ms", "Broker latency / round-trip time in microseconds.", BrokerLevelLabelNames);

            // Per Topic (add topic name as label)			
            BatchSizeAverageBytes = Metrics.CreateGauge("kafka_topic_batch_size_bytes_average", "Batch sizes in bytes average.", TopicLevelLabelNames);
            BatchMessageCountsAverage = Metrics.CreateGauge("kafka_topic_batch_count_average", "Batch message counts average.", TopicLevelLabelNames);

            // Per partition(topic brokder id PartitionId as label)

            ConsumerLag = Metrics.CreateGauge("kafka_partition_lag", "Difference between (hi_offset or ls_offset) - max(app_offset, committed_offset). hi_offset is used when isolation.level=read_uncommitted, otherwise ls_offset.", PartitionLevelLabelNames);
            TotalNumberOfMessagesconsumed = Metrics.CreateGauge("kafka_partition_message_consumed_total", "Total number of messages consumed, not including ignored messages (due to offset, etc).", PartitionLevelLabelNames);
            TotalNumberOfBytesConsumed = Metrics.CreateGauge("kafka_partition_message_bytes_consumed_total", "Total number of bytes received for rxmsgs", PartitionLevelLabelNames);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="statistics"></param>
        public override void Publish(Statistics statistics)
        {
            var generalLabelValues = (new string[] { statistics.ClientId.ToString() }).Concat(LabelValues).ToArray();
            // General statistics
            TotalNumberOfMessagesConsumed.Labels(generalLabelValues).Set(statistics.TotalNumberOfMessagesConsumed);
            TotalNumberOfMessageBytesConsumed.Labels(generalLabelValues).Set(statistics.TotalNumberOfMessageBytesConsumed);
            NumberOfOpsWaitinInQueue.Labels(generalLabelValues).Set(statistics.NumberOfOpsWaitinInQueue);
            TotalNumberOfResponsesReceivedFromKafka.Labels(generalLabelValues).Set(statistics.TotalNumberOfResponsesReceivedFromKafka);
            TotalNumberOfBytesReceivedFromKafka.Labels(generalLabelValues).Set(statistics.TotalNumberOfBytesReceivedFromKafka);
            
            RebalanceAge.Labels(generalLabelValues).Set(statistics.ConsumerGroups.RebalanceAge);
            TotalNumberOfRelabalance.Labels(generalLabelValues).Set(statistics.ConsumerGroups.TotalNumberOfRelabalance);


            // Broker statistics
            foreach (var broker in statistics.Brokers)
            {
                var brokerLabelValues = (new string[] { statistics.ClientId.ToString(), broker.Value.NodeId.ToString() }).Concat(LabelValues).ToArray();

                TotalNumberOfResponsesReceived.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfResponsesReceived);
                TotalNumberOfBytesReceived.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfBytesReceived);
                TotalNumberOfReceivedErrors.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfReceivedErrors);
                NumberOfConnectionAttemps.Labels(brokerLabelValues).Set(broker.Value.NumberOfConnectionAttemps);
                NumberOfDisconnects.Labels(brokerLabelValues).Set(broker.Value.NumberOfDisconnects);
                BrokerLatencyAverageMs.Labels(brokerLabelValues).Set(broker.Value.BrokerLatency.Average);
            }

            // Per Topic(add topic name as label)
            foreach (var topic in statistics.Topics)
            {
                var topicLabelValues = (new string[] { statistics.ClientId.ToString(), topic.Value.TopicName }).Concat(LabelValues).ToArray();
                BatchSizeAverageBytes.Labels(topicLabelValues).Set(topic.Value.BatchSize.Average);
                BatchMessageCountsAverage.Labels(topicLabelValues).Set(topic.Value.BatchMessageCounts.Average);


                //  Per Partition(topic brokder id PartitionId as label)
                foreach (var partition in topic.Value.Partitions)
                {
                    var partitionLabelsValues = (new string[] { statistics.ClientId.ToString(), partition.Value.BrokerId.ToString(), topic.Value.TopicName, partition.Value.PartitionId.ToString() }).Concat(LabelValues).ToArray();

                    ConsumerLag.Labels(partitionLabelsValues).Set(partition.Value.ConsumerLag);
                    TotalNumberOfMessagesconsumed.Labels(partitionLabelsValues).Set(partition.Value.TotalNumberOfMessagesconsumed);
                    TotalNumberOfBytesConsumed.Labels(partitionLabelsValues).Set(partition.Value.TotalNumberOfBytesConsumed);
                }

            }
        }
    }
}
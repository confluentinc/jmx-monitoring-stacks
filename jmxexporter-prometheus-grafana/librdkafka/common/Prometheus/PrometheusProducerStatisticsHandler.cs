using System.Linq;
using common.Model;
using Prometheus;

namespace common.Prometheus
{
    /// <summary>
    /// 
    /// </summary>
    public class PrometheusProducerStatisticsHandler : PrometheusStatisticsHandler
    {
        private readonly Gauge TotalNumberOfMessagesProduced;
        private readonly Gauge TotalNumberOfMessageBytesProduced;
        private readonly Gauge NumberOfOpsWaitinInQueue; // Gauge
        private readonly Gauge CurrentNumberOfMessagesInProducerQueues; // Gauge
        private readonly Gauge CurrentSizeOfMessagesInProducerQueues; // Gauge
        private readonly Gauge MaxMessagesAllowedOnProducerQueues;
        private readonly Gauge MaxSizeOfMessagesAllowedOnProducerQueues;
        private readonly Gauge TotalNumberOfRequestSentToKafka;
        private readonly Gauge TotalNumberOfBytesTransmittedToKafka;

        //PER BROKER (add Broker NodeId as label)
        private readonly Gauge NumberOfRequestAwaitingTransmission; // Gauge
        private readonly Gauge NumberOfMessagesAwaitingTransmission; //Gauge
        private readonly Gauge NumberOfRequestInFlight; // Gauge
        private readonly Gauge NumberOfMessagesInFlight; // Gauge
        private readonly Gauge TotalNumberOfRequestSent;
        private readonly Gauge TotalNumberOfBytesSent;
        private readonly Gauge TotalNumberOfTransmissionErrors;
        private readonly Gauge TotalNumberOfRequestRetries;
        private readonly Gauge TotalNumberOfRequestTimeout;
        private readonly Gauge NumberOfConnectionAttemps; // Including successful, failed and name resolution failures
        private readonly Gauge NumberOfDisconnects;
        private readonly Gauge InternalQueueProducerLatencyAverageMs;
        private readonly Gauge InternalRequestQueueLatencyAverageMs;
        private readonly Gauge BrokerLatencyAverageMs;

        // Per Topic(add topic name as label)
        private readonly Gauge BatchSizeAverageBytes;
        private readonly Gauge BatchMessageCountsAverage;

        //  Per Partition(topic brokder id PartitionId as label)
        private readonly Gauge PartitionTotalNumberOfMessagesProduced; // Gauge
        private readonly Gauge PartitionTotalNumberOfBytesProduced; // Gauge
        private readonly Gauge PartitionNumberOfMessagesInFlight; // Gauge
        private readonly Gauge PartitionNextExpectedAckSequence; // Gauge idempotent producer
        private readonly Gauge PartitionLastInternalMessageIdAcked; // Gauge idempotent producer

        public PrometheusProducerStatisticsHandler(string[] labelNames = null, string[] labelValues = null) : base(labelNames, labelValues)
        {
            TotalNumberOfMessagesProduced = Metrics.CreateGauge("kafka_transmitted_message_total", "Total number of messages transmitted (produced) to Kafka brokers", GeneralLevelLabelNames);
            TotalNumberOfMessageBytesProduced = Metrics.CreateGauge("kafka_transmitted_message_bytes_total", "Total number of message bytes (including framing, such as per-Message framing and MessageSet/batch framing) transmitted to Kafka brokers", GeneralLevelLabelNames);
            NumberOfOpsWaitinInQueue = Metrics.CreateGauge("kafka_ops_waiting_queue_total", "Number of ops (callbacks, events, etc) waiting in queue for application to serve with rd_kafka_poll()", GeneralLevelLabelNames);
            CurrentNumberOfMessagesInProducerQueues = Metrics.CreateGauge("kafka_messages_queue_current", "Current number of messages in producer queues", GeneralLevelLabelNames);
            CurrentSizeOfMessagesInProducerQueues = Metrics.CreateGauge("kafka_messages_queue_size_bytes_total", "Current total size of messages in producer queues", GeneralLevelLabelNames);
            MaxMessagesAllowedOnProducerQueues = Metrics.CreateGauge("kafka_message_queue_max", "Threshold: maximum number of messages allowed allowed on the producer queues", GeneralLevelLabelNames);
            MaxSizeOfMessagesAllowedOnProducerQueues = Metrics.CreateGauge("kafka_message_queue_size_bytes_max", "Threshold: maximum total size of messages allowed on the producer queues", GeneralLevelLabelNames);
            TotalNumberOfRequestSentToKafka = Metrics.CreateGauge("kafka_transmitted_request_total", "Total number of requests sent to Kafka brokers", GeneralLevelLabelNames);
            TotalNumberOfBytesTransmittedToKafka = Metrics.CreateGauge("kafka_transmited_request_bytes_total", "Total number of bytes transmitted to Kafka brokers", GeneralLevelLabelNames);

            //PER BROKER (add Broker NodeId as label)
            NumberOfRequestAwaitingTransmission = Metrics.CreateGauge("kafka_broker_request_awaiting_total", "Number of requests awaiting transmission to broker", BrokerLevelLabelNames);
            NumberOfMessagesAwaitingTransmission = Metrics.CreateGauge("kafka_broker_message_awaiting_total", "Number of messages awaiting transmission to broker", BrokerLevelLabelNames);
            NumberOfRequestInFlight = Metrics.CreateGauge("kafka_broker_request_in_flight_total", "Number of requests in-flight to broker awaiting response", BrokerLevelLabelNames);
            NumberOfMessagesInFlight = Metrics.CreateGauge("kafka_broker_message_in_flight_total", "Number of messages in-flight to broker awaiting response", BrokerLevelLabelNames);
            TotalNumberOfRequestSent = Metrics.CreateGauge("kafka_broker_request_sent_total", "Total number of requests sent", BrokerLevelLabelNames);
            TotalNumberOfBytesSent = Metrics.CreateGauge("kafka_broker_request_sent_bytes_total", "Total number of bytes sent", BrokerLevelLabelNames);
            TotalNumberOfTransmissionErrors = Metrics.CreateGauge("kafka_broker_error_total", "Total number of transmission errors", BrokerLevelLabelNames);
            TotalNumberOfRequestRetries = Metrics.CreateGauge("kafka_broker_retries_total", "Total number of request retries", BrokerLevelLabelNames);
            TotalNumberOfRequestTimeout = Metrics.CreateGauge("kafka_broker_timeout_total", "Total number of requests timed out", BrokerLevelLabelNames);
            NumberOfConnectionAttemps = Metrics.CreateGauge("kafka_broker_connection_total", "Number of connection attempts, including successful and failed, and name resolution failures.", BrokerLevelLabelNames);
            NumberOfDisconnects = Metrics.CreateGauge("kafka_broker_disconnection_total", "Number of disconnects (triggered by broker, network, load-balancer, etc.).", BrokerLevelLabelNames);
            InternalQueueProducerLatencyAverageMs = Metrics.CreateGauge("kafka_broker_internal_queue_latency_ms", "Internal producer queue latency in microseconds. ", BrokerLevelLabelNames);
            InternalRequestQueueLatencyAverageMs = Metrics.CreateGauge("kafka_broker_internal_request_queue_latency_ms", "Internal request queue latency in microseconds. This is the time between a request is enqueued on the transmit (outbuf) queue and the time the request is written to the TCP socket. Additional buffering and latency may be incurred by the TCP stack and network.", BrokerLevelLabelNames);
            BrokerLatencyAverageMs = Metrics.CreateGauge("kafka_broker_latency_average_ms", "Broker latency / round-trip time in microseconds.", BrokerLevelLabelNames);

            // Per Topic(add topic name as label)

            BatchSizeAverageBytes = Metrics.CreateGauge("kafka_topic_batch_size_bytes_average", "Batch sizes in bytes average", TopicLevelLabelNames);
            BatchMessageCountsAverage = Metrics.CreateGauge("kafka_topic_batch_count_average", "Batch message counts average", TopicLevelLabelNames);

            //  Per Partition(topic brokder id PartitionId as label)

            PartitionTotalNumberOfMessagesProduced = Metrics.CreateGauge("kafka_partition_transmitted_message_total", "Total number of messages transmitted (produced)", PartitionLevelLabelNames);
            PartitionTotalNumberOfBytesProduced = Metrics.CreateGauge("kafka_partition_transmitted_message_bytes_total", "Total number of bytes transmitted for txmsgs", PartitionLevelLabelNames);
            PartitionNumberOfMessagesInFlight = Metrics.CreateGauge("kafka_partition_message_in_flight_total", "Current number of messages in-flight to/from broker", PartitionLevelLabelNames);
            PartitionNextExpectedAckSequence = Metrics.CreateGauge("kafka_partition_next_expected_ack", "Next expected acked sequence (idempotent producer)", PartitionLevelLabelNames);
            PartitionLastInternalMessageIdAcked = Metrics.CreateGauge("kafka_partition_last_message_id_acked", "Last acked internal message id (idempotent producer)", PartitionLevelLabelNames);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="statistics"></param>
        public override void Publish(Statistics statistics)
        {
            var generalLabelValues = (new string[] { statistics.ClientId.ToString() }).Concat(LabelValues).ToArray();

            TotalNumberOfMessagesProduced.Labels(generalLabelValues).Set(statistics.TotalNumberOfMessagesProduced);
            TotalNumberOfMessageBytesProduced.Labels(generalLabelValues).Set(statistics.TotalNumberOfMessageBytesProduced);
            NumberOfOpsWaitinInQueue.Labels(generalLabelValues).Set(statistics.NumberOfOpsWaitinInQueue);
            CurrentNumberOfMessagesInProducerQueues.Labels(generalLabelValues).Set(statistics.CurrentNumberOfMessagesInProducerQueues);
            CurrentSizeOfMessagesInProducerQueues.Labels(generalLabelValues).Set(statistics.CurrentSizeOfMessagesInProducerQueues);
            MaxMessagesAllowedOnProducerQueues.Labels(generalLabelValues).Set(statistics.MaxMessagesAllowedOnProducerQueues);
            MaxSizeOfMessagesAllowedOnProducerQueues.Labels(generalLabelValues).Set(statistics.MaxSizeOfMessagesAllowedOnProducerQueues);
            TotalNumberOfRequestSentToKafka.Labels(generalLabelValues).Set(statistics.TotalNumberOfRequestSentToKafka);
            TotalNumberOfBytesTransmittedToKafka.Labels(generalLabelValues).Set(statistics.TotalNumberOfBytesTransmittedToKafka);

            //PER BROKER (add Broker NodeId as label)

            foreach (var broker in statistics.Brokers)
            {
                var brokerLabelValues = (new string[] { statistics.ClientId.ToString(), broker.Value.NodeId.ToString() }).Concat(LabelValues).ToArray();

                NumberOfRequestAwaitingTransmission.Labels(brokerLabelValues).Set(broker.Value.NumberOfRequestAwaitingTransmission);
                NumberOfMessagesAwaitingTransmission.Labels(brokerLabelValues).Set(broker.Value.NumberOfMessagesAwaitingTransmission);
                NumberOfRequestInFlight.Labels(brokerLabelValues).Set(broker.Value.NumberOfRequestInFlight);
                NumberOfMessagesInFlight.Labels(brokerLabelValues).Set(broker.Value.NumberOfMessagesInFlight);
                TotalNumberOfRequestSent.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfRequestSent);
                TotalNumberOfBytesSent.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfBytesSent);
                TotalNumberOfTransmissionErrors.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfTransmissionErrors);
                TotalNumberOfRequestRetries.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfRequestRetries);
                TotalNumberOfRequestTimeout.Labels(brokerLabelValues).Set(broker.Value.TotalNumberOfRequestTimeout);
                NumberOfConnectionAttemps.Labels(brokerLabelValues).Set(broker.Value.NumberOfConnectionAttemps);
                NumberOfDisconnects.Labels(brokerLabelValues).Set(broker.Value.NumberOfDisconnects);
                InternalQueueProducerLatencyAverageMs.Labels(brokerLabelValues).Set(broker.Value.InternalQueueProducerLatency.Average);
                InternalRequestQueueLatencyAverageMs.Labels(brokerLabelValues).Set(broker.Value.InternalRequestQueueLatency.Average);
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

                    PartitionTotalNumberOfMessagesProduced.Labels(partitionLabelsValues).Set(partition.Value.TotalNumberOfMessagesProduced);
                    PartitionTotalNumberOfBytesProduced.Labels(partitionLabelsValues).Set(partition.Value.TotalNumberOfBytesProduced);
                    PartitionNumberOfMessagesInFlight.Labels(partitionLabelsValues).Set(partition.Value.NumberOfMessagesInFlight);
                    PartitionNextExpectedAckSequence.Labels(partitionLabelsValues).Set(partition.Value.NextExpectedAckSequence);
                    PartitionLastInternalMessageIdAcked.Labels(partitionLabelsValues).Set(partition.Value.LastInternalMessageIdAcked);
                }

            }

        }
    }
}
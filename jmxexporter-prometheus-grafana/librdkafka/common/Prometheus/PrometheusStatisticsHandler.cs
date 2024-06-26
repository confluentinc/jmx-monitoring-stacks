using System.Linq;
using common.Model;

namespace common.Prometheus
{

    /// <summary>
    /// 
    /// </summary>
    public abstract class PrometheusStatisticsHandler : IStatisticsHandler
    {

        protected string[] LabelNames;

        protected string[] LabelValues;

        internal string[] GeneralLevelLabelNames;
        internal string[] BrokerLevelLabelNames;
        internal string[] TopicLevelLabelNames;
        internal string[] PartitionLevelLabelNames;

        private static readonly string[] GeneralDefaultLabels = { "client_id" };
        private static readonly string[] BrokerDefaultLabels = { "client_id", "broker_id" };
        private static readonly string[] TopicDefaultLabels = { "client_id", "topic" };
        private static readonly string[] PartitionDefaultLabels = { "client_id", "broker_id", "topic", "partition_id" };


        public PrometheusStatisticsHandler(string[] labelNames = null, string[] labelValues = null)
        {
            this.LabelNames = labelNames ?? new string[] { };
            this.LabelValues = labelValues ?? new string[] { };

            GeneralLevelLabelNames = GeneralDefaultLabels.Concat(LabelNames).ToArray();
            BrokerLevelLabelNames = BrokerDefaultLabels.Concat(LabelNames).ToArray();
            TopicLevelLabelNames = TopicDefaultLabels.Concat(LabelNames).ToArray();
            PartitionLevelLabelNames = PartitionDefaultLabels.Concat(LabelNames).ToArray();

        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="statistics"></param>
        public abstract void Publish(Statistics statistics);
    }
}
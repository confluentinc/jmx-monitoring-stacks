using System;
using System.Drawing;
using common;
using common.Prometheus;
using Confluent.Kafka;
using Microsoft.Extensions.Configuration;

namespace consumer.Nodes
{
    public class SinkProcessorNode : AbstractProcessorNode<string, int>
    {
        private readonly ISerializer<string> _keySerializer;
        private readonly ISerializer<int> _valueSerializer;
        private IProducer<string,int> producer;
        private string outputTopic;

        public SinkProcessorNode(ISerializer<string> keySerializer, ISerializer<int> valueSerializer)
        {
            _keySerializer = keySerializer;
            _valueSerializer = valueSerializer;
        }
        
        public override void Init(IConfiguration configuration)
        {
            outputTopic = configuration.GetValue<string>("outputTopic");
            ProducerBuilder<string, int> builder = new(
                configuration.GetSection("producerConf").Get<ProducerConfig>());
            
            builder.SetErrorHandler((_, error) =>
            {
                Console.WriteLine($"An error ocurred producing the event: {error.Reason}");
                if (error.IsFatal) Environment.Exit(-1);
            });

            builder.HandleStatistics(new PrometheusProducerStatisticsHandler(new string[] { "application" }, new string[] { "test-producer-statistics" }));
            builder.SetKeySerializer(_keySerializer);
            builder.SetValueSerializer(_valueSerializer);

            producer = builder.Build();
        }

        protected override void Process(string key, int value)
        {
            producer.Produce(outputTopic, new Message<string, int>()
            {
                Key = key,
                Value = value
            }, delegate(DeliveryReport<string, int> report)
            {
                if (report.Error.IsError)
                {
                    Console.WriteLine($"Delivery Error: {report.Error.Reason}");
                }
                else
                {
                    Console.WriteLine($"Delivered message to {report.TopicPartitionOffset}");
                }
            });
        }

        public override void Close()
        {
            base.Close();
            producer.Flush();
            producer.Dispose();
        }
    }
}
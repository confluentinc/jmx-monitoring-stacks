using System.Collections.Generic;
using Confluent.Kafka;
using Microsoft.Extensions.Configuration;

namespace consumer.Nodes
{
    public interface IProcessorNode
    {
        IEnumerable<IProcessorNode> Next { get; }
        public void Init(IConfiguration configuration);
        public void Process(object key, object value);
        public void SetCurrentMetadata(string topic, Headers headers);
        public void Close();
    }
}
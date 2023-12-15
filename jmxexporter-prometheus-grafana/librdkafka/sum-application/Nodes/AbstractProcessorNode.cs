using System.Collections.Generic;
using Confluent.Kafka;
using Microsoft.Extensions.Configuration;

namespace consumer.Nodes
{
    public abstract class AbstractProcessorNode<K, V> : IProcessorNode
    {
        public AbstractProcessorNode(params IProcessorNode[] next)
        {
            Next = next;
        }

        public IEnumerable<IProcessorNode> Next { get; }
        public string Topic { get; private set; }
        public Headers Headers { get; private set; }

        public void Process(object key, object value)
        {
            Process((K) key, (V) value);
        }

        public void SetCurrentMetadata(string topic, Headers headers)
        {
            Topic = topic;
            Headers = headers;
        }

        protected void Forward<K1, V1>(K1 key, V1 value)
        {
            foreach (var n in Next)
                n.Process(key, value);
        }

        public abstract void Init(IConfiguration configuration);
        protected abstract void Process(K key, V value);

        public virtual void Close()
        {
            foreach(var n in Next)
                n.Close();
        }
    }
}
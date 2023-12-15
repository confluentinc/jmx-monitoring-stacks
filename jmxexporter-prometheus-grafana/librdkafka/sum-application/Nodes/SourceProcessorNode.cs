using System;
using Confluent.Kafka;
using Microsoft.Extensions.Configuration;

namespace consumer.Nodes
{
    public class SourceProcessorNode<K, V> : AbstractProcessorNode<byte[], byte[]>
        where K : class
        where V : class
    {
        private readonly IDeserializer<K> _keyDeserializer;
        private readonly IDeserializer<V> _valueDeserializer;

        public SourceProcessorNode(
            IDeserializer<K> keyDeserializer,
            IDeserializer<V> valueDeserializer,
            IProcessorNode countProcessor)
            : base(countProcessor)
        {
            _keyDeserializer = keyDeserializer;
            _valueDeserializer = valueDeserializer;
        }
        
        public override void Init(IConfiguration configuration)
        {
            // nothing
        }

        protected override void Process(byte[] key, byte[] value)
        {
            K newKey = _keyDeserializer.Deserialize(
                    new ReadOnlySpan<byte>(key), false,
                    new SerializationContext(MessageComponentType.Key, Topic, Headers));
               
            V newValue = _valueDeserializer.Deserialize(
                new ReadOnlySpan<byte>(value), false,
                new SerializationContext(MessageComponentType.Value, Topic, Headers));
            
            Forward(newKey, newValue);
        }
    }
}
using System.Threading;
using Confluent.Kafka;
using consumer.Nodes;

namespace consumer.Topology
{
    public class Topology
    {
        private readonly IProcessorNode sourceProcessorNode;
        private readonly CancellationTokenSource tokenSource;
        private readonly IConsumer<byte[], byte[]> consumer;
        private readonly string inputTopic;

        public Topology(IProcessorNode sourceProcessorNode, CancellationTokenSource tokenSource, IConsumer<byte[], byte[]> consumer, string inputTopic)
        {
            this.sourceProcessorNode = sourceProcessorNode;
            this.tokenSource = tokenSource;
            this.consumer = consumer;
            this.inputTopic = inputTopic;
        }

        public void Run()
        {
            consumer.Subscribe(inputTopic);
            while (!tokenSource.IsCancellationRequested)
            {
                var result = consumer.Consume(tokenSource.Token);
                if (result != null)
                {
                    sourceProcessorNode.SetCurrentMetadata(result.Topic, result.Message.Headers);
                    sourceProcessorNode.Process(result.Message.Key, result.Message.Value);
                    consumer.StoreOffset(result);
                }
            }
            consumer.Unsubscribe();
            consumer.Close();
            consumer.Dispose();
            sourceProcessorNode.Close();
        }
    }
}
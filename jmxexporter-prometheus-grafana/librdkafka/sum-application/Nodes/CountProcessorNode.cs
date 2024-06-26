using consumer.Store;
using io.confluent.demos.common.wiki;
using Microsoft.Extensions.Configuration;

namespace consumer.Nodes
{
    // No restoration phase has been implemented here, so the result count could be wrong in some times
    // No repartition, because the state store is global
    public class CountProcessorNode : AbstractProcessorNode<string, WikiEdit>
    {
        private KeyValueStore store;
        
        public CountProcessorNode(IProcessorNode sinkProcessor)
            : base(sinkProcessor)
        {
            
        }
        
        public override void Init(IConfiguration configuration)
        {
            store = new KeyValueStore(configuration.GetValue<string>("stateDir"));
        }

        protected override void Process(string key, WikiEdit value)
        {
            var existingCount = store.Read(value.id.ToString());
            existingCount += 1;
            store.Upsert(key, existingCount);
            Forward(key, existingCount);
        }

        public override void Close()
        {
            base.Close();
            store.Dispose();
        }
    }
}
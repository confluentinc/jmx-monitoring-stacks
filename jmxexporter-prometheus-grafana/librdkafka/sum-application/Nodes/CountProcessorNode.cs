using consumer.Store;
using Microsoft.Extensions.Configuration;

namespace consumer.Nodes
{
    // No restoration phase has been implemented here, so the result count could be wrong in some times
    // No repartition, because the state store is global
    public class CountProcessorNode : AbstractProcessorNode<string, string>
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

        protected override void Process(string key, string value)
        {
            var existingCount = store.Read(key);
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
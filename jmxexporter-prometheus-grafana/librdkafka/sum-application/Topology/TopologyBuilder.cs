using System;
using System.Threading;
using common;
using common.Prometheus;
using Confluent.Kafka;
using Confluent.Kafka.SyncOverAsync;
using Confluent.SchemaRegistry;
using Confluent.SchemaRegistry.Serdes;
using consumer.Nodes;
using io.confluent.demos.common.wiki;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

namespace consumer.Topology
{
    public static class TopologyBuilder
    {
        // [2023-12-15 16:12:37,519] INFO Principal = User:appSA is Denied Operation = Describe from host = 172.19.0.1 on resource = Group:LITERAL:count-wikipedia-page (kafka.authorizer.logger)
        // openssl pkcs12 -in /Users/slegouellec/Repos/cp-demo/scripts/security/appSA.keystore.p12 -nodes -passin pass:"confluent"
        
        public class DeserializerWikiEdit : IDeserializer<WikiEdit>
        {
            public WikiEdit Deserialize(ReadOnlySpan<byte> data, bool isNull, SerializationContext context)
            {
                return JsonConvert.DeserializeObject<WikiEdit>(Deserializers.Utf8.Deserialize(data, isNull, context)) ?? new WikiEdit();
            }
        }
        
        public static Topology BuildTopology(IConfiguration configuration)
        {
            CancellationTokenSource cancellationTokenSource = new();
            
            var consumerConf = configuration.GetSection("consumerConf").Get<ConsumerConfig>();
            consumerConf.GroupId = "count-wikipedia-page";
            consumerConf.AutoOffsetReset = AutoOffsetReset.Earliest;
            consumerConf.EnableAutoCommit = true;
            consumerConf.EnableAutoOffsetStore = false;
            consumerConf.SecurityProtocol = SecurityProtocol.Ssl;
            consumerConf.SslKeyLocation = "/Users/slegouellec/Repos/cp-demo/scripts/security/appSA.key";
            consumerConf.SslKeyPassword = "confluent";
            consumerConf.SslCaLocation = "/Users/slegouellec/Repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            consumerConf.SslCertificateLocation = "/Users/slegouellec/Repos/cp-demo/scripts/security/appSA-ca1-signed.crt";
            consumerConf.EnableSslCertificateVerification = true;

            var srConfig = configuration.GetSection("schemaRegistryConf").Get<SchemaRegistryConfig>();
            srConfig.SslCaLocation = "/Users/slegouellec/Repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            srConfig.SslKeystoreLocation = "/Users/slegouellec/Repos/cp-demo/scripts/security/appSA.keystore.p12";
            srConfig.SslKeystorePassword = "confluent";
            srConfig.BasicAuthCredentialsSource = AuthCredentialsSource.UserInfo;
            srConfig.BasicAuthUserInfo = "appSA:appSA";
            
            var client = new CachedSchemaRegistryClient(srConfig);
            var deserializer = new AvroDeserializer<WikiEdit>(client);

            SinkProcessorNode sinkProcessorNode =
                new(Serializers.Utf8, Serializers.Int32);
            CountProcessorNode countProcessorNode =
                new(sinkProcessorNode);
            SourceProcessorNode<String, WikiEdit> sourceProcessorNode = new(
                Deserializers.Utf8, deserializer.AsSyncOverAsync(), countProcessorNode);
                //Deserializers.Utf8, new DeserializerWikiEdit() , countProcessorNode);
            
            sourceProcessorNode.Init(configuration);
            countProcessorNode.Init(configuration);
            sinkProcessorNode.Init(configuration);
            
            ConsumerBuilder<byte[], byte[]> builder = new(consumerConf);
            builder.SetErrorHandler((_, error) =>
            {
                Console.WriteLine($"An error ocurred consuming the event: {error.Reason}");
                if (error.IsFatal) Environment.Exit(-1);
            });

            builder.HandleStatistics(new PrometheusConsumerStatisticsHandler(
                new string[] { "application" },
                new string[] { "test-consumer-statistics" }));
            builder.SetKeyDeserializer(Deserializers.ByteArray);
            builder.SetValueDeserializer(Deserializers.ByteArray);

            return new Topology(
                sourceProcessorNode,
                cancellationTokenSource,
                builder.Build(),
                configuration.GetValue<string>("inputTopic"));
        }
    }
}
using System;
using System.Threading;
using common;
using common.Prometheus;
using Confluent.Kafka;
using Confluent.Kafka.SyncOverAsync;
using Confluent.SchemaRegistry;
using Confluent.SchemaRegistry.Serdes;
using consumer.Deserializer;
using consumer.Nodes;
using io.confluent.demos.common.wiki;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

namespace consumer.Topology
{
    public static class TopologyBuilder
    {
        public static Topology BuildTopology(IConfiguration configuration)
        {
            CancellationTokenSource cancellationTokenSource = new();
            
            var consumerConf = configuration.GetSection("consumerConf").Get<ConsumerConfig>();
            consumerConf.GroupId = "count-wikipedia-page";
            consumerConf.AutoOffsetReset = AutoOffsetReset.Latest;
            consumerConf.AutoOffsetReset = AutoOffsetReset.Earliest;
            consumerConf.EnableAutoCommit = true;
            consumerConf.EnableAutoOffsetStore = false;
            consumerConf.SecurityProtocol = SecurityProtocol.Ssl;
            consumerConf.SslKeyLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA.key";
            consumerConf.SslKeyPassword = "confluent";
            consumerConf.SslCaLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            consumerConf.SslCertificateLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA-ca1-signed.crt";
            consumerConf.EnableSslCertificateVerification = true;

            var srConfig = configuration.GetSection("schemaRegistryConf").Get<SchemaRegistryConfig>();
            srConfig.SslCaLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            srConfig.SslKeystoreLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA.keystore.p12";
            srConfig.SslKeystorePassword = "confluent";
            srConfig.EnableSslCertificateVerification = false;
            srConfig.BasicAuthCredentialsSource = AuthCredentialsSource.UserInfo;
            srConfig.BasicAuthUserInfo = "appSA:appSA";
            
            var client = new CachedSchemaRegistryClient(srConfig);
            var deserializer = new AvroDeserializer<WikiEdit>(client);

            SinkProcessorNode sinkProcessorNode =
                new(Serializers.Utf8, Serializers.Int32);
            CountProcessorNode countProcessorNode =
                new(sinkProcessorNode);
            SourceProcessorNode<String, WikiEdit> sourceProcessorNode = new(
                Deserializers.Utf8, new DeserializerWikiEdit() , countProcessorNode);
            
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
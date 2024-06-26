using common;
using common.Prometheus;
using Confluent.Kafka;
using Confluent.SchemaRegistry;
using Confluent.SchemaRegistry.Serdes;
using consumer.Deserializer;
using consumer.Nodes;
using io.confluent.demos.common.wiki;
using Microsoft.Extensions.Configuration;

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
            consumerConf.EnableAutoCommit = true;
            consumerConf.EnableAutoOffsetStore = false;
            consumerConf.SecurityProtocol = SecurityProtocol.Ssl;
            //consumerConf.SslKeyLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA.key";
            //consumerConf.SslKeyPassword = "confluent";
            //consumerConf.SslCaLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            //consumerConf.SslCertificateLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA-ca1-signed.crt";
            //consumerConf.EnableSslCertificateVerification = true;

            var srConfig = configuration.GetSection("schemaRegistryConf").Get<SchemaRegistryConfig>();
            // srConfig.SslCaLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            // srConfig.SslKeystoreLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA.keystore.p12";
            // srConfig.SslKeystorePassword = "confluent";
            // srConfig.EnableSslCertificateVerification = false;
            srConfig.BasicAuthCredentialsSource = AuthCredentialsSource.UserInfo;
            //srConfig.BasicAuthUserInfo = "appSA:appSA";
            
            var producerConfig = configuration.GetSection("producerConf").Get<ProducerConfig>();
            producerConfig.SecurityProtocol = SecurityProtocol.Ssl;
            //producerConfig.SslKeyLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA.key";
            //producerConfig.SslKeyPassword = "confluent";
            //producerConfig.SslCaLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/snakeoil-ca-1.crt";
            //producerConfig.SslCertificateLocation = "/Users/sylvainlegouellec/repos/cp-demo/scripts/security/appSA-ca1-signed.crt";
            //producerConfig.EnableSslCertificateVerification = true;
            
            var client = new CachedSchemaRegistryClient(srConfig);
            var deserializer = new AvroDeserializer<WikiEdit>(client);

            SinkProcessorNode sinkProcessorNode =
                new(Serializers.Utf8, Serializers.Int32, producerConfig);
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

            var appID = configuration.GetValue<string>("applicationId");
            builder.HandleStatistics(new PrometheusConsumerStatisticsHandler(
                new string[] { "application", "librdkafka_type" },
                new string[] { appID, "consumer" }));
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
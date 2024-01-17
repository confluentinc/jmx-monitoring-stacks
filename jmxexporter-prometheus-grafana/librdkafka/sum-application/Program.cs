using System;
using System.IO;
using consumer.Topology;
using Microsoft.Extensions.Configuration;
using Prometheus;

namespace consumer
{
    class Program
    {
        public static void Main(string[] args)
        {
            var configuration = GetConfiguration(args);
            try
            {
                MetricServer metricServer = new(7071);
                metricServer.Start();
                var topology = TopologyBuilder.BuildTopology(configuration);
                topology.Run();
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error happening ...{e}");
            }
        }

        private static IConfiguration GetConfiguration(string[] args)
        {
            var configurationBuilder = new ConfigurationBuilder();
            configurationBuilder.AddJsonFile("config.json", optional: true, reloadOnChange: true);
            configurationBuilder.AddEnvironmentVariables();
            configurationBuilder.AddCommandLine(args);
            return configurationBuilder.Build();
        }
    }
}
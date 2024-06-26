using System;
using System.IO;
using FASTER.core;

namespace consumer.Store
{
    public class KeyValueStore : IDisposable
    {
        public KeyValueStore(string pathDir)
        {
            Path = pathDir;
            ObjectLog = Devices.CreateLogDevice(Path + "_obj.log");
            Log = Devices.CreateLogDevice(Path + ".log");
            Store = new FasterKV<string, int>(
                size: 1L << 20, // 1M cache lines of 64 bytes each = 64MB hash table
                logSettings: new LogSettings { LogDevice = Log, ObjectLogDevice = ObjectLog }
            );
            var funcs = new SimpleFunctions<string, int>((a, b) => a + b); // function used for read-modify-write (RMW).
            Session = Store.NewSession(funcs);
        }
        
        string Path { get; set; }
        IDevice Log { get; set; }
        IDevice ObjectLog { get; set; }
        FasterKV<string, int> Store { get; set; }
        ClientSession<string, int, int, int, Empty, IFunctions<string, int, int, int, Empty>> Session { get; set; }

        public void Dispose()
        {
            Session.Dispose();
            Store.Dispose();
            Log.Dispose();
            ObjectLog.Dispose();
            File.Delete(Path);
        }

        public int Read(string key)
        {
            var (_, count) = Session.Read(key);
            return count;
        }

        public void Upsert(string key, int count)
        {
            Session.Upsert(key, count);
        }
    }
}
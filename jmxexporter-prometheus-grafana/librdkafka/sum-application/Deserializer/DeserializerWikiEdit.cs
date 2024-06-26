using System.Net;
using Avro.Generic;
using Avro.IO;
using Confluent.Kafka;
using io.confluent.demos.common.wiki;

namespace consumer.Deserializer;


public class DeserializerWikiEdit : IDeserializer<WikiEdit>
{
    public WikiEdit Deserialize(ReadOnlySpan<byte> data, bool isNull, SerializationContext context)
    {
        if (isNull) return null;
        
        var array = data.ToArray();
        using (var stream = new MemoryStream(array))
        using (var reader = new BinaryReader(stream))
        {
            var magicByte = reader.ReadByte();
            var writeId = IPAddress.NetworkToHostOrder(reader.ReadInt32());
            DatumReader<GenericRecord?> datumReader = new GenericReader<GenericRecord?>(WikiEdit._SCHEMA, WikiEdit._SCHEMA);
            var record = datumReader.Read(default(GenericRecord), new BinaryDecoder(stream));
            WikiEdit wikiEdit = new WikiEdit();
            
            wikiEdit.bot = (bool?)record.GetValue(0);
            wikiEdit.comment = (string)record.GetValue(1);
            wikiEdit.id = (long?)record.GetValue(2);
            
            return wikiEdit;
        }
    }
}
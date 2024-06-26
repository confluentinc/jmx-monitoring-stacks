using common.Model;

namespace common
{
    /// <summary>
    /// 
    /// </summary>
    public interface IStatisticsHandler
    {
        /// <summary>
        /// 
        /// </summary>
        /// <param name="statistics"></param>
        void Publish(Statistics statistics);
    } 
}
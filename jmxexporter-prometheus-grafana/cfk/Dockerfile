FROM confluentinc/cp-server:7.8.0
USER root
RUN rm -f /usr/share/java/cp-base-new/jmx_prometheus_javaagent*
COPY jmx_prometheus_javaagent-1.1.0.jar /usr/share/java/cp-base-new/
RUN chown --reference=/usr/share/java/cp-base-new/disk-usage-agent-7.8.0.jar /usr/share/java/cp-base-new/jmx_prometheus_javaagent-1.1.0.jar
USER appuser

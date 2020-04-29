#!/bin/bash

. ../helper/configure_cp_demo.sh

echo -e "Stop cp-demo in $CP_DEMO_HOME and monitoring stack in $MONITORING_STACK"
(cd $CP_DEMO_HOME && ./scripts/stop.sh)

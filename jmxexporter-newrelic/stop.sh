#!/bin/bash

########################################
# Stop cp-demo
########################################

export MONITORING_STACK="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

. $MONITORING_STACK/../utils/setup_cp_demo.sh

echo -e "Stop cp-demo in $CP_DEMO_HOME and monitoring stack in $MONITORING_STACK"
(cd $CP_DEMO_HOME && ./scripts/stop.sh)

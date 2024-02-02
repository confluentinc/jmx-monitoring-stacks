#!/usr/bin/env bash

# Teardown local k8s cluster with kind
kind delete cluster
rm -fr dashboards
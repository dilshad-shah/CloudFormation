#!/usr/bin/env groovy

@Library('pipeline-utils') _

buildPipeline([
    slack: [
      [ branches: ['master'], channels: ['nse-cdk-builds'] ],
      [ branches: ['.*'], channels: ['_owner_'] ]
    ]
])

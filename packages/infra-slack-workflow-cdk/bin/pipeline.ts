#!/usr/bin/env node
import 'source-map-support/register';
import { generateTags } from '@cvent/aws-cdk-core';
import { getAccountId } from '@cvent/environments';
import { CdkPipeline, getProjectGroupId, getEnvironmentId } from '@cvent/octopusdeploy-cdk';
import { App, Stack } from '@aws-cdk/core';

const app = new App();
const stack = new Stack(app, 'infra-slack-workflow-pipeline', {
  env: {
    account: getAccountId('cvent-management'),
    region: 'us-east-1'
  }
});
generateTags(stack, {
  product: 'shared',
  businessUnit: 'shared',
  platform: 'shared',
  env: 'production'
});

new CdkPipeline(stack, 'Pipeline', {
  projectGroupId: getProjectGroupId('6 - Shared Assets'),
  packageName: 'cvent.infra-slack-workflow-cdk',
  name: 'Infra Slack Workflow',
  slackChannel: 'nse-cdk-builds',
  queueName: 'crossteam',
  phases: [
    {
      Name: 'Development',
      AutomaticDeploymentTargets: [
        // Used for Workflow testing
        getEnvironmentId('cvent-internaltools-dev')
      ]
    },
    {
      Name: 'Production',
      OptionalDeploymentTargets: [getEnvironmentId('cvent-internaltools-prod')]
    }
  ]
});

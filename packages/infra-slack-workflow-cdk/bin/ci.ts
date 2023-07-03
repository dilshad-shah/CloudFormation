#!/usr/bin/env node
import 'source-map-support/register';
import { ciVersion } from '@cvent/aws-cdk-core';
import { getAccountId } from '@cvent/environments';
import { Application } from '../lib/application';

new Application('infra-slack-slack-workflow', {
  awsEnvironment: {
    account: getAccountId('cvent-sandbox'),
    region: 'us-east-1'
  },
  cventEnvironment: 'ci',
  cventSubEnv: 'beach',
  version: ciVersion(),
  tableName: 'infra-slack-workflow' + ciVersion(),
  lambdaEnvJira: '/infra-slack-workflow-testing/jira-token',
  lambdaEnvPd: '/infra-slack-workflow-testing/pd-token',
  lambdaEnvSlack: '/infra-slack-workflow-testing/slack-token',
  lambdaEnvDBTable: 'infra-slack-workflow' + ciVersion(),
  lambdaEnvPdSrvId: '/infra-slack-workflow-testing/pd-srv-id'
});

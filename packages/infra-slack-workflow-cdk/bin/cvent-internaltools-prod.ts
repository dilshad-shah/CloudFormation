#!/usr/bin/env node
import 'source-map-support/register';
import { getAccountId } from '@cvent/environments';
import { Application } from '../lib/application';

new Application('infra-slack-workflow', {
  awsEnvironment: {
    account: getAccountId('cvent-internaltools-prod'),
    region: 'us-east-2'
  },
  cventEnvironment: 'production',
  cventSubEnv: 'production',
  tableName: 'infra-slack-workflow',
  lambdaEnvJira: '/infra-slack-workflow/jira-token',
  lambdaEnvPdSrvId: '/infra-slack-workflow/pd-srv-id',
  lambdaEnvPd: '/infra-slack-workflow/pd-token',
  lambdaEnvSlack: '/infra-slack-workflow/slack-token',
  lambdaEnvDBTable: 'infra-slack-workflow'
});

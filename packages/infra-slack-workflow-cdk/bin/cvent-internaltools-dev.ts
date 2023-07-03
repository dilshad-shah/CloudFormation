#!/usr/bin/env node
import 'source-map-support/register';
import { getAccountId } from '@cvent/environments';
import { Application } from '../lib/application';

new Application('infra-slack-workflow', {
  awsEnvironment: {
    account: getAccountId('cvent-internaltools-dev'),
    region: 'us-east-2'
  },
  cventEnvironment: 'development',
  cventSubEnv: 'development',
  tableName: 'infra-slack-workflow',
  lambdaEnvJira: '/infra-slack-workflow/jira-token',
  lambdaEnvPd: '/infra-slack-workflow/pd-token',
  lambdaEnvSlack: '/infra-slack-workflow/slack-token',
  lambdaEnvDBTable: 'infra-slack-workflow',
  lambdaEnvPdSrvId: '/infra-slack-workflow/pd-srv-id'
});

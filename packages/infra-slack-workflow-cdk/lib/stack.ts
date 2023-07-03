import { Construct, Stack, StackProps, CfnOutput, Duration } from '@aws-cdk/core';
import { createDnsRecordAndCert } from '@cvent/aws-cdk-core';
import { EndpointType, MethodLoggingLevel, RestApi, LambdaIntegration } from '@aws-cdk/aws-apigateway';
import { Function, Runtime, Code, IFunction } from '@aws-cdk/aws-lambda';
import { PolicyStatement } from '@aws-cdk/aws-iam';
import path = require('path');

export interface InfraSlackWorkflowStackProps extends StackProps {
  lambdaEnvJira?: string;
  lambdaEnvPd?: string;
  lambdaEnvSlack?: string;
  lambdaEnvDBTable?: string;
  lambdaEnvPdSrvId?: string;
}

export class InfraSlackWorkflowStack extends Stack {
  public readonly InfraSlackWorkflowApi: RestApi;
  public readonly infraSlackWorkflowLambda: IFunction;

  constructor(scope: Construct, id: string, props?: InfraSlackWorkflowStackProps) {
    super(scope, id, props);
    const runtime = Runtime.PYTHON_3_9;
    const memorySize = 3008;
    const timeout = Duration.seconds(300);
    const retryAttempts = 0;

    const InfraSlackWorkflowLambda = new Function(this, 'InfraSlackWorkflowLambda', {
      handler: 'index.handler',
      retryAttempts,
      timeout,
      memorySize,
      runtime,
      code: Code.fromAsset(path.dirname(require.resolve('@cvent/infra-slack-workflow-lambda'))),
      environment: {
        JIRA_TKN: props.lambdaEnvJira,
        PD_TKN: props.lambdaEnvPd,
        SLACK_TKN: props.lambdaEnvSlack,
        DB_TABLE: props.lambdaEnvDBTable,
        PD_SRV_ID: props.lambdaEnvPdSrvId
      }
    });
    InfraSlackWorkflowLambda.addToRolePolicy(
      new PolicyStatement({
        actions: ['ssm:GetParameter', 'ssm:GetParameters'],
        resources: [
          `arn:aws:ssm:${this.region}:${this.account}:parameter${props.lambdaEnvJira}`,
          `arn:aws:ssm:${this.region}:${this.account}:parameter${props.lambdaEnvPd}`,
          `arn:aws:ssm:${this.region}:${this.account}:parameter${props.lambdaEnvSlack}`,
          `arn:aws:ssm:${this.region}:${this.account}:parameter${props.lambdaEnvPdSrvId}`
        ]
      })
    );
    const InfraSlackWorkflowApi = new RestApi(this, 'infra-slack-workflow-api', {
      restApiName: 'infra-slack-workflow-api',
      description: 'API for the InfraWorkflow App',
      endpointTypes: [EndpointType.REGIONAL],
      deployOptions: {
        loggingLevel: MethodLoggingLevel.INFO,
        metricsEnabled: true,
        tracingEnabled: true
      },
      cloudWatchRole: false
    });
    this.infraSlackWorkflowLambda = InfraSlackWorkflowLambda;
    const { record } = createDnsRecordAndCert(InfraSlackWorkflowApi, InfraSlackWorkflowStack.name, true, false, false);
    new CfnOutput(this, 'LoadBalancerDNS', {
      value: record
    });
    const eventhandler = InfraSlackWorkflowApi.root.addResource('event-handler');
    eventhandler.addMethod('POST', new LambdaIntegration(InfraSlackWorkflowLambda));
  }
}

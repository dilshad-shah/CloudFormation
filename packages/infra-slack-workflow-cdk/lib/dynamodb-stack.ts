import { Construct, RemovalPolicy, Stack, StackProps } from '@aws-cdk/core';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import { IFunction } from '@aws-cdk/aws-lambda';
import { addLintIgnore } from '@cvent/aws-cdk-core';

export interface InfraSlackWorkflowDynamoStackProps extends StackProps {
  tableName: string;
  partitionKey: string;
  infraSlackWorkflowLambda: IFunction;
  cventEnvironment: string;
}

export class InfraSlackWorkflowDynamoStack extends Stack {
  constructor(scope: Construct, id: string, props?: InfraSlackWorkflowDynamoStackProps) {
    super(scope, id, props);

    const table = new dynamodb.Table(this, 'infra-slack-workflow-dynamodb', {
      partitionKey: { name: 'threadId', type: dynamodb.AttributeType.STRING },
      tableName: props.tableName,
      removalPolicy: RemovalPolicy.DESTROY
    });

    addLintIgnore(table, ['E9020', 'E9019', 'E9022']);

    table.grantReadWriteData(props.infraSlackWorkflowLambda);
  }
}

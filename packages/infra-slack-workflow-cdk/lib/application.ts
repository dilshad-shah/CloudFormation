import { InfraSlackWorkflowStack } from './stack';
import { InfraSlackWorkflowDynamoStack } from './dynamodb-stack';
import { ephemeralize, generateTags, stackName } from '@cvent/aws-cdk-core';
import { Env, SubEnv } from '@cvent/environments';
import { App, Environment } from '@aws-cdk/core';

export interface ApplicationProps {
  /** used primarily for CI stacks to give them a unique name based on package version */
  readonly version?: string;

  /** AWS account and region */
  readonly awsEnvironment: Environment;

  /** name of the hogan environment (e.g. pr50) */
  readonly cventEnvironment: string;

  /** name of the Cvent Sub-environment (e.g. production) */
  readonly cventSubEnv?: SubEnv;

  readonly tableName?: string;
  readonly partitionKey?: string;
  // readonly infraWorkflowLambda?: IFunction;

  readonly lambdaEnvJira?: string;
  readonly lambdaEnvPd?: string;
  readonly lambdaEnvSlack?: string;
  readonly lambdaEnvDBTable?: string;
  readonly lambdaEnvPdSrvId?: string;
}

export class Application extends App {
  // Exposed for testing purposes
  public readonly stack: InfraSlackWorkflowStack;
  public readonly dynamodbStack: InfraSlackWorkflowDynamoStack;

  constructor(id: string, props: ApplicationProps) {
    super();

    this.stack = new InfraSlackWorkflowStack(this, stackName(id, props.version), {
      env: props.awsEnvironment,
      lambdaEnvJira: props.lambdaEnvJira,
      lambdaEnvPd: props.lambdaEnvPd,
      lambdaEnvSlack: props.lambdaEnvSlack,
      lambdaEnvDBTable: props.lambdaEnvDBTable,
      lambdaEnvPdSrvId: props.lambdaEnvPdSrvId
    });

    generateTags(this.stack, {
      product: 'shared',
      businessUnit: 'shared',
      platform: 'shared',
      env: props.cventEnvironment as Env,
      subEnv: props.cventSubEnv
    });

    if (props.version !== undefined) {
      this.dynamodbStack = new InfraSlackWorkflowDynamoStack(this, stackName(id + '-dynamodb-' + props.version), {
        env: props.awsEnvironment,
        tableName: props.tableName,
        partitionKey: props.partitionKey,
        infraSlackWorkflowLambda: this.stack.infraSlackWorkflowLambda,
        cventEnvironment: props.cventEnvironment
      });
    } else {
      this.dynamodbStack = new InfraSlackWorkflowDynamoStack(this, stackName(id + '-dynamodb'), {
        env: props.awsEnvironment,
        tableName: props.tableName,
        partitionKey: props.partitionKey,
        infraSlackWorkflowLambda: this.stack.infraSlackWorkflowLambda,
        cventEnvironment: props.cventEnvironment
      });
    }

    generateTags(this.dynamodbStack, {
      product: 'shared',
      businessUnit: 'shared',
      platform: 'shared',
      env: props.cventEnvironment as Env,
      subEnv: props.cventSubEnv
    });

    if (props.cventEnvironment === 'ci') {
      ephemeralize(this.stack);
      ephemeralize(this.dynamodbStack);
    }
  }
}

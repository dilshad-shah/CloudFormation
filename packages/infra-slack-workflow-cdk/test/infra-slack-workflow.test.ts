import '@aws-cdk/assert/jest';
import { SynthUtils } from '@aws-cdk/assert';
import { Application } from '../lib/application';

describe('application', (): void => {
  test('with defaults', (): void => {
    const app = new Application('infra-slack-workflow', {
      awsEnvironment: { account: '572724207364', region: 'us-east-1' },
      cventEnvironment: 'beach',
      cventSubEnv: 'beach'
    });

    expect(SynthUtils.toCloudFormation(app.stack)).toMatchSnapshot();
  });

  test('with version', (): void => {
    const app = new Application('infra-slack-workflow', {
      awsEnvironment: { account: '572724207364', region: 'us-east-1' },
      cventEnvironment: 'beach',
      cventSubEnv: 'beach',
      version: 'version'
    });

    expect(SynthUtils.toCloudFormation(app.stack)).toMatchSnapshot();
  });
});

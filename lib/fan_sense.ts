import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { BucketEncryption } from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as custom from 'aws-cdk-lib/custom-resources';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { AWS_ACCOUNT_ID, AWS_REGION } from './constants';

export class FanSenseStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const redditDocumentsBucket = new s3.Bucket(this, 'RedditDocuments', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      bucketName: `reddit-documents-${AWS_REGION}`,
      encryption: BucketEncryption.S3_MANAGED,
    });

    const comprehendOutputBucket = new s3.Bucket(this, 'ComprehendReports', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      bucketName: `comprehend-reports-${AWS_REGION}`,
      encryption: BucketEncryption.S3_MANAGED,
    });

    const redditApiLambda = new lambda.Function(this, 'RedditApiLambda', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'scrape_reddit.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_13.bundlingImage,
          command: [
            'bash', '-c',
            [
              'pip install -r requirements.txt -t /asset-output',
              'cp -r . /asset-output',
            ].join(' && '),
          ],
        },
      }),
      timeout: cdk.Duration.minutes(15),
      memorySize: 2048,
      environment: {
        DOCUMENT_BUCKET_NAME: redditDocumentsBucket.bucketName,
        AWS_ACCOUNT_ID: AWS_ACCOUNT_ID,
      },
    });

      const boxLambda = new lambda.Function(this, 'BoxLambda', {
          runtime: lambda.Runtime.PYTHON_3_13,
          handler: 'box.handler',
          code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
              bundling: {
                  image: lambda.Runtime.PYTHON_3_13.bundlingImage,
                  command: [
                      'bash', '-c',
                      [
                          'pip install -r requirements.txt -t /asset-output',
                          'cp -r . /asset-output',
                      ].join(' && '),
                  ],
              },
          }),
          environment: {
              OUTPUT_BUCKET_NAME: comprehendOutputBucket.bucketName,
              AWS_ACCOUNT_ID: AWS_ACCOUNT_ID,
          },
      });

      comprehendOutputBucket.grantReadWrite(boxLambda);

      comprehendOutputBucket.addEventNotification(
          s3.EventType.OBJECT_CREATED_PUT,
          new s3n.LambdaDestination(boxLambda),
          { suffix: '.gz' } // only files in "uploads/" ending in ".gz"
      );

    const comprehendServiceRole = new iam.Role(this, 'ComprehendServiceRole', {
      assumedBy: new iam.ServicePrincipal('comprehend.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
      ],
    });

    const comprehendSchedulerLambda = new lambda.Function(
      this,
      'ComprehendSchedulerLambda',
      {
        runtime: lambda.Runtime.PYTHON_3_13,
        handler: 'comprehend_scheduler.handler',
        code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
          bundling: {
            image: lambda.Runtime.PYTHON_3_13.bundlingImage,
            command: [
              'bash', '-c',
              [
                'pip install -r requirements.txt -t /asset-output',
                'cp -r . /asset-output',
              ].join(' && '),
            ],
          },
        }),
        environment: {
          DOCUMENT_BUCKET_NAME: redditDocumentsBucket.bucketName,
          OUTPUT_BUCKET_NAME: comprehendOutputBucket.bucketName,
          COMPREHEND_ROLE_ARN: comprehendServiceRole.roleArn,
          AWS_ACCOUNT_ID: AWS_ACCOUNT_ID,
        },
      }
    );

    comprehendSchedulerLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          'comprehend:StartEntitiesDetectionJob',
          'comprehend:DescribeEntitiesDetectionJob',
          'comprehend:ListEntitiesDetectionJobs',
          'iam:PassRole',
        ],
        resources: ['*'],
      })
    );

    redditDocumentsBucket.grantReadWrite(comprehendSchedulerLambda);
    redditDocumentsBucket.grantReadWrite(redditApiLambda);
    redditDocumentsBucket.grantReadWrite(comprehendServiceRole);
    comprehendOutputBucket.grantReadWrite(comprehendServiceRole);

    const rankingsTable = new dynamodb.Table(this, 'FanSenseRankingsTable', {
      partitionKey: { name: 'team', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      tableName: `fansense_rankings`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const bedrockSummaryLambda = new lambda.Function(this, 'bedrockSummaryLambda', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'bedrock_summary.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
        bundling: {
          image: lambda.Runtime.PYTHON_3_13.bundlingImage,
          command: [
            'bash', '-c',
            [
              'pip install -r requirements.txt -t /asset-output',
              'cp -r . /asset-output',
            ].join(' && '),
          ],
        },
      }),
      environment: {
        DOCUMENT_BUCKET_NAME: redditDocumentsBucket.bucketName,
        RANKINGS_TABLE_NAME: rankingsTable.tableName
      },
    });

    redditDocumentsBucket.grantRead(bedrockSummaryLambda);
    rankingsTable.grantReadData(bedrockSummaryLambda);

    bedrockSummaryLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'],
        resources: ['*'],
      })
    );

const kbSyncLambda = new lambda.Function(this, 'KBSyncLambda', {
  runtime: lambda.Runtime.PYTHON_3_13,
  handler: 'kb_sync.handler',
    code: lambda.Code.fromAsset(path.join(__dirname, '../lambda'), {
        bundling: {
            image: lambda.Runtime.PYTHON_3_13.bundlingImage,
            command: [
                'bash', '-c',
                [
                    'pip install -r requirements.txt -t /asset-output',
                    'cp -r . /asset-output',
                ].join(' && '),
            ],
        },
    }),
  environment: {
    KB_ID: process.env.KB_ID ?? '',
    DATA_SOURCE_ID: process.env.DATA_SOURCE_ID ?? '',
  },
});


    kbSyncLambda.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:*'],
        resources: ['*'],
      })
    );

    redditDocumentsBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(kbSyncLambda)
    );
  }
}

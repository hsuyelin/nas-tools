# AWS Lambda Bolt Python Examples

This directory contains two example apps. Both respond to the Slash Command
`/hello-bolt-python-lambda` and both respond to app at-mentions.

The "Lazy Lambda Listener" example is the simpler application and it leverages
AWS Lambda and AWS Lambda Function URL to execute the Bolt app logic in Lambda and
expose the application HTTP routes to the internet via Lambda URL. The "OAuth
Lambda Listener" example additionally includes OAuth flow handling routes and uses
AWS S3 to store workspace installation credentials and OAuth flow state
variables, enabling your app to be installed by anyone.

Instructions on how to set up and deploy each example are provided below.

## Lazy Lambda Listener Example Bolt App

1. You need an AWS account and your AWS credentials set up on your machine.
2. Make sure you have an AWS IAM Role defined with the needed permissions for
   your Lambda function powering your Slack app:
  - Head to the AWS IAM section of AWS Console
  - Click Roles from the menu
  - Click the Create Role button
  - Under "Select type of trusted entity", choose "AWS service"
  - Under "Choose a use case", select "Common use cases: Lambda"
  - Click "Next: Permissions"
  - Under "Attach permission policies", enter "lambda" in the Filter input
  - Check the "AWSLambdaBasicExecutionRole", "AWSLambdaExecute" and "AWSLambdaRole" policies
  - Click "Next: tags"
  - Click "Next: review"
  - Enter `bolt_python_lambda_invocation` as the Role name. You can change this
      if you want, but then make sure to update the role name in
      `lazy_aws_lambda_config.yaml`
  - Optionally enter a description for the role, such as "Bolt Python basic
      role"
3. Ensure you have created an app on api.slack.com/apps as per the [Getting
   Started Guide](https://slack.dev/bolt-python/tutorial/getting-started).
   Ensure you have installed it to a workspace.
4. Ensure you have exported your Slack Bot Token and Slack Signing Secret for your
   apps as the environment variables `SLACK_BOT_TOKEN` and
   `SLACK_SIGNING_SECRET`, respectively, as per the [Getting
   Started Guide](https://slack.dev/bolt-python/tutorial/getting-started).
5. You may want to create a dedicated virtual environment for this example app, as
   per the "Setting up your project" section of the [Getting
   Started Guide](https://slack.dev/bolt-python/tutorial/getting-started).
6. Let's deploy the Lambda! Run `./deploy_lazy.sh`. By default it deploys to the
   us-east-1 region in AWS - you can change this at the top of `lazy_aws_lambda_config.yaml` if you wish.
7. Load up AWS Lambda inside the AWS Console - make sure you are in the correct
   region that you deployed your app to. You should see a `bolt_py_function`
   Lambda there.
8. While your Lambda exists, it is not accessible to the internet, so Slack
   cannot send events happening in your Slack workspace to your Lambda. Let's
   fix that by adding an AWS Lambda Function URL to your Lambda so that your
   Lambda can accept HTTP requests:
  - Click on your `bolt_py_function` Lambda
  - In the Function Overview click "Configuration"
  - On the left side, click "Function URL"
  - Click "Create function URL"
  - Choose auth type "NONE"
  - Click "Save"
9. Congrats! Your Slack app is now accessible to the public. On the right side of
   your `bolt_py_function` Function Overview you should see your Lambda Function URL.
10. Copy this URL to your clipboard.
11. We will now inform Slack that this example app can accept Slash Commands.
  - Back on api.slack.com/apps, select your app and choose Slash Commands from the left menu.
  - Click Create New Command
  - By default, the `lazy_aws_lambda.py` function has logic for a
      `/hello-bolt-python-lambda` command. Enter `/hello-bolt-python-lambda` as
      the Command.
  - Under Request URL, paste in the previously-copied Lambda Function URL.
  - Click Save
12. Test it out! Back in your Slack workspace, try typing
    `/hello-bolt-python-lambda hello`.
13. If you have issues, here are some debugging options:
  - Check the Monitor tab under your Lambda. Did the Lambda get invoked? Did it
      respond with an error? Investigate the graphs to see how your Lambda is
      behaving.
  - From this same Monitor tab, you can also click "View Logs in CloudWatch" to
      see the execution logs for your Lambda. This can be helpful to see what
      errors are being raised.

## OAuth Lambda Listener Example Bolt App

### Setup your AWS Account + Credentials
You need an AWS account and your AWS credentials set up on your machine.

Once you’ve done that you should have access to AWS Console, which is what we’ll use for the rest of this tutorial.

### Create S3 Buckets to store Installations and State

1. Start by creating two S3 buckets:
    1. One to store installation credentials for each Slack workspace that installs your app.
    2. One to store state variables during the OAuth flow.
2. Head over to **Amazon S3** in the AWS Console
3. Give your bucket a name, region, and set access controls. If you’re doing this for the first time, it’s easiest to keep the defaults and edit them later as necessary. We'll be using the names:
    1. slack-installations-s3
    2. slack-state-store-s3
4. After your buckets are created, in each bucket’s page head over to “Properties” and save the Amazon Resource Name (ARN). It should look something like `arn:aws:s3:::slack-installations-s3`.

### Create a Policy to Enable Actions on S3 Buckets
Now let's create a policy that will allow the holder of the policy to take actions in your S3 buckets.

1. Head over to Identity and Access Management (IAM) in the AWS Console via Search Bar
2. Head to **Access Management > Policies** and select “Create Policy”
3. Click the JSON tab and copy this in:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:Put*",
                "s3:Delete*",
                "s3-object-lambda:*"
            ],
            "Resource": [
                "<your-first-bucket-arn>/*",   // don't forget the `/*`
                "<your-second-bucket-arn>/*"
            ]
        }
    ]
}
```
4. Edit “Resource” to include the ARNs of the two buckets you created in the earlier step. These need to exactly match the ARNS you copied earlier and end with a `/*`
5. Hit "Next:Tags" and "Next:Review"
6. Review policy
    1. Name your policy something memorable enough that you won’t have forgotten it 5 minutes from now when we’ll need to look it up from a list. (e.g. AmazonS3-FullAccess-SlackBuckets)
    2. Review the summary, and hit "Create Policy". Once the policy is created you should be redirected to the Policies page and see your new policy show up as Customer managed policy.

### Setup an AWS IAM Role with Policies for Executing Your Lambda
Let’s create a user role that will use the custom policy we created as well as other policies to let us execute our lambda, write output logs to CloudWatch.

1. Head to the **Identity and Access Management (IAM)** section of AWS Console
2. Select **Access Management > Roles** from the menu
3. Click "Create Role"
4. Step 1 - Select trusted entity
    1. Under "Select type of trusted entity", choose "AWS service"
    2. Under "Choose a use case", select "Common use cases: Lambda"
    3. Click "Next: Permissions"
5. Step 2 - Add permissions
    1. Add the following policies to the role we’re creating that will allow the user with the role permission to execute Lambda, make changes to their S3 Buckets, log output to CloudWatch
        1. `AWSLambdaExecute`
        2. `AWSLambdaBasicExecutionRole`
        3. `AWSLambdaRole`
        4. `<NameOfS3PolicyYouCreatedEarlier>`
6. Step 3 - Name, review, create
    1. Enter `bolt_python_s3_storage` as your role name. To use a different name, make sure to update the role name in `aws_lambda_oauth_config.yaml`
    2. Optionally enter a description for the role, such as "Bolt Python with S3 access role”
    3. "Create Role"

### Create Slack App and Load your Lambda to AWS
Ensure you have created an app on [api.slack.com/apps](https://api.slack.com/apps) as per the [Getting Started Guide](https://slack.dev/bolt-python/tutorial/getting-started). You do not need to ensure you have installed it to a workspace, as the OAuth flow will provide your app the ability to be installed by anyone.

1. Remember those S3 buckets we made? You will need the names of these buckets again in the next step.
2. You need many environment variables exported! Specifically the following from api.slack.com/apps

```bash
SLACK_SIGNING_SECRET=  # Signing Secret from Basic Information page
SLACK_CLIENT_ID= # Client ID from Basic Information page
SLACK_CLIENT_SECRET # Client Secret from Basic Information page
SLACK_SCOPES= "app_mentions:read,chat:write"
SLACK_INSTALLATION_S3_BUCKET_NAME: # The name of installations bucket
SLACK_STATE_S3_BUCKET_NAME: # The name of the state store bucket
export
```
6. Let's deploy the Lambda! Run `./deploy_oauth.sh`. By default it deploys to the us-east-1 region in AWS - you can customize this in `aws_lambda_oauth_config.yaml`.
7. Load up AWS Lambda inside the AWS Console - make sure you are in the correct region that you deployed your app to. You should see a `bolt_py_oauth_function` Lambda there.

### Set up AWS Lambda Function URL
Your Lambda exists, but it is not accessible to the internet, so Slack cannot yet send events happening in your Slack workspace to your Lambda. Let's fix that by adding an AWS Lambda Function URL to your Lambda so that your Lambda can accept HTTP requests

1. Click on your `bolt_py_oauth_function` Lambda
2. In the **Function Overview**, on the left side, click "Configuration
3. On the left side, click "Function URL"
4. Click "Create function URL"
5. Choose auth type "NONE"
6. Click "Save"

Phew, congrats! Your Slack app is now accessible to the public. On the right side of your bolt_py_oauth_function Function Overview you should see a your Lambda Function URL.

1. Copy it - this is the URL your Lambda function is accessible at publicly.
2. We will now inform Slack that this example app can accept Slash Commands.
3. Back on [api.slack.com/apps](https://api.slack.com/apps), select your app and choose "Slash Commands" from the left menu.
4. Click "Create New Command"
    1. By default, the `aws_lambda_oauth.py` function has logic for a /hello-bolt-python-lambda command. Enter `/hello-bolt-python-lambda` as the Command.
    * Under **Request URL**, paste in the previously-copied Lambda Function URL.
    * Click "Save"
5. We also need to register the API Endpoint as the OAuth redirect URL:
    1. Load up the **OAuth & Permissions** page on[api.slack.com/apps](https://api.slack.com/apps)
    2. Scroll down to "Redirect URLs"
    3. Copy the URL endpoint in - but remove the path portion. The Redirect URL needs to only partially match where we will send users.

You can now install the app to any workspace!

### Test it out!
1. Once installed to a Slack workspace, try typing `/hello-bolt-python-lambda` hello.
2. If you have issues, here are some debugging options:
    1. _View lambda activity_: Head to the Monitor tab under your Lambda. Did the Lambda get invoked? Did it respond with an error? Investigate the graphs to see how your Lambda is behaving.
    2. _Check out the logs_: From this same Monitor tab, you can also click "View Logs in CloudWatch" to see the execution logs for your Lambda. This can be helpful to see what errors are being raised.

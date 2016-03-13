# sheepdawg
<img align="right" src="images/jump.jpg"/>
This is part tutorial and part example. The goal is to provide a workflow for others to learn about AWS Lambda without getting bogged down by all the configuration. Included is a build of the [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html). A more in-depth example creates a basic geoprocessing pipeline for the [2016 CUGOS Spring Fling](http://cugos.org/2016-spring-fling/). Everything uses the provisioning tool Ansible because working with AWS configuration can lead to boredom and death. Some people have asked why this wasn't built with shell scripts around AWS CLI commands, wrapping boto calls outright or using AWS CloudFormation tools. Ansible already wraps a lot of boto and a good number of commands are idempotent. An additional upsell was getting to work with the repository `ansible-lambda` which makes working with Lambda functions way easier. Much thanks.

## Getting Started
0. install `python-virtualenv` for your OS environment. Create a virtualenv

    ```bash
    DEFAULT_PY=$(which python)
    $ virtualenv --python=$DEFAULT_PY venv
    $ source venv/bin/activate
    ```
0. pip install -r requirements

## Create an IAM User to Run the Examples
0. we probably don't want to run these examples as the AWS account holder, so let's create a new IAM user
0. first, login to your AWS account and go to Account > Security Credentials > Access Keys
0. either use your existing keys or create and activate new ones
0. create a shell script with your Access Key and Access Secret called `aws_creds.sh`

    ```bash
    export AWS_ACCESS_KEY_ID=AKSFKLFAKERDEICPA
    export AWS_SECRET_ACCESS_KEY=J+FAKERen0JaarxmnopeemP/xPHi
    ```

0. add environment variables for the new IAM user you'll be creating

    ```bash
    export AWS_ACCESS_KEY_ID=AKSFKLFAKERDEICPA
    export AWS_SECRET_ACCESS_KEY=J+FAKERen0JaarxmnopeemP/xPHi
    # new lines
    export IAM_USER_NAME=cugos
    export IAM_USER_PASSWORD=cugos
    ```
0. source it

    ```bash
    $ source aws_creds.sh
    ```
0. now run the ansible playbook to create the IAM user. Note, this is just creating a new user with AdminAccess policy. To restrict the permissions override the policy json and `policy_path` in `overrides/iam_user_vars.yml`

    ```bash
    $ ansible-playbook -i devops/inventories/dynamic  devops/iam_create_user.yml
    ```
0. there should be a `new_aws_creds.sh` file created in the root directory with this new user's access keys and secrets as well as an account number:

    ```bash
    export IAM_USER_NAME="cugos"
    export IAM_USER_PASSWORD="cugos"
    export AWS_ACCESS_KEY_ID=AKIMAPFARTOVGUKAA
    export AWS_SECRET_ACCESS_KEY=Eo2tjTi3QMAPFARTHfd197bI/rXRen/T
    export ACCOUNT=359356595137
    ```
0. these are the credentials we're going to want to use for the rest of the examples so source this:

    ```bash
    $ source new_aws_creds.sh
    ```

## Run the AWS Lambda with Amazon S3 Tutorial Example
0. this example is a build of the [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html). If you've ever tried to follow that tutorial you'll notice there's a lot of configuration and ways to screw up the result.
0. this example is running off a set of default config vars. if you want to change these then uncomment and update the variables in `overrides/aws_with_amazon_s3_tutorial_vars.yml`. Note, the `--private-key` is referring to this thing you'll have to setup and export the public key to this file
0. then run this ansible playbook for the tutorial and cross your fingers.

    ```bash
    ```

0. an overview of things this command does:
    0. creates an ec2 instance with key pairs, wide open security groups and elastic ips
    0. creates S3 buckets with correct permissions and notification policies for events
    0. uses the ec2 instance to build our lambda dependencies and lambda handler into a zipfile
    0. creates a Lambda function service from our built zipfile
    0. creates the correct IAM roles and permissions for S3 to invoke our Lambda function and for Lambda to access S3

## Run the Geospatial Job Queue Example
0. blah


## TODO
0. add invoking function for Lambda tutorial
0. get rid of the vars in the create Lambda function, also clean up any variable definition in this section
0. use the new iam module with role from ansible-lambda
0. remove `ansible-vault` and unencrypt public key to be used
0. copy over all vars to the needed var overrides
0. move reusable task to separate plays with includes

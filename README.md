# sheepdawg
This is part tutorial, part example and part tool. The goal is to provide a base for others learning about lambda.
<img align="right" src="images/jump.jpg"/>
Included is a full build out of their [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html). A more indepth example of creating a geoprocessing pipeline is also included for the [2016 CUGOS Spring Fling](http://cugos.org/2016-spring-fling/). It's built using the provisioning tool Ansible because working with AWS Lambda configuration can lead to boredom and frustration. While this could've been built with shell scripts around AWS CLI commands or directly wrapping boto calls, Ansible already wraps a lot of boto and has mostly idempotent commands. Then there's the wonderful repository `ansible-lambda` with it's idempotent lambda commands. Much thanks.

## Getting Started
0. get an AWS Account
0. login and go to My Account > Security Credentials
0. create a shell script of your Access Key and Access Secret called aws_creds.sh
0. source them

0. create a virtualenv
0. pip install -r requirements

## Create an IAM User to Run the Examples
0. open up this yaml file and add a username, region and required
0. run ansible playbook create_iam_user
0. note the *.sh file created for you? 
   it includes your account_number,
   new user access_key and secret, it also includes the Ansible AWS_PROFILE
   that will be used to shell out to AWS CLI for calls that aren't wrapped yet. source it
0. let's make sure this user has ALL admin permissions we need
   by running the AWS Lambda tutorial example

## Run the Using AWS Lambda with Amazon S3 Example
0. open up this yaml file and add required variables
0. then run this ansible playbook for the tutorial and cross your fingers
0. some things it does:

## Run the Geospatial Job Queue Example
0. blah



# Spatial-SheepDa
![lamb geometry](images/jump.png)

## Getting Started
0. get an AWS Account
0. login and go to My Account > Security Credentials
0. create a shell script of your Access Key and Access Secret called aws_creds.sh
0. source them

0. create a virtualenv
0. pip install -r requirements

## Step 1: Create a user to run these examples
0. open up this yaml file and add a username, region and required
0. run ansible playbook create_iam_user
0. note the *.sh file created for you? 
   it includes your account_number,
   new user access_key and secret, it also includes the Ansible AWS_PROFILE
   that will be used to shell out to AWS CLI for calls that aren't wrapped yet. source it
0. let's make sure this user has ALL admin permissions we need
   by running the AWS Lambda tutorial example

## Step 2: Run the tutorial example
0. open up this yaml file and add required variables
0. then run this ansible playbook for the tutorial and cross your fingers
0. some things it does:

## Step 3: Geo Walkabout
0. blah



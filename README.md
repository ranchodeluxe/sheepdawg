# sheepdawg
This is part tutorial and part example. The goal is to provide a workflow for others to learn about AWS Lambda without getting bogged down by all the configuration.
<img align="right" src="images/jump.jpg"/>
Included is a build of the [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html). A more in-depth example creates a basic geoprocessing pipeline for the [2016 CUGOS Spring Fling](http://cugos.org/2016-spring-fling/). Everything uses the provisioning tool Ansible because working with AWS configuration can lead to boredom and death. Some people have asked why this wasn't built with shell scripts around AWS CLI commands or directly wrapping boto calls. Ansible already wraps a lot of boto and a good number of commands are idempotent. An additional upsell was getting to work with the repository `ansible-lambda` which makes working with Lambda functions way easier. Much thanks.

## Getting Started
* login to your AWS account and go to Account > Security Credentials > Access Keys
* either use your existing keys or create and active new ones
* create a shell script with your Access Key and Access Secret called `aws_creds.sh`
```bash
export AWS_ACCESS_KEY_ID=AKSFKLFAKERDEICPA
export AWS_SECRET_ACCESS_KEY=J+FAKERen0JaarxmnopeemP/xPHi
```
* source it
```bash
$ source aws_creds.sh
```
* install `python-virtualenv` for your OS environment. Create a virtualenv
```bash
DEFAULT_PY=$(which python)
$ virtualenv --python=$DEFAULT_PY venv
$ source venv/bin/activate
```
* pip install -r requirements

## Create an IAM User to Run the Examples
* We probably don't want to run our services as the account holder, so let's create a new IAM user
* open `aws_creds.sh` again and add environment variables for the new IAM user you'll be creating
```bash
export AWS_ACCESS_KEY_ID=AKSFKLFAKERDEICPA
export AWS_SECRET_ACCESS_KEY=J+FAKERen0JaarxmnopeemP/xPHi
# new lines
export IAM_USER_NAME=cugos
export IAM_USER_PASSWORD=mapfart
```
* source it again
```bash
$ source aws_creds.sh
```
* now run the ansible playbook to create the IAM user
```bash
$ ansible-playbook -i devops/inventories/dynamic  devops/iam_create_user.yml
```
* there should be a `new_aws_creds.sh` file created in the root directory with this new user's access keys and secrets as well as an account number:
```bash
export IAM_USER_NAME="cugos"
export IAM_USER_PASSWORD="mapfart"
export AWS_ACCESS_KEY_ID=AKIAJL2ULAFYDOVGUKAA
export AWS_SECRET_ACCESS_KEY=Eo2tjTi3QF9kNjX1dYfvXItzHfd197bI/rXRen/T
export ACCOUNT=359356595137
```
* these are the credentials we're going to want to use for the rest of the examples so source this:
```bash
$ source new_aws_creds.sh
```

## Run the AWS Lambda with Amazon S3 Tutorial Example
* this example is a build of the [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html). If you've ever tried to follow that tutorial you'll notice there's a lot of configuration and ways to screw up the result.
* open up this yaml file and add required variables
* then run this ansible playbook for the tutorial and cross your fingers
* some things it does:

## Run the Geospatial Job Queue Example
* blah



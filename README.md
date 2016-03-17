
<img align="right" src="images/jump.jpg"/>
This is part tutorial and part example. The goal was to build a toolchain to help myself learn and write AWS Lambda handlers without the configuration headaches. Included is a build of the [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html). A more in-depth example for creating a geoprocessing pipeline using shared libs is currently baking. Everything uses the provisioning tool Ansible because working with AWS configuration can lead to boredom and death. A few people asked why this was built with Ansible. If you feel this way, then please read the [Why Ansible](#why-ansible) section.

## Getting Started
0. `git` checkout this respository
    ```bash
    $ mkdir -p /usr/local/src/sheepdawg
    $ cd /usr/local/src/sheepdawg
    $ git checkout git@github.com:ranchodeluxe/sheepdawg.git .
    ```
0. install `python-virtualenv` for your OS environment ( linux below, [mac-osx here](http://www.marinamele.com/2014/05/install-python-virtualenv-virtualenvwrapper-mavericks.html), avoid windows ):

    ```bash
    DEFAULT_PY=$(which python)
    $ virtualenv --python=$DEFAULT_PY venv
    $ source venv/bin/activate
    ```
0. pip install -r requirements

## Create an IAM User to Run the Examples
0. we won't run these examples with the AWS root account, so let's create a new IAM user
0. first, login to your AWS account and go to Account > Security Credentials > Access Keys
0. either use your existing root account keys or create and activate new ones
0. create a shell script with your Access Key and Access Secret called `aws_creds.sh`

    ```bash
    export AWS_ACCESS_KEY_ID=ABCDEFGHIJKLMN
    export AWS_SECRET_ACCESS_KEY=A+BCDEFGHIJK/LMN
    ```

0. add environment variables for the new IAM user you'll be creating

    ```bash
    export AWS_ACCESS_KEY_ID=ABCDEFGHIJKLMN
    export AWS_SECRET_ACCESS_KEY=A+BCDEFGHIJK/LMN
    # new lines
    export IAM_USER_NAME=cugos
    export IAM_USER_PASSWORD=cugos
    ```
0. source it

    ```bash
    $ source aws_creds.sh
    ```
0. now create a new IAM user with the following command. Note, this creates a user with same AdminAccess policy as the root account which is not what most people want. To restrict the permissions override the policy json and `policy_path` in `overrides/iam_user_vars.yml`

    ```bash
    $ ansible-playbook ./devops/iam_create_user.yml --extra-vars="overrides_filename=iam_users"
    ```
0. there should be a `new_aws_creds.sh` file created in the `/sheepdawg/` root directory with this new user's access keys and secrets as well as an account number:

    ```bash
    export IAM_USER_NAME="cugos"
    export IAM_USER_PASSWORD="cugos"
    export AWS_ACCESS_KEY_ID=ABCDEFGHIJKLMN
    export AWS_SECRET_ACCESS_KEY=A+BCDEFGHIJK/LMN
    export AWS_ACCOUNT_ID=123456789
    ```
0. these are the credentials we're going to want to use for the rest of the examples so source this:

    ```bash
    $ source new_aws_creds.sh
    ```

## Run the AWS Lambda with Amazon S3 Tutorial Example
0. this example is a build of the [AWS S3 Lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html)
0. this example is running off a set of default config variables declared in `devops/group_vars/*.yml`. if you want to override one of these then copy and paste it into `overrides/aws_with_amazon_s3_tutorial_vars.yml`. Note, the only default variable that you **have to change** is the `centos_ssh_public_key` which determines how you ssh into the ec2 build box and should mirror the private ssh key passed in commands as `--private-key` flag`. Read more about that in (creating-ssh-keys)[#create-ssh-keys]
0. create an ec2 build box where we we'll bundle our Lambda code and it's dependencies into a zipfile as [described in the tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html)
    ```bash
    $ ansible-playbook ./devops/ec2_create_instance.yml --extra-vars="overrides_filename=aws_with_amazon_s3_tutorial_vars"
    ```
0. then run this command to setup the S3 buckets, Lambda function, policies and permissions as [described in the tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-deployment-pkg.html)

    ```bash
    $ ansible-playbook -i devops/inventories/dynamic \
        devops/run_aws_lambda_with_s3_tutorial.yml --private-key=./private.pem -u ec2-user \
        --extra-vars="overrides_filename=aws_with_amazon_s3_tutorial_vars" --limit="tag_Name_tutorial*ec2"
    ```
0. when it's done running go take a look at the source S3 bucket it created which should be called `lambda-example-v1` unless you overrode the config vars to call it something else in `overrides/aws_with_amazon_s3_tutorial_vars.yml`
0. there's a single image that was uploaded called `HappyFace.jpg` just to make sure it's working
0. now let's make sure the tutorial example is working. let's upload more images to the source S3 bucket and an event should fire that runs a Lambda function, resizes the image and dumps it to the `lambda-example-v1resized` S3 bucket as [described in the lambda tutorial](http://docs.aws.amazon.com/lambda/latest/dg/with-s3-example-configure-event-source.html)

    ```bash
    $ ansible-playbook ./devops/test_aws_lambda_with_s3_tutorial.yml \
        --extra-vars="overrides_filename=aws_with_amazon_s3_tutorial_vars"
    ```
0. when it's done running go check the target S3 bucket called `lambda-example-v1resized` unless you overrode the config var name. you should see the resized versions of the images you uploaded to the source bucket

## Run a Geoprocessing Example that Converts a Raster to GeoJSON with PROJ4, GDAL and GEOS shared libs
0. there's a lot of tricks and trapdoors that are still being worked out in this example. Based on [work done here](http://www.perrygeo.com/running-python-with-compiled-code-on-aws-lambda.html)
0. let's use the same credentials created at the beginning of this tutorial, so source this for good measures:
    ```bash
    $ source new_aws_creds.sh
    ```
0. create a new build box. `t2.micro` will build the C dependencies very slow. this example uses overrides for a larger image and also different names so we can tell the AWS infrastructure apart. modify `overrides/geoprocessing_example.yml` if needed.
    ```bash
    $ ansible-playbook ./devops/ec2_create_instance.yml --extra-vars="overrides_filename=geoprocessing_example"
    ```
0. then run this command to setup the S3 buckets, Lambda function, policies and permissions. make sure you have some coffee at hand. it's gonna take awhile to build to the C libs.
    ```bash
    $ ansible-playbook -i devops/inventories/dynamic \
        devops/run_geoprocessor_example.yml --private-key=./private.pem -u ec2-user \
        --extra-vars="overrides_filename=geoprocessing_example"  --limit="tag_Name_geoprocess*ec2"
    ```
0. test the build out...to be continued

## Why Ansible
A few people have asked why this wasn't built with shell scripts around AWS CLI commands, wrapping boto calls outright or using AWS CloudFormation tools. Ansible already wraps a lot of boto and a good number of commands are already idempotent. An additional upsell was getting to work with the great [Ansible Lambda wrappers](https://github.com/pjodouin/ansible-lambda).

## Creating SSH Keys
You need to create a [passwordless ssh key pair](http://www.linuxproblem.org/art_9.html) to log into your ec2 instance. The public key will be loaded onto the ec2 box. The private key will stay local and the path will be pointed to when you run Ansible commands with the `--private-key` flag. The only you have to do is `cat` your public key and then replace the  `centos_ssh_public_key` variable that exists in `devops/group_vars/all.yml` with your new public key. *MAKE SURE IT IS INSERTED IN THE POSITION IT WAS BEFORE -- SAME NUMBER OF SPACES AT FRONT OF THE LINE, NO SPACES AT THE END*

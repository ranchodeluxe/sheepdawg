#!/usr/bin/python
# (c) 2016, Pierre Jodouin <pjodouin@virtualcomputing.solutions>
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

try:
    import boto3
    import boto              # seems to be needed for ansible.module_utils
    from botocore.exceptions import ClientError, ParamValidationError, MissingParametersError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


DOCUMENTATION = '''
---
module: lambda_alias
short_description: Creates, updates or deletes AWS Lambda function aliases.
description:
    - This module allows the management of AWS Lambda functions aliases via the Ansible
      framework.  It is idempotent and supports "Check" mode.
version_added: "2.0"
author: Pierre Jodouin (@pjodouin)
options:
  function_name:
    description:
      - The name of the function alias.
    required: true
  state:
    description:
      - Describes the desired state and defaults to "present".
    required: true
    default: "present"
    choices: ["present", "absent"]
  name:
    description:
      - Name of the function alias.
    required: true
    aliases: ['alias_name']
  description:
    description:
      - A short, user-defined function alias description.
    required: false
  version:
    description:
      -  Version associated with the Lambda function alias.
         A value of 0 (or missing parameter) sets the alias to the $LATEST version.
    required: false
    aliases: ['function_version']

'''

EXAMPLES = '''
---
# Simple example to create a lambda function and publish a version
- hosts: localhost
  gather_facts: no
  vars:
    state: present
    project_folder: /path/to/deployment/package
    deployment_package: lambda.zip
    account: 123456789012
    production_version: 5
  tasks:
  - name: AWS Lambda Function
    lambda:
      state: "{{ state | default('present') }}"
      name: myLambdaFunction
      publish: True
      description: lambda function description
      code_s3_bucket: package-bucket
      code_s3_key: "lambda/{{ deployment_package }}"
      local_path: "{{ project_folder }}/{{ deployment_package }}"
      runtime: python2.7
      timeout: 5
      handler: lambda.handler
      memory_size: 128
      role: "arn:aws:iam::{{ account }}:role/API2LambdaExecRole"

  - name: show results
    debug: var=lambda_facts

# The following will set the Dev alias to the latest version ($LATEST) since version is omitted (or = 0)
  - name: "alias 'Dev' for function {{ lambda_facts.FunctionName }} "
    lambda_alias:
      state: "{{ state | default('present') }}"
      function_name: "{{ lambda_facts.FunctionName }}"
      name: Dev
      description: Development is $LATEST version

# The QA alias will only be created when a new version is published (i.e. not = '$LATEST')
  - name: "alias 'QA' for function {{ lambda_facts.FunctionName }} "
    lambda_alias:
      state: "{{ state | default('present') }}"
      function_name: "{{ lambda_facts.FunctionName }}"
      name: QA
      version: "{{ lambda_facts.Version }}"
      description: "QA is version {{ lambda_facts.Version }}"
    when: lambda_facts.Version != "$LATEST"

# The Prod alias will have a fixed version based on a variable
  - name: "alias 'Prod' for function {{ lambda_facts.FunctionName }} "
    lambda_alias:
      state: "{{ state | default('present') }}"
      function_name: "{{ lambda_facts.FunctionName }}"
      name: Prod
      version: "{{ production_version }}"
      description: "Production is version {{ production_version }}"

'''


def aws_client(module, resource='lambda'):
    """
    Returns a boto3 client object for the requested resource type.

    :param module:
    :param resource:
    :return:
    """

    try:
        region, endpoint, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        aws_connect_kwargs.update(dict(region=region,
                                       endpoint=endpoint,
                                       conn_type='client',
                                       resource=resource
                                       ))
        client = boto3_conn(module, **aws_connect_kwargs)

    except (ClientError, ParamValidationError, MissingParametersError), e:
        module.fail_json(msg="Can't authorize connection - {0}".format(e))

    return client


def get_account_id(module):
    """
    Returns the account ID.

    :param module:
    :return:
    """

    client = aws_client(module, resource='iam')

    try:
        account_id = client.get_user()['User']['Arn'].split(':')[4]
    except (ClientError, ValueError, KeyError, IndexError):
        account_id = ''

    return account_id


def pc(key):
    """
    Changes python key into Pascale case equivalent. For example, 'this_function_name' becomes 'ThisFunctionName'.

    :param key:
    :return:
    """

    return "".join([token.capitalize() for token in key.split('_')])


def set_api_params(module, module_params):
    """
    Sets module parameters to those expected by the boto3 API.

    :param module:
    :param module_params:
    :return:
    """

    api_params = dict()

    for param in module_params:
        module_param = module.params.get(param, None)
        if module_param:
            api_params[pc(param)] = module_param

    return api_params


def validate_params(module):
    """
    Performs basic parameter validation.

    :param module:
    :return:
    """

    function_name = module.params['function_name']

    # validate function name
    if not re.search('^[\w\-:]+$', function_name):
        module.fail_json(
                msg='Function name {0} is invalid. Names must contain only alphanumeric characters and hyphens.'.format(function_name)
        )
    if len(function_name) > 64:
        module.fail_json(msg='Function name "{0}" exceeds 64 character limit'.format(function_name))

    #  if parameter 'function_version' is zero, set it to $LATEST, else convert it to a string
    if module.params['function_version'] == 0:
        module.params['function_version'] = '$LATEST'
    else:
        module.params['function_version'] = str(module.params['function_version'])

    return


def get_lambda_alias(module):
    """
    Returns the lambda function alias if it exists.

    :param module:
    :return:
    """

    client = aws_client(module)

    # set API parameters
    api_params = set_api_params(module, ('function_name', 'name'))

    # check if alias exists and get facts
    try:
        results = client.get_alias(**api_params)

    except (ClientError, ParamValidationError, MissingParametersError), e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            results = None
        else:
            module.fail_json(msg='Error retrieving function alias: {0}'.format(e))

    return results


def lambda_alias(module):
    """
    Adds, updates or deletes lambda function aliases.

    :param module: Ansible module reference
    :return dict:
    """
    client = aws_client(module)
    results = dict()
    changed = False
    current_state = 'absent'
    state = module.params['state']

    facts = get_lambda_alias(module)
    if facts:
        current_state = 'present'

    if state == 'present':
        if current_state == 'present':

            # check if alias has changed -- only version and description can change
            alias_params = ('function_version', 'description')
            for param in alias_params:
                if module.params.get(param) != facts.get(pc(param)):
                    changed = True
                    break

            if changed:
                api_params = set_api_params(module, ('function_name', 'name'))
                api_params.update(set_api_params(module, alias_params))

                if not module.check_mode:
                    try:
                        results = client.update_alias(**api_params)
                    except (ClientError, ParamValidationError, MissingParametersError), e:
                        module.fail_json(msg='Error updating function alias: {0}'.format(e))

        else:
            # create new function alias
            api_params = set_api_params(module, ('function_name', 'name', 'function_version', 'description'))

            try:
                if not module.check_mode:
                    results = client.create_alias(**api_params)
                changed = True
            except (ClientError, ParamValidationError, MissingParametersError), e:
                module.fail_json(msg='Error creating function alias: {0}'.format(e))

    else:  # state = 'absent'
        if current_state == 'present':
            # delete the function
            api_params = set_api_params(module, ('function_name', 'name'))

            try:
                if not module.check_mode:
                    results = client.delete_alias(**api_params)
                changed = True
            except (ClientError, ParamValidationError, MissingParametersError), e:
                module.fail_json(msg='Error deleting function alias: {0}'.format(e))

    return dict(changed=changed, ansible_facts=dict(lambda_alias_facts=results or facts))


def main():
    """
    Main entry point.

    :return dict: ansible facts
    """
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        state=dict(required=False, default='present', choices=['present', 'absent']),
        function_name=dict(required=True, default=None),
        name=dict(required=True, default=None, aliases=['alias_name']),
        function_version=dict(type='int', required=False, default=0, aliases=['version']),
        description=dict(required=False, default=None),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[],
        required_together=[]
    )

    # validate dependencies
    if not HAS_BOTO3:
        module.fail_json(msg='Both boto3 & boto are required for this module.')

    validate_params(module)

    results = lambda_alias(module)

    module.exit_json(**results)


# ansible import module(s) kept at ~eof as recommended
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()

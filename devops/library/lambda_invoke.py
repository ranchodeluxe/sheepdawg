#!/usr/bin/python
# (c) 2016, Pierre Jodouin <pjodouin(at)virtualcomputing.solutions
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

DOCUMENTATION = '''
---
module: lambda_invoke
short_description: Invokes an AWS Lambda function 
description:
    - This module has a single purpose of triggering the execution of a specified lambda function. 
version_added: "2.0"
author: Pierre Jodouin (@pjodouin)
options:
  function_name:
    description:
      - The Lambda function name. You can specify an unqualified function name (for example, "Thumbnail") or you can 
        specify Amazon Resource Name (ARN) of the function. AWS Lambda also allows you to specify only the account ID 
        qualifier (for example, "account-id:Thumbnail"). Note that the length constraint applies only to the ARN. 
        If you specify only the function name, it is limited to 64 character in length.
    required: true
  qualifier:
    description:
      - You can use this optional parameter to specify a Lambda function version or alias name. If you specify function
        version, the API uses qualified function ARN to invoke a specific Lambda function. If you specify alias name, 
        the API uses the alias ARN to invoke the Lambda function version to which the alias points. 
        If you don't provide this parameter, then the API uses unqualified function ARN which results in invocation of 
        the $LATEST version.
    required: false
    default: none
  invocation_type:
    description:
      - By default, the Invoke API assumes "RequestResponse" invocation type. You can optionally request asynchronous 
        execution by specifying "Event" as the invocation type. You can also use this parameter to request AWS Lambda 
        to not execute the function but do some verification, such as if the caller is authorized to invoke the 
        function and if the inputs are valid. You request this by specifying "DryRun" as the invocation_type. This is 
        useful in a cross-account scenario when you want to verify access to a function without running it.
    required: true
    choices: [
        "RequestResponse",
        "Event",
        "DryRun"
        ]
    default: RequestResponse
  log_type:
    description:
      - You can set this optional parameter to "Tail" in the request only if you specify the invocation_type parameter 
        with value "RequestResponse". In this case, AWS Lambda returns the base64-encoded last 4 KB of log data 
        produced by your Lambda function in the x-amz-log-results header.
    required: false
    choices: ["Tail"]
    default: none
  client_context:
    description:
      - Using client_context you can pass client-specific information to the Lambda function you are invoking. You can 
        then process the client information in your Lambda function as you choose through the context variable. 
        The ClientContext JSON must be base64-encoded.
    required: false
    default: none
  payload:
    description:
      - JSON that you want to provide to your Lambda function as input. 
    required: false
    default: none  
extends_documentation_fragment: aws
'''

EXAMPLES = '''
---
# Simple example that invokes a lambda function
- name: execute lambda function
  lambda_invoke:
    function_name: myFunction
    invocation_type: RequestResponse
    log_type: Tail
  register: my_function_details
- name: show Lambda function results
  debug: var=Results
'''

try:
    import boto3
    import boto                                         # seems to be needed for ansible.module_utils
    from botocore.exceptions import ClientError, EndpointConnectionError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


# ----------------------------------
#          Helper functions
# ----------------------------------

def pc(key):
    """
    Changes python key into Pascale case equivalent. For example, 'this_function_name' becomes 'ThisFunctionName'.

    :param key:
    :return:
    """

    return "".join([token.capitalize() for token in key.split('_')])


def get_api_params(params, module, resource_type, required=False):
    """
    Check for presence of parameters, required or optional and change parameter case for API.

    :param params: AWS parameters needed for API
    :param module: Ansible module reference
    :param resource_type:
    :param required:
    :return:
    """

    api_params = dict()

    for param in params:
        value = module.params.get(param)
        if value:
            api_params[pc(param)] = value
        else:
            if required:
                module.fail_json(msg='Parameter {0} required for this action on resource type {1}'.format(param, resource_type))

    return api_params


# ----------------------------------
#   Resource management functions
# ----------------------------------

def invoke_function(client, module):
    """
    Invokes the lambda function.

    :param client: AWS API client reference (boto3)
    :param module: Ansible module reference
    :return dict:
    """

    results = dict()
    api_params = dict()

    resource = 'invoke'

    required_params = ('function_name',)
    api_params.update(get_api_params(required_params, module, resource, required=True))

    optional_params = ('qualifier', 'invocation_type', 'log_type', 'client_context', 'payload')
    api_params.update(get_api_params(optional_params, module, resource, required=False))
 
    # override invocation type if 'Check' mode is on
    if module.check_mode:
        api_params[pc('invocation_type')] = 'DryRun'
 
    # execute lambda function 
    try:
        results = client.invoke(**api_params)
    except ClientError, e:
        module.fail_json(msg='Error invoking function {0}: {1}'.format(module.params['function_name'], e))
    except EndpointConnectionError, e:
        module.fail_json(msg='Lambda function not found: {0}'.format(e))

    # The returned Payload is a botocore StreamingBody object. Read all content and convert to JSON.
    if 'Payload' in results:
        results['Payload'] = json.loads(results['Payload'].read())

    return results


def main():
    """
    Main entry point.

    :return dict: ansible facts
    """
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            function_name=dict(required=True, default=None),
            invocation_type=dict(required=False, choices=['Event', 'RequestResponse', 'DryRun'], default='RequestResponse'),
            qualifier=dict(default=None, required=False),
            log_type=dict(default=None, required=False, choices=['Tail', ]),
            client_context=dict(default=None, required=False),
            payload=dict(default=None, required=False)
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
        module.fail_json(msg='boto3 is required for this module.')

    # validate function_name if present
    function_name = module.params['function_name']
    if function_name:
        if not re.search('^[\w\-:]+$', function_name):
            module.fail_json(
                    msg='Function name {0} is invalid. Names must contain only alphanumeric characters and hyphens.'.format(function_name)
            )
        if len(function_name) > 64:
            module.fail_json(msg='Function name "{0}" exceeds 64 character limit'.format(function_name))

    try:
        region, endpoint, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        aws_connect_kwargs.update(dict(region=region,
                                       endpoint=endpoint,
                                       conn_type='client',
                                       resource='lambda'
                                       ))
        client = boto3_conn(module, **aws_connect_kwargs)
    except ClientError, e:
        module.fail_json(msg="Can't authorize connection - {0}".format(e))
    except EndpointConnectionError, e:
        module.fail_json(msg="Connection Error - {0}".format(e))

    response = invoke_function(client, module)
    results = dict(ansible_facts=response, changed=False)

    module.exit_json(**results)


# ansible import module(s) kept at ~eof as recommended
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()

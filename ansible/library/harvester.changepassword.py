#!/usr/bin/env python3
"""
Copyright (C) 2024 SUSE LLC
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.harvester_api import HarvesterAPI, API_ARG_SPEC


DOCUMENTATION = r'''
---
module: harvester.changepassword

short_description: Change or set the password of a user account of Harvester HCI

version_added: "1.0.0"

options:
    api:
        description: API endpoint and authentication information
        required: true
        type: dict
    new_password:
        description: New password in clear text
        required: true
        type: str

author:
    - Moritz Röhrich (@m-ildefons)
'''

EXAMPLES = r'''
 - name: Change Cluster Password
   harvester.changepassword:
     api:
       endpoint: 'https://10.10.10.10/'
       username: 'admin'
       password: 'admin'
     new_password: "password1234"
'''

RETURN = r'''
'''


def main():
    module_args = dict(
        api=dict(type='dict', required=True, options=API_ARG_SPEC),

        new_password=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    if module.params['new_password'] == module.params['api']['password']:
        module.fail_json(
                msg='new password must be different from old password',
                **result)

    try:
        api = HarvesterAPI.login(
            endpoint=module.params['api']['endpoint'],
            username=module.params['api']['username'],
            password=module.params['api']['password'],
            ssl_verify=module.params['api']['tls_verify'],
        )

        params = dict(
            action="changepassword",
        )

        body = dict(
            currentPassword=module.params['api']['password'],
            newPassword=module.params['new_password'],
        )

        resp = api.post("v3/users", params=params, json=body)
        assert resp.status_code == 200
    except AssertionError:
        module.fail_json(
                msg='API error while changing passwords',
                **result)
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()

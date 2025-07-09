#!/usr/bin/env python3
"""
Copyright (C) 2024 SUSE LLC
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.harvester_api import HarvesterAPI, API_ARG_SPEC


DOCUMENTATION = r'''
---
module: harvester.version

short_description: Query a Harvester HCI cluster for its version

version_added: "1.0.0"

options:
    api:
        description: API endpoint and authentication information
        required: true
        type: dict

author:
    - Moritz Röhrich (@m-ildefons)
'''

EXAMPLES = r'''
 - name: Get Harvester Cluster Version
   harvester.version:
     api:
       endpoint: 'https://10.10.10.10/'
       username: 'admin'
       password: 'admin'
   register: cluster_information
'''

RETURN = r'''
cluster_version:
    description: The version information string of the Harvester HCI cluster
    type: str
    returned: always:
    sample: v1.3.0-rc2
'''


def main():
    module_args = dict(
        api=dict(type='dict', required=True, options=API_ARG_SPEC)
    )

    result = dict(
        changed=False,
        cluster_version='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        api = HarvesterAPI.login(
            endpoint=module.params['api']['endpoint'],
            username=module.params['api']['username'],
            password=module.params['api']['password'],
            ssl_verify=module.params['api']['tls_verify'],
        )
        resp = api.get("apis/harvesterhci.io/v1beta1/settings/server-version/")
        assert resp.status_code == 200
    except AssertionError:
        result['cluster_version'] = "v0.0.0-error"
    else:
        result['cluster_version'] = resp.json()['value']

    module.exit_json(**result)


if __name__ == '__main__':
    main()

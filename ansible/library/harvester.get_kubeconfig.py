#!/usr/bin/env python3
"""
Copyright (C) 2024 SUSE LLC
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.harvester_api import HarvesterAPI, API_ARG_SPEC


DOCUMENTATION = r'''
module: harvester.get_kubeconfig

short_description: Fetch the kubeconfig file from a Harvester HCI cluster

version_added: "1.0.0"

options:
    api:
        description: API endpoint and authentication information
        required: true
        type: dict
    path:
        description: Path to save the kubeconfig file to
        required: true
        type: str

author:
    - Moritz Röhrich (@m-ildefons)
'''

EXAMPLES = r'''
 - name: Get Harvester Kubeconfig
   harvester.get_kubeconfig:
     api:
       endpoint: 'https://10.10.10.10/'
       username: 'admin'
       password: 'password1234'
     path: /tmp/kubeconfig.yaml
'''

RETURN = r'''
kubeconfig:
    description: The kubeconfig received from the Harvester HCI cluster
    type: str
    returned: always:
    sample:
'''


def main():
    module_args = dict(
        api=dict(type='dict', required=True, options=API_ARG_SPEC),

        path=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        kubeconfig='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        api = HarvesterAPI.login(
            endpoint=module.params['api']['endpoint'],
            username=module.params['api']['username'],
            password=module.params['api']['password'],
            ssl_verify=module.params['api']['tls_verify'],
        )

        params=dict(
            action="generateKubeconfig",
        )

        resp = api.post("v1/management.cattle.io.clusters/local", params=params)
        assert resp.status_code == 200
    except AssertionError:
        module.fail_json(**result)
    else:

        path = module.params['path']

        with open(path, 'w', encoding='utf-8') as kubeconfig:
            kubeconfig.write(resp.json()['config'])

        result['changed'] = True
        result['kubeconfig'] = resp.json()['config']

    module.exit_json(**result)


if __name__ == '__main__':
    main()

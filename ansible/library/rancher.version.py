#!/usr/bin/env python3
"""
Copyright (C) 2024 SUSE LLC
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.rancher_api import RancherAPI, API_ARG_SPEC


DOCUMENTATION = r'''
'''

EXAMPLES = r'''
'''

RETURN = r'''
'''


def main():
    module_args = dict(
        api=dict(type='dict', required=True, options=API_ARG_SPEC),
    )

    result = dict(
        changed=False,
        k8s_version='',
        install_uuid='',
        server_version='',
        server_url='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        api = RancherAPI.login(
            endpoint=module.params['api']['endpoint'],
            username=module.params['api']['username'],
            password=module.params['api']['password'],
            ssl_verify=module.params['api']['tls_verify'],
        )
        k8s_ver_resp = api.get("apis/management.cattle.io/v3/settings/k8s-version/")
        assert k8s_ver_resp.status_code == 200
        inst_uuid_resp = api.get("apis/management.cattle.io/v3/settings/install-uuid/")
        assert inst_uuid_resp.status_code == 200
        server_ver_resp = api.get("apis/management.cattle.io/v3/settings/server-version/")
        assert server_ver_resp.status_code == 200
        server_url_resp = api.get("apis/management.cattle.io/v3/settings/server-url/")
        assert server_url_resp.status_code == 200
    except AssertionError:
        module.fail_json(
            msg="failed to get rancher version information",
            k8s_version='',
            install_uuid='',
            server_version='',
            server_url='',
        )
    else:
        result['k8s_version'] = k8s_ver_resp.json()['value']
        result['install_uuid'] = inst_uuid_resp.json()['value']
        result['server_version'] = server_ver_resp.json()['value']
        result['server_url'] = server_url_resp.json()['value']

    module.exit_json(**result)


if __name__ == '__main__':
    main()

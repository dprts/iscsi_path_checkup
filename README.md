# Ansible ISCSI Checkup Playbook
## Requirements

1. On the worker: `netapp-lib`, `json`, `jmespath`
```bash
pip3 install --user netapp-lib jmespath
```

2. On every host belonging to `www_servers` group: `json`, `json2html`
```bash
pip3 install --user netapp-lib jmespath
```

## Installation

1. Pull the repository

```bash
git clone git@github.com:dprts/iscsi_path_checkup.git
```

2. Update inventory. This repository contains example inventory, update it to your needs:
```
inventory/
├── group_vars
│   └── filers
│       └── all.yml
├── hosts
└── host_vars
    ├── cluster1.example.com
    │   └── vars.yml
    └── cluster2.example.com
        └── vars.yml
```

## Execution
```bash
ansible-playbook check_lun_maps.yml
```




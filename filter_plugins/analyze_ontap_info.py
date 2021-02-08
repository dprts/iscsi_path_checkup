# Copyright: (c) 2021, Piotr Olczak (@dprts) <piotr.olczak@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from json import load, dumps
import jmespath

initiators_query = """
* | [?initiators.initiator_info!=null].{
  vserver: vserver
  igroup: initiator_group_name
  initiators: [initiators.initiator_info] | []
}
"""

iscsi_initiator_list_info_query = """
* | [].{
  vserver: vserver
  initiator: initiator_nodename
  initiator_aliasname: initiator_aliasname
  lif: tpgroup_name
  target_session_id: target_session_id
  igroups: [initiator_group_list.initiator_group_list_info] | []
}
"""


def validate_paths(data):
    """ Generates json output containing multipath status """

    lun_map_info = data['ontap_info']['lun_map_info']
    lun_info = data['ontap_info']['lun_info']
    igroup_info = data['ontap_info']['igroup_info']
    iscsi_initiator_list_entry_info = data['ontap_info']['iscsi_initiator_list_entry_info']

    igroup_initiators = jmespath.search(initiators_query, igroup_info)

    vserver_initiator = []

    for igroup in igroup_initiators:
        for initiator in igroup['initiators']:
            vserver_initiator += [
                {
                    'vserver': igroup['vserver'],
                    'igroup': igroup['igroup'],
                    'initiator': initiator['initiator_name']
                }
            ]

    recombined_lun_map_info = []
    for lun_key in lun_map_info.keys():
        # recombined_lun_map_info = lun_map_info[lun_key]
        lun = lun_map_info["{}".format(lun_key)]
        recombine_lun_map_info_query = "*|[?path=={!r} && {!r}]".format(
            lun['path'], lun['vserver'])
        volume = jmespath.search(recombine_lun_map_info_query, lun_info)
        lun['volume'] = volume[0]['volume']
        recombined_lun_map_info += [lun]

    lun_maps = []
    for initiator in vserver_initiator:
        igroup_query = '[?initiator_group=={!r} && vserver=={!r}]'.format(
            initiator['igroup'], initiator['vserver'])
        mapped_luns = jmespath.search(igroup_query, recombined_lun_map_info)
        lun_maps += [{
            'initiator': initiator['initiator'],
            'igroup': initiator['igroup'],
            'vserver': initiator['vserver'],
            'mapped_luns': mapped_luns
        }]

    initiator_list = jmespath.search(
        iscsi_initiator_list_info_query, iscsi_initiator_list_entry_info)

    igroup_initiator_list = []
    for igr_initiator in initiator_list:
        for igr in igr_initiator['igroups']:
            igroup_initiator_list += [
                {
                    'initiator': igr_initiator['initiator'],
                    'initiator_aliasname': igr_initiator['initiator_aliasname'],
                    'lif': igr_initiator['lif'],
                    'target_session_id': igr_initiator['target_session_id'],
                    'vserver': igr_initiator['vserver'],
                    'igroup': igr['initiator_group_name']
                }
            ]

    final_stuff_dude = []
    for lun_map in lun_maps:
        final_query = "[?igroup=={!r} && initiator=={!r} && vserver=={!r}]".\
            format(lun_map['igroup'], lun_map['initiator'], lun_map['vserver'])
        login_status = jmespath.search(final_query, igroup_initiator_list)
        if len(lun_map['mapped_luns']) > 1 and len(login_status) > 0:
            final_entry = lun_map
            final_entry['login_status'] = login_status
            final_entry['multipath_paths'] = len(login_status)
            if len(login_status) == 1:
                final_entry['multipath_state'] = '<p style=\"color:red\">BAD</p>'
            elif len(login_status) % 2 == 1:
                final_entry['multipath_state'] = '<p style=\"color:orange\">WARN</p>'
            else:
                final_entry['multipath_state'] = '<p style=\"color:lime\">OK</p>'

            final_stuff_dude += [final_entry]

    return final_stuff_dude


class FilterModule(object):
    """ Ansible filters """

    def filters(self):
        filters = {
            'validate_paths': validate_paths
        }

        return filters

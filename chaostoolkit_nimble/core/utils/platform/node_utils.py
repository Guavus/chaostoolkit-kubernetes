import logging

from logzero import logger
from retrying import retry

from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

NODE_PING_TIMEOUT = 90000
NODE_GOING_DOWN_TIMEOUT = 10000

_LOGGER = logging.getLogger(__name__)


def _query_node_status(result):
    return not result


def is_node_up_and_running(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    command = ShellUtils.ping(node_hostname_domain, count=5)
    logger.info("Executing command: %s" % command)
    response = ShellUtils.execute_shell_command(command).stdout
    logger.debug(response)
    return not "Request timeout" in response


@retry(stop_max_delay=NODE_PING_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def wait_for_node_to_be_pingable(node_alias):
    return is_node_up_and_running(node_alias)


def reboot_node(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    node_username = NodeManager.node_obj.nodes[node_alias].username
    node_password = NodeManager.node_obj.nodes[node_alias].password
    # command = 'sshpass -p "guavus@123" ssh guavus@testautomation004-infra-01.cloud.in.guavus.com "nohup sleep 10m &"'
    command = 'sshpass -p "guavus@123" ssh -tt guavus@testautomation004-infra-01.cloud.in.guavus.com \'echo guavus@123 | sudo -S -s sh -c "nohup sleep 10m &"\''
    # command = 'sshpass -p "%s" ssh -tt %s@%s \'echo %s | sudo -S -s sh -c "nohup reboot &"\'' % (node_password, node_username, node_hostname_domain, node_password)
    return ShellUtils.execute_shell_command(command)


# def reboot_nodes_sequentially(node_alias_list, callable_=None, **kwargs):
#     for node_alias in node_alias_list:
#         node_alias = node_alias.strip()
#         prev_node_alias = node_alias if (node_alias_list.index(node_alias) - 1) is -1 else node_alias_list[
#             node_alias_list.index(node_alias) - 1]
#         try:
#             wait_for_node_to_be_pingable(prev_node_alias)
#             assert is_node_up_and_running(node_alias)
#             reboot_node(node_alias)
#             time.sleep(6)
#             # assert not is_node_up_and_running(node_alias)
#             if callable_:
#                 callable_(**kwargs)
#         except RetryError:
#             _LOGGER.info("**** HA could not be tested on node '%s'. Node is in down state!" % node_alias)
#             logger.info("**** HA could not be tested on node '%s'. Node is in down state!" % node_alias)
#
#
# def run_test_suites_post_node_down(options_dict, test_suites, tests=None):
#     option_string = " ".join("--%s=%s" % (option, value) for option, value in options_dict.items())
#     command = "python -m pytest %s" % option_string
#     if tests:
#         command = "%s -k '%s'" % (command, tests)
#     command = "%s %s" % (command, ",".join(test_suite for test_suite in test_suites))
#     _LOGGER.info("Running test suites: '%s'" % test_suites)
#     # assert ShellUtils.execute_shell_command(command).status
#     command = 'python -m pytest -k "test_2 or test_3" --testbed=resources/testbeds/automation_squad/testautomation004.yml  --componentAttributesConfig=resources/components/component_attributes_kerberos_non_root.yml  --keytabFileserverPath=modules/platform/sanity/keytabs/stuser.keytab --ha=testautomation004-slv-02,testautomation004-slv-01,testautomation004-slv-03  tests/krititests'
#     response = ShellUtils.execute_shell_command(command)
#     pass
#
#
# def perform_node_ha_with_func_suite(node_alias_list,callable_=None, **kwargs):
#     reboot_nodes_sequentially(node_alias_list, callable_=run_test_suites_post_node_down, **kwargs)


@retry(stop_max_delay=NODE_GOING_DOWN_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def wait_for_node_to_go_down(node_alias):
    # _LOGGER to be removed
    _LOGGER.info("Waiting for node '%s' to go down" % node_alias)
    logger.info("Waiting for node '%s' to go down" % node_alias)
    return not is_node_up_and_running(node_alias)

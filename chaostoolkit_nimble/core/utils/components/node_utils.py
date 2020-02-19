from logzero import logger
from retrying import retry

from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils

NODE_PING_TIMEOUT = 90000
NODE_GOING_DOWN_TIMEOUT = 10000
NODE_SSH_TIMEOUT = 60000


def _query_node_status(result):
    return not result


def is_node_up_and_running(node_alias):
    return is_node_pingable(node_alias) and is_node_sshable(node_alias)


def is_node_pingable(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    command = ShellUtils.ping(node_hostname_domain, count=5)
    logger.info("Executing command: %s" % command)
    response = ShellUtils.execute_shell_command(command).stdout
    logger.debug(response)
    return not "Request timeout" in response


def is_node_sshable(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    node_username = NodeManager.node_obj.nodes[node_alias].username
    node_password = NodeManager.node_obj.nodes[node_alias].password
    command = 'sshpass -p "%s" ssh -tt %s@%s \'echo %s | sudo -S -s sh -c "date"\'' % (
        node_password, node_username, node_hostname_domain, node_password)
    logger.info("Executing command: %s" % command)
    response = ShellUtils.execute_shell_command(command).stderr
    logger.debug(response)
    return not ("Operation timed out" in response or "Connection refused" in response)


@retry(stop_max_delay=NODE_SSH_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def wait_for_node_to_be_sshable(node_alias):
    return is_node_sshable(node_alias)


@retry(stop_max_delay=NODE_PING_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def wait_for_node_to_be_pingable(node_alias):
    return is_node_pingable(node_alias)


def reboot_node(node_alias):
    node_hostname_domain = NodeManager.node_obj.get_node_hostname_domain_by_alias(node_alias)
    node_username = NodeManager.node_obj.nodes[node_alias].username
    node_password = NodeManager.node_obj.nodes[node_alias].password
    # command = 'sshpass -p "%s" ssh -tt %s@%s \'echo %s | sudo -S -s sh -c "nohup reboot &"\'' % (
    #     node_password, node_username, node_hostname_domain, node_password)
    command = 'sshpass -p "%s" ssh -tt %s@%s \'echo %s | sudo -S -s sh -c "nohup sleep 5m &"\' &' % (
        node_password, node_username, node_hostname_domain, node_password)
    logger.info("Executing reboot node %s: %s" % (node_alias, command))

    return ShellUtils.execute_shell_command(command)


@retry(stop_max_delay=NODE_GOING_DOWN_TIMEOUT, wait_fixed=5000, retry_on_result=_query_node_status)
def wait_for_node_to_go_down(node_alias):
    logger.info("Waiting for node '%s' to go down" % node_alias)
    return not is_node_up_and_running(node_alias)

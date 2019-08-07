import pytest
from chaostoolkit_nimble.actions.base.flows import chaos_user_actions
from chaostoolkit_nimble.actions.jio.media_plane_actions import MediaPlaneActions
from nimble.core.entity.components import Components
from nimble.core.entity.node_manager import NodeManager
from nimble.core.utils.shell_utils import ShellUtils


@pytest.mark.incremental
class TestJio():
    job_alias = "media_plane"
    job_user = "ambari-qa"

    @pytest.fixture(scope="session")
    def media_plane_actions(self, config_parser):
        return MediaPlaneActions(self.job_alias, config_parser, self.job_user)

    @pytest.fixture(scope="session", autouse=True)
    def clean_table(self, media_plane_actions):
        command = "hive -e 'drop table if exists %s.%s'" % (
            media_plane_actions.database_name, media_plane_actions.table_name)
        assert NodeManager.node_obj.execute_command_on_node(media_plane_actions.node_alias,
                                                            ShellUtils.su(self.job_user, command)).status

    def test_schedule_15min_job(self, media_plane_actions):
        media_plane_actions.schedule_15_min_job()

    def test_perform_15min_job_ha(self):
        exp_template_file = "process/exp.json"
        context = {"rand_dynamic_component": Components.MANAGEMENT.name,
                   "rand_dynamic_process_name": "media_plane_microapp1",
                   }
        chaos_user_actions.run_experiment(exp_template_file=exp_template_file, context=context)
        # chaos_user_actions.run_experiment(exp_file=OPTIONS_DICT["experimentsPath"])

    def test_validation_on_15min_job_ha(self, user_actions, media_plane_actions):
        user_actions.validate(media_plane_actions.validate_media_plane, self.job_alias)

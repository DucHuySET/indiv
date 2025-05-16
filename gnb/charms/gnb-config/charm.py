import sys
import traceback
from charms.osm import libansible
from charms.osm.sshproxy import SSHProxyCharm
from ops.main import main


class GNBCharm(SSHProxyCharm):
    def __init__(self, framework, key):
        super().__init__(framework, key)

        self.framework.observe(self.on.install, self.on_install)
        self.framework.observe(self.on.config_slice_action, self.on_config_slice_action)
        self.framework.observe(self.on.restart_gnb_action, self.on_restart_gnb_action)

    def on_install(self, event):
        self.unit.status = self.model.ActiveStatus("Ready")
        libansible.install_ansible_support()

    def on_config_slice_action(self, event):
        self._run_playbook(event, "config-slice.yaml", {
            "sst": event.params["sst"],
            "sd": event.params["sd"],
            "min_prb": event.params["min_prb"],
            "max_prb": event.params["max_prb"],
        })

    def on_restart_gnb_action(self, event):
        self._run_playbook(event, "restart-gnb.yaml", {})

    def _run_playbook(self, event, playbook, variables):
        try:
            config = self.model.config
            result = libansible.execute_playbook(
                f"playbooks/{playbook}",
                config["ssh-hostname"],
                config["ssh-username"],
                config["ssh-password"],
                variables,
            )
            event.set_results({"output": result})
        except Exception as e:
            err = traceback.format_exc()
            event.fail(message="Playbook failed: " + str(err))


if __name__ == "__main__":
    main(GNBCharm)

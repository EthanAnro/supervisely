
# What is Supervisely Agent?

Supervisely Agent is a tiny docker container that allows you to connect your computational resources (cloud server or PC) to the platform. You can run any plugin from web interface (for exmaple import, DTL, Neural Network training/inference/deploy).

After you run Agent on your computer, Agent will automatically connect your server to Supervisely platform. You will see this information in "Cluster" page.  


# How Agent works

This principal scheme illustrates how agent processes the task.

![](https://i.imgur.com/HW6iIXu.png)


# How to run Agent?

[Here](https://docs.supervise.ly/cluster/add_delete_node/add_delete_node/) you will find step-by-step guide about how to run Agent on your machine.

![](https://i.imgur.com/24zHYdz.png)

# How to monitor Agent information?

[Here](https://docs.supervise.ly/cluster/add_delete_node/add_delete_node/) you will find documentaion about how to monitor Agent status.

![](https://i.imgur.com/rgihpsQ.png)


# Environment variables:

#### Required:

- `AGENT_HOST_DIR`: directory, where agent stores user data. _(default: `$HOME/.supervisely-agent/$ACCESS_TOKEN`)_

- `SERVER_ADDRESS`: full server URL to connect to (e.g. `http://somehost:12345/agent`).

- `ACCESS_TOKEN`: unique string which allows the server to identify the agent.

- `DOCKER_REGISTRY`: list of used docker registry addresses. (e.g. `docker.deepsystems.io,docker.enterprise.supervise.ly`)

- `DOCKER_LOGIN`: list of login names for used docker registries (ordered as registries), e.g. `user,user`.

- `DOCKER_PASSWORD`: list of passwords for used docker registries (ordered as registries), e.g. `123,345`.


#### Optional: 

- `WITH_LOCAL_STORAGE`: whether to use local agent storage for long-term persistent storage of task results (learned model checkpoints, images generated by DTL) instead of uploading the results to the web instance storage. When this option is enabled, those results will be unavailable when the agent is not connected to the web instance. Do not enable this option when running the agent on transient machines, like hourly rented AWS instances, as the local data there will be lost as soon as your rented time ends. _(default: true)_

- `PULL_ALWAYS`: whether to always pull docker image from registry, or only if image with given name and tags not found localy. _(default: true)_

- `DEFAULT_TIMEOUTS`: whether to use default timeout configs or load from `/workdir/src/configs/timeouts_for_stateless.json` file. _(default: true)_

- `DELETE_TASK_DIR_ON_FINISH`: whether to remove task directory after the task finishes successfully. _(default: true)_

- `DELETE_TASK_DIR_ON_FAILURE`: whether to remove task directory after the task finishes with a failure. _(default: false)_

- `DOCKER_API_CALL_TIMEOUT`: timeout for Docker API calls, in seconds. _(default: 60)_
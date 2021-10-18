# Deploying a TSM Demo Environment
---
This repository contains a framework to automatically depoly K8s clusters and onboard those clusters to TSM in order to expedite the creation and destruction of TSM demo environments

Currently both EKS and AKS cluster creation and destruction is supported.

You can also use this tool to add and remove existing clusters to TSM declaritively


### Deploying a demo environment
---
A demo environment is specified using a yaml file.  Use the [tsm-demo-sample.yaml](sample-config/tsm-demo-sample.yaml) file found in `sample-config` as a starting point for your deployment.

This sample file deploys two clusters, one AKS cluster and one EKS cluster, then adds these two clusters to TSM.

The following disects the yaml sample in more detail.

#### Cluster Names and API keys
Specify the cluster names for your deployment.  In this example specify the cluster name for your AKS cluster and your EKS cluster.  Also specify the API keys for Azure, AWS and TSM.  Please note that `AWS_SESSION_TOKEN` is optional, however if your keys have been provided through CloudGate then this is required.  This sample uses yaml anchors(&) and aliases(*) which act like variables that can be reused throughout the yaml file. 

```yaml
CLUSTER_NAME_AKS_WEST: &cluster_name_aks_west ''
CLUSTER_NAME_EKS_EAST: &cluster_name_eks_east ''


AZURE_APP_ID: &azure_app_id ''
AZURE_PASSWORD: &azure_password '' 

AWS_ACCESS_KEY_ID: &aws_access_key_id ''
AWS_SECRET_ACCESS_KEY: &aws_secret_access_key ''
AWS_SESSION_TOKEN: &aws_session_token '' #optional.  Please specifiy if using CloudGate

TSM_API_SERVER: &tsm_api_server ''
TSM_API_KEY: &tsm_api_key ''
```

### Tasks
The automation works by executing tasks in sequential order.  In this example `TASKS_CREATE` contains a list of tasks to be executed.  First an AKS cluster is provisioned followd by an EKS cluster.  Next, the AKS cluster is added to TSM followed by the EKS cluster added to TSM.  Please note that `TASKS_DESTROY` contains a list of tasks that are executed in the reverse order in order to deprovision what was created in `TASKS_CREATE`.  Each task has a corresponding configuration that provides the details for that task.  We'll discuss the details of each task in more detail 

```yaml
TASKS_CREATE: &create_task
  - aks: akswest-cfg
  - eks: ekseast-cfg
  - tsmCluster: tsmakswest-cfg
  - tsmCluster: tsmekseast-cfg


TASKS_DESTROY: &destroy_task
  - tsmCluster: tsmakswest-cfg
  - tsmCluster: tsmekseast-cfg
  - aks: akswest-cfg
  - eks: ekseast-cfg
```
To create the demo environment uncomment the three lines under `# create`.  To destroy the demo environment uncomment the three lines under `# destroy`.  These sections are mutually exclusive...make sure only one is uncommented at any given time.

```yaml
# create
#CLUSTER_ACTION: &cluster_action 'CREATE'
#TSM_ACTION: &tsm_action 'ADD'  
#TASKS: *create_task
 

# destroy
#CLUSTER_ACTION: &cluster_action 'DESTROY'
#TSM_ACTION: &tsm_action 'REMOVE'  
#TASKS: *destroy_task
```


### AKS Task  
The following is an example of the configuration options for the AKS task.  `ACTION` can be either `CREATE` or `DESTROY`

```yaml
akswest-cfg:
  ACTION: *cluster_action
  AKS_CLUSTER_NAME: *cluster_name_aks_west
  AZURE_REGION: 'West US 2'
  AZURE_APP_ID: *azure_app_id
  AZURE_PASSWORD: *azure_password
  AKS_NUM_NODES: 2
  AKS_NODE_SIZE: 'Standard_D4_v3'
  AKS_K8S_VERSION: '1.20.9'
```
Please note that in order to provision an AKS cluster you'll need to login to azure first using the azure command line utility `az`
```shell
$ az login
```

### EKS Task
The following is an example of the configuration options for the EKS task.  `ACTION` can be either `CREATE` or `DESTROY`

```yaml
ekseast-cfg:
  ACTION: *cluster_action
  EKS_CLUSTER_NAME: *cluster_name_eks_east
  EKS_NUM_NODES: 3
  EKS_NODE_SIZE: "t2.xlarge"
  EKS_K8S_VERSION: "1.20"
  AWS_REGION: 'us-east-2'
  AWS_ACCESS_KEY_ID: *aws_access_key_id
  AWS_SECRET_ACCESS_KEY: *aws_secret_access_key
  AWS_SESSION_TOKEN: *aws_session_token
```
Please note the `AWS_SESSION_TOKEN` is optional and if not in use needs to be removed.

### tsmCluster Task
The following is an example configuration for the tsmCluster task.  This task adds or removes existing clusters to TSM. Please note that this example is EKS specific and therefore the additional environment variables containing the AWS keys and tokens are required.  For AKS clusters these additional environment variables are not required and can be removed in the task configuration.  `ACTION` can be either `ADD` or `REMOVE`

```yaml
tsmekseast-cfg:
  ACTION: *tsm_action
  TSM_CLUSTER_NAME: *cluster_name_eks_east
  TSM_API_SERVER: *tsm_api_server
  TSM_API_KEY: *tsm_api_key
  ENV_VARIABLES:
    - AWS_ACCESS_KEY_ID: *aws_access_key_id
    - AWS_SECRET_ACCESS_KEY: *aws_secret_access_key
    - AWS_SESSION_TOKEN: *aws_session_token
```

### Building and Destroying your TSM demo environment
---
A docker container has been created with all the dependancies so that you can easily build and destroy your TSM demo environment. Please follow these steps to build and destroy your demo environment.

### Build

1. Save and modify the sample [tsm-demo-sample.yaml](sample-config/tsm-demo-sample.yaml) file to your local system.  You can rename the file if you wish.  Please use the documentation above to modify the file accordingly.  Make sure to uncomment the following section if not uncommented already
    ```yaml
    # create
    CLUSTER_ACTION: &cluster_action 'CREATE'
    TSM_ACTION: &tsm_action 'ADD'  
    TASKS: *create_task
    ```

2. Pull the docker image from the following repository.  You will need to be on VPN in order to pull the image.
    ```shell
    $ docker pull harbor.tek8s.com/tsm/tsmdeploy
    ```

3. Run the image as follows
    ```shell
    $ docker run -it --rm -v <path to your .azure directory>:/root/.azure -v <path to your .kube directory>:/root/.kube -v <path to the directory containing your yaml config file>:/mnt/config  harbor.tek8s.com/tsm/tsmdeploy <yaml config file>
    ```
    Here is an example:
    ```shell
    $ docker run -it --rm -v ~/.azure:/root/.azure -v ~/.kube:/root/.kube -v ~/tsm-demo-configs:/mnt/config  harbor.tek8s.com/tsm/tsmdeploy tsm-demo-sample.yaml
    ```
    At the end of this step you should have your clusters provisioned and added to TSM.

### Destroy

1.  Modify your yaml file and comment the `# create` section and uncomment the `# destroy` section.
    ```yaml
    # create
    #CLUSTER_ACTION: &cluster_action 'CREATE'
    #TSM_ACTION: &tsm_action 'ADD'  
    #TASKS: *create_task
    

    # destroy
    CLUSTER_ACTION: &cluster_action 'DESTROY'
    TSM_ACTION: &tsm_action 'REMOVE'  
    TASKS: *destroy_task
    ```

2. Run the docker image again as you did in `Build` step 3.


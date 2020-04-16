#!/bin/bash
OLD_TASK_IDS=$(aws ecs list-tasks --cluster $cluster_id --desired-status RUNNING  | egrep "task/" | sed -E "s/.*task\/(.*)\"/\1/" | sed -z 's/\n/ /g')
IFS=', ' read -r -a array <<< "$OLD_TASK_IDS"
echo $cluster_id
echo $OLD_TASK_IDS
exit 1
for element in "${array[@]}"
do
    aws ecs stop-task --cluster $cluster_id --task ${element}
done

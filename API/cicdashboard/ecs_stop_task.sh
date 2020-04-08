#!/bin/bash
OLD_TASK_IDS=$(aws ecs list-tasks --cluster cic-production-dashboard --desired-status RUNNING  | egrep "task/" | sed -E "s/.*task\/(.*)\"/\1/" | sed -z 's/\n/ /g')
IFS=', ' read -r -a array <<< "$OLD_TASK_IDS"
for element in "${array[@]}"
do
    aws ecs stop-task --cluster cic-production-dashboard --task ${element}
done

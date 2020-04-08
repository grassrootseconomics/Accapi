#!/bin/bash
DB_USER=`aws secretsmanager get-secret-value --secret-id /prod/dbcredentials | jq --raw-output .SecretString | jq -r ."username"`
DB_PASS=`aws secretsmanager get-secret-value --secret-id /prod/dbcredentials | jq --raw-output .SecretString | jq -r ."password"`
DB_HOST=`aws secretsmanager get-secret-value --secret-id /prod/dbcredentials | jq --raw-output .SecretString | jq -r ."host"`

docker build --no-cache -t cic-dashboard-api-prod --build-arg DB_USER=$DB_USER --build-arg DB_PASS=$DB_PASS  --build-arg DB_HOST=$DB_HOST . 

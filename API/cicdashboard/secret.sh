#!/bin/bash
DBPASS=`aws secretsmanager get-secret-value --secret-id /prod/dbcredentials | jq --raw-output .SecretString | jq -r ."password"`
DBUSER=`aws secretsmanager get-secret-value --secret-id /prod/dbcredentials | jq --raw-output .SecretString | jq -r ."username"`
HOST=`aws secretsmanager get-secret-value --secret-id /prod/dbcredentials | jq --raw-output .SecretString | jq -r ."host"`

export DBPASS
export DBUSER
export HOST

#!/usr/bin/env bash

# usage:
# bash automation/build_deploy.bash user-auth-core user_auth_core dev

# Variables
BUCKET=oep-deployment
PACKAGE=$1
MODULE=$2
ENV=$3

# Clean
rm -rf package
rm -rf ${PACKAGE}/function.zip

# Dependencies
pip install --target ./package -r ${PACKAGE}/requirements.txt
cp -r binaries/* package/

# Package
cd ${PACKAGE}
cd ../package
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
zip -gr function.zip ${MODULE}

# AWS
aws s3 cp function.zip s3://${BUCKET} --profile oep
aws lambda update-function-code \
--function-name ${ENV}_${MODULE} \
--region ap-southeast-2 \
--s3-bucket ${BUCKET} \
--s3-key function.zip \
--profile oep

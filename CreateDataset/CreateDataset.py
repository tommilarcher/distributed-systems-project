import sys
import os
import json
import time
import boto3


class StatusIndicator:

    def __init__(self):
        self.previous_status = None
        self.need_newline = False

    def update(self, status):
        if self.previous_status != status:
            if self.need_newline:
                sys.stdout.write("\n")
            sys.stdout.write(status + " ")
            self.need_newline = True
            self.previous_status = status
        else:
            sys.stdout.write("util")
            self.need_newline = True
        sys.stdout.flush()

    def end(self):
        if self.need_newline:
            sys.stdout.write("\n")


def get_or_create_iam_role( role_name ):

    iam = boto3.client("iam")

    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "forecast.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
            }
        ]
    }

    try:
        create_role_response = iam.create_role(
            RoleName = role_name,
            AssumeRolePolicyDocument = json.dumps(assume_role_policy_document)
        )
        role_arn = create_role_response["Role"]["Arn"]
        print("Created", role_arn)
    except iam.exceptions.EntityAlreadyExistsException:
        print("The role " + role_name + " exists, ignore to create it")
        role_arn = boto3.resource('iam').Role(role_name).arn

    print("Attaching policies")

    iam.attach_role_policy(
        RoleName = role_name,
        PolicyArn = "arn:aws:iam::aws:policy/AmazonForecastFullAccess"
    )

    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess',
    )

    print("Waiting for a minute to allow IAM role policy attachment to propagate")
    time.sleep(60)

    print("Done.")
    return role_arn



def lambda_handler(event, context):
    # global settings
    bucket_name = "tommi-stockprices"
    filename = "stock-prices.csv"
    project = "stockprices"
    region = "us-east-1"
    datasetName = project + "_ds"
    datasetGroupName = project + "_dsg"
    s3DataPath = "s3://" + bucket_name + "/" + filename
    DATASET_FREQUENCY = "H"
    TIMESTAMP_FORMAT = "yyyy-MM-dd hh:mm:ss"

    session = boto3.Session(region_name=region)
    forecast = session.client(service_name="forecast")
    forecastquery = session.client(service_name="forecastquery")

    create_dataset_group_response = forecast.create_dataset_group(
        DatasetGroupName=datasetGroupName,
        Domain="CUSTOM",
    )
    datasetGroupArn = create_dataset_group_response["DatasetGroupArn"]
    forecast.describe_dataset_group(DatasetGroupArn=datasetGroupArn)

    # Specify the schema of your dataset here. Make sure the order of columns matches the raw data files.
    schema = {
        "Attributes": [
            {"AttributeName": "timestamp", "AttributeType": "timestamp"},
            {"AttributeName": "target_value", "AttributeType": "float"},
            {"AttributeName": "item_id", "AttributeType": "string"},
        ]
    }

    response = forecast.create_dataset(
        Domain="CUSTOM",
        DatasetType="TARGET_TIME_SERIES",
        DatasetName=datasetName,
        DataFrequency=DATASET_FREQUENCY,
        Schema=schema,
    )

    datasetArn = response["DatasetArn"]
    forecast.describe_dataset(DatasetArn=datasetArn)

    forecast.update_dataset_group(DatasetGroupArn=datasetGroupArn, DatasetArns=[datasetArn])

    role_name = "forecastRole"
    role_arn = get_or_create_iam_role(role_name=role_name)

    datasetImportJobName = "EP_DSIMPORT_JOB_TARGET"
    ds_import_job_response = forecast.create_dataset_import_job(
        DatasetImportJobName=datasetImportJobName,
        DatasetArn=datasetArn,
        DataSource={"S3Config": {"Path": s3DataPath, "RoleArn": role_arn}},
        TimestampFormat=TIMESTAMP_FORMAT,
    )

    ds_import_job_arn = ds_import_job_response["DatasetImportJobArn"]
    print(ds_import_job_arn)

    status_indicator = StatusIndicator()

    while True:
        status = forecast.describe_dataset_import_job(
            DatasetImportJobArn=ds_import_job_arn
        )["Status"]
        status_indicator.update(status)
        if status in ("ACTIVE", "CREATE_FAILED"):
            break
        time.sleep(10)

    status_indicator.end()

    forecast.describe_dataset_import_job(DatasetImportJobArn=ds_import_job_arn)

    return {
        "dataset_group_arn": datasetGroupArn
    }
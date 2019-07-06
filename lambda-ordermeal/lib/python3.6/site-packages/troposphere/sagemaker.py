# Copyright (c) 2012-2018, Mark Peek <mark@peek.org>
# All rights reserved.
#
# See LICENSE file for full license.

from . import AWSObject, AWSProperty, Tags
from .validators import integer


class Endpoint(AWSObject):
    resource_type = "AWS::SageMaker::Endpoint"

    props = {
        'EndpointName': (str, False),
        'EndpointConfigName': (str, True),
        'Tags': (Tags, True)
    }


class ProductionVariant(AWSProperty):
    props = {
        'ModelName': (str, True),
        'VariantName': (str, True),
        'InitialInstanceCount': (integer, True),
        'InstanceType': (str, True),
        'InitialVariantWeight': (float, True)
    }


class EndpointConfig(AWSObject):
    resource_type = "AWS::SageMaker::EndpointConfig"

    props = {
        'EndpointConfigName': (str, False),
        'ProductionVariants': ([ProductionVariant], True),
        'KmsKeyId': (str, False),
        'Tags': (Tags, True)
    }


class ContainerDefinition(AWSProperty):
    props = {
        'ContainerHostname': (str, False),
        'Environment': (dict, False),
        'ModelDataUrl': (str, False),
        'Image': (str, True)
    }


class VpcConfig(AWSProperty):
    props = {
        'Subnets': ([str], True),
        'SecurityGroupIds': ([str], True)
    }


class Model(AWSObject):
    resource_type = "AWS::SageMaker::Model"

    props = {
        'ExecutionRoleArn': (str, True),
        'PrimaryContainer': (ContainerDefinition, True),
        'Containers': ([ContainerDefinition], False),
        'ModelName': (str, False),
        'VpcConfig': (VpcConfig, False),
        'Tags': (Tags, False)
    }


class NotebookInstanceLifecycleHook(AWSProperty):
    props = {
        'Content': (str, False)
    }


class NotebookInstanceLifecycleConfig(AWSObject):
    resource_type = "AWS::SageMaker::NotebookInstanceLifecycleConfig"

    props = {
        'NotebookInstanceLifecycleConfigName': (str, False),
        'OnCreate': ([NotebookInstanceLifecycleHook], False),
        'OnStart': ([NotebookInstanceLifecycleHook], False)
    }


class NotebookInstance(AWSObject):
    resource_type = "AWS::SageMaker::NotebookInstance"

    props = {
        'KmsKeyId': (str, False),
        'DirectInternetAccess': (str, False),
        'SubnetId': (str, False),
        'NotebookInstanceName': (str, False),
        'InstanceType': (str, True),
        'LifecycleConfigName': (str, False),
        'SecurityGroupIds': ([str], False),
        'RoleArn': (str, True),
        'Tags': (Tags, False)
    }

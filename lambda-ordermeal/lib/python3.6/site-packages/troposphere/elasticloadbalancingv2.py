# Copyright (c) 2012-2013, Mark Peek <mark@peek.org>
# All rights reserved.
#
# See LICENSE file for full license.

from . import AWSObject, AWSProperty, If, Tags
from .validators import (
    elb_name, exactly_one, network_port,
    tg_healthcheck_port, integer,
    one_of
)


class LoadBalancerAttributes(AWSProperty):
    props = {
        'Key': (str, False),
        'Value': (str, False)
    }


class Certificate(AWSProperty):
    props = {
        'CertificateArn': (str, False)
    }


class RedirectConfig(AWSProperty):
    # https://docs.aws.amazon.com/
    # AWSCloudFormation/latest/UserGuide/
    # aws-properties-elasticloadbalancingv2-listener-redirectconfig.html
    props = {
        'Host': (str, False),
        'Path': (str, False),
        'Port': (str, False),
        'Protocol': (str, False),
        'Query': (str, False),
        'StatusCode': (str, True),
    }

    def validate(self):
        one_of(self.__class__.__name__,
               self.properties,
               'StatusCode',
               ['HTTP_301', 'HTTP_302'])


class FixedResponseConfig(AWSProperty):
    props = {
        'ContentType': (str, False),
        'MessageBody': (str, False),
        'StatusCode': (str, False),
    }

    def validate(self):
        one_of(self.__class__.__name__,
               self.properties,
               'ContentType',
               ['text/plain', 'text/css', 'text/html',
                'application/javascript', 'application/json'])


class Action(AWSProperty):
    props = {
        'Type': (str, True),
        'TargetGroupArn': (str, False),
        'RedirectConfig': (RedirectConfig, False),
        'FixedResponseConfig': (FixedResponseConfig, False)
    }

    def validate(self):
        one_of(self.__class__.__name__,
               self.properties,
               'Type',
               ['forward', 'redirect', 'fixed-response'])

        def requires(action_type, prop):
            if self.properties.get('Type') == action_type and \
                    prop not in self.properties:
                raise ValueError(
                    'Type "%s" requires definition of "%s"' % (
                        action_type, prop
                    )
                )

            if prop in self.properties and \
                    self.properties.get('Type') != action_type:
                raise ValueError(
                    'Definition of "%s" allowed only with '
                    'type "%s", was: "%s"' % (
                        prop, action_type, self.properties.get('Type')
                    )
                )

        requires('forward', 'TargetGroupArn')
        requires('redirect', 'RedirectConfig')
        requires('fixed-response', 'FixedResponseConfig')


class Condition(AWSProperty):
    props = {
        'Field': (str, True),
        'Values': ([str], True)
    }


class Matcher(AWSProperty):
    props = {
        'HttpCode': (str, False)
    }


class SubnetMapping(AWSProperty):
    props = {
        'AllocationId': (str, True),
        'SubnetId': (str, True)
    }


class TargetGroupAttribute(AWSProperty):
    props = {
        'Key': (str, False),
        'Value': (str, False)
    }


class TargetDescription(AWSProperty):
    props = {
        'AvailabilityZone': (str, False),
        'Id': (str, True),
        'Port': (network_port, False)
    }


class Listener(AWSObject):
    resource_type = "AWS::ElasticLoadBalancingV2::Listener"

    props = {
        'Certificates': ([Certificate], False),
        'DefaultActions': ([Action], True),
        'LoadBalancerArn': (str, True),
        'Port': (network_port, True),
        'Protocol': (str, True),
        'SslPolicy': (str, False)
    }


class ListenerCertificate(AWSObject):
    resource_type = "AWS::ElasticLoadBalancingV2::ListenerCertificate"

    props = {
        'Certificates': ([Certificate], True),
        'ListenerArn': (str, True),
    }


class ListenerRule(AWSObject):
    resource_type = "AWS::ElasticLoadBalancingV2::ListenerRule"

    props = {
        'Actions': ([Action], True),
        'Conditions': ([Condition], True),
        'ListenerArn': (str, True),
        'Priority': (integer, True)
    }


TARGET_TYPE_INSTANCE = 'instance'
TARGET_TYPE_IP = 'ip'


class TargetGroup(AWSObject):
    resource_type = "AWS::ElasticLoadBalancingV2::TargetGroup"

    props = {
        'HealthCheckIntervalSeconds': (integer, False),
        'HealthCheckPath': (str, False),
        'HealthCheckPort': (tg_healthcheck_port, False),
        'HealthCheckProtocol': (str, False),
        'HealthCheckTimeoutSeconds': (integer, False),
        'HealthyThresholdCount': (integer, False),
        'Matcher': (Matcher, False),
        'Name': (str, False),
        'Port': (network_port, True),
        'Protocol': (str, True),
        'Tags': ((Tags, list), False),
        'TargetGroupAttributes': ([TargetGroupAttribute], False),
        'Targets': ([TargetDescription], False),
        'TargetType': (str, False),
        'UnhealthyThresholdCount': (integer, False),
        'VpcId': (str, True),
    }


class LoadBalancer(AWSObject):
    resource_type = "AWS::ElasticLoadBalancingV2::LoadBalancer"

    props = {
        'LoadBalancerAttributes': ([LoadBalancerAttributes], False),
        'Name': (elb_name, False),
        'Scheme': (str, False),
        'IpAddressType': (str, False),
        'SecurityGroups': (list, False),
        'SubnetMappings': ([SubnetMapping], False),
        'Subnets': (list, False),
        'Tags': ((Tags, list), False),
        'Type': (str, False),
    }

    def validate(self):
        conds = [
            'SubnetMappings',
            'Subnets',
        ]

        def check_if(names, props):
            validated = []
            for name in names:
                validated.append(name in props and isinstance(props[name], If))
            return all(validated)

        if check_if(conds, self.properties):
            return

        exactly_one(self.__class__.__name__, self.properties, conds)

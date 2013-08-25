#!/usr/bin/env python

import os
import sha
import requests
import time
import urllib2
from datetime import timedelta
from xml.dom import minidom
from lxml import etree
from jobs import AbstractJob


class Leaf(AbstractJob):

    def __init__(self, conf):
        self.username = conf['username']
        self.password = conf['password']
        self.base_url = conf['base_url']
        self.interval = conf['interval']

    def get(self):
        cw = Carwings(self.username, self.password, self.base_url)
        return cw.get_data()


class Carwings():
    vs_ns = {'ns4': 'urn:com:airbiquity:smartphone.vehicleservice:v1',
             'ns3': 'urn:com:hitachi:gdc:type:vehicle:v1',
             'ns2': 'urn:com:hitachi:gdc:type:portalcommon:v1'}

    us_ns = {'ns3': 'urn:com:hitachi:gdc:type:report:v1',
             'ns2': 'urn:com:airbiquity:smartphone.userservices:v1'}

    def __init__(self, username, password, base_url):
        self.base_url = base_url
        self.username = username
        self.password = password
        self._connect()

    def _connect(self):
        self.handler = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(self.handler)

    def _post_xml(self, service, xml_data, suppress_response=False):
        data = xml_data.toxml()
        request = urllib2.Request("%s%s" % (self.base_url, service), data,
                                  {'Content-Type': 'text/xml',
                                   'User-Agent':
                                   'NissanLEAF/1.40'})
        response = self.opener.open(request)
        response_data = response.read()
        response.close()
        return response_data

    def get_data(self):
        d = {'SmartphoneLoginInfo':
             {'UserLoginInfo':
              {'userId': self.username,
               'userPassword': self.password},
              'DeviceToken': 'DUMMY%f' % time.time(),
              'UUID': sha.sha("carwings_api:%s" % self.username).hexdigest(),
              'Locale': 'US',
              'AppVersion': '1.40',
              'SmartphoneType': 'IPHONE'},
             'SmartphoneOperationType':
             'SmartphoneLatestBatteryStatusRequest'}
        ns = {'ns2': self.us_ns['ns2']}
        xml = self._dict_to_xml(d,
                                'ns2:SmartphoneLogin' +
                                'WithAdditionalOperationRequest', ns)
        response_data = self._post_xml('/userService', xml)
        if self._check_login(response_data):
            self._request_update(self._get_vin(response_data))
            return self._parse_xml(response_data)
        return None

    def _check_login(self, data):
        self.logged_in = True if not 'Error' in data else False
        return self.logged_in

    def _request_update(self, vin):
        d = {'ns3:BatteryStatusCheckRequest':
            {'ns3:VehicleServiceRequestHeader': {'ns2:VIN': vin}}}
        xml = self._dict_to_xml(
            d, 'ns4:SmartphoneRemoteBatteryStatusCheckRequest', self.vs_ns)
        self._post_xml('/vehicleService', xml)

    def _get_vin(self, data):
        ns = {'ns3': self.vs_ns['ns3']}
        tree = etree.fromstring(data)
        vin = tree.xpath('//Vin', namespaces=ns).pop().text
        return vin

    def _parse_xml(self, xml):
        ns3 = {'ns3': 'urn:com:hitachi:gdc:type:report:v1'}
        tree = etree.fromstring(xml)
        batteryCapacity = float(tree.xpath('//ns3:BatteryCapacity',
                                           namespaces=ns3).pop().text)
        return {
            'updated': tree.xpath('//ns3:OperationDateAndTime',
                                  namespaces=ns3).pop().text,
            'charger': self._get_charge_status(ns3, tree),
            'range': {
                'acoff':
                round(float(tree.xpath('//ns3:CruisingRangeAcOff',
                                       namespaces=ns3).pop().text) / 1000),
                'acon':
                round(float(tree.xpath('//ns3:CruisingRangeAcOn',
                                       namespaces=ns3).pop().text) / 1000),
            },
            'battery': {
                # As the battery degrade, 12 may not be 100%
                'capacity': float(100) / float(12) * batteryCapacity,
                'remaining':
                round(float(tree.xpath('//ns3:BatteryRemainingAmount',
                                       namespaces=ns3).pop().text) * 100
                      / batteryCapacity)
            }
        }

    def _get_charge_status(self, namespaces, tree):
        if tree.xpath('//ns3:TimeRequiredToFull200', namespaces=namespaces):
            hourFinished = tree.xpath('//ns3:HourRequiredToFull',
                                      namespaces=namespaces).pop().text
            minuteFinished = tree.xpath('//ns3:MinutesRequiredToFull',
                                        namespaces=namespaces).pop().text
            donein = hourFinished + ':' + minuteFinished.zfill(2)
        return {
            'plugstate': 'Tilkoblet'
            if tree.xpath('//ns3:PluginState',
                          namespaces=namespaces).pop().text ==
            'CONNECTED' else 'Ikke tilkoblet',
            'status': 'Lader ('+str(donein)+')'
            if tree.xpath('//ns3:BatteryChargingStatus',
                          namespaces=namespaces).pop().text ==
            'NORMAL_CHARGING' else 'Lader ikke',
        }

    def _dict_to_xml(self, data, root_name, namespaces=None):
        doc = minidom.Document()
        root = doc.createElement(root_name)

        if namespaces:
            for ns_name, ns_uri in namespaces.iteritems():
                root.setAttribute('xmlns:%s' % ns_name, ns_uri)
                doc.appendChild(root)
                self._xml_add_dict(data, root, doc)
        return doc

    def _xml_add_dict(self, data, root, doc):
        for name, value in data.iteritems():
            if isinstance(value, list):
                self._xml_add_list(value, name, root, doc)
            else:
                self._xml_add_item(value, name, root, doc)

    def _xml_add_list(self, data, name, root, doc):
        for item in data:
            self._xml_add_item(item, name, root, doc)

    def _xml_add_item(self, data, name, root, doc):
        if isinstance(data, dict):
            node = doc.createElement(name)
            root.appendChild(node)
            self._xml_add_dict(data, node, doc)
        else:
            if name.startswith('@'):
                root.setAttribute(name[1:], data)
            else:
                node = doc.createElement(name)
                text = doc.createTextNode(str(data))
                node.appendChild(text)
                root.appendChild(node)

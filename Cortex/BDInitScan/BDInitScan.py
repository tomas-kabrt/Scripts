#!/usr/bin/env python3
# encoding: utf-8

# BDInitScan
# Author: Tomas Kabrt

from cortexutils.responder import Responder
import requests
import base64
import uuid

class BDInitScan(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.Bitdefender_Url = self.get_param('config.Bitdefender_Url', None, 'Bitdefender URL is Missing')
        self.Bitdefender_API_Key = self.get_param('config.Bitdefender_API_Key', None, 'Bitdefender API Key is Missing')
        self.Target_Device_ID = self.get_param('data.customFieldValues.bitdefender-computer-id', None, 'Error loading customField bitdefender-computer-id')

    def run(self):
        h = {
            'content-type': 'application/json',
            'Version': '9.1',
            'Authorization': 'Basic ' + (base64.b64encode(bytes(self.Bitdefender_API_Key, 'utf-8')+bytes(':', 'utf-8'))).decode('utf-8')
        }

        j = {
            'params': {
                'targetIds': [ self.Target_Device_ID ],
                'type': 2,
                'name': 'The Hive Generated scan'
            },
            'jsonrpc': '2.0',
            'method': 'createScanTask',
            'id': str(uuid.uuid4())
        }
        print(self.Target_Device_ID)

        r = requests.post(self.Bitdefender_Url, headers=h, json=j)

        if r.status_code == 200:
            self.report({'message': 'Scan task was succesfully requested!'})
        else:
            self.error({'message': r.status_code})


if __name__ == '__main__':
    BDInitScan().run()

#!/usr/bin/env python

import http.client
import json
import xml.etree.ElementTree as ET

class Jenkins:
    def __init__(self, host):
        self.host = host

    def show(self):
        conn = http.client.HTTPConnection(self.host)
        conn.request('GET', '/api/json')

        res = conn.getresponse()
        rawdata = res.read()

        jsondata = json.loads(rawdata.decode('utf-8'))

        jobs = [x['name'] for x in jsondata['jobs']]
        conn.close()

        return jobs

    def build(self, job):
        conn = http.client.HTTPConnection(self.host)
        conn.request('POST', '/job/%s/build'%job)

        conn.getresponse()
        conn.close()

    def lastbuiltbranch(self, job, buildnumber):
        conn = http.client.HTTPConnection(self.host)
        conn.request('GET', '/job/%s/%d/api/json'%(job, buildnumber))

        res = conn.getresponse()
        rawdata = res.read()

        jsondata = json.loads(rawdata.decode('utf-8'))
        actions = jsondata['actions']

        for action in actions:
            try:
                branch = action['lastBuiltRevision']['branch'][0]['name']
            except KeyError:
                pass

        conn.close()
        return branch

    def getbranch(self, job):
        conn = http.client.HTTPConnection(self.host)
        conn.request('GET', '/job/%s/config.xml'%job)

        res = conn.getresponse()
        rawdata = res.read()

        xml = ET.fromstring(rawdata.decode('utf-8'))
        tree = ET.ElementTree(xml)

        for element in tree.iter("hudson.plugins.git.BranchSpec"):
            name = element.find('name')
            break

        conn.close()
        return name.text

    def setbranch(self, job, branch):
        conn = http.client.HTTPConnection(self.host)
        conn.request('GET', '/job/%s/config.xml'%job)

        res = conn.getresponse()
        rawdata = res.read()
        conn.close()

        xml = ET.fromstring(rawdata.decode('utf-8'))

        for element in xml.iter("hudson.plugins.git.BranchSpec"):
            name = element.find('name')
            name.text = 'feature/test'
            break

        payload = ET.tostring(xml, encoding='utf-8', method='xml')
        headers = {
                'Content-Type': 'application/xml'
                }

        conn = http.client.HTTPConnection(self.host)
        conn.request('POST', '/job/%s/config.xml'%job, payload, headers)

        res = conn.getresponse()
        conn.close()


if __name__ == '__main__':
    j = Jenkins('localhost:8080')
    j.show()
    j.build('dev-test-api-server')
    j.getbranch('dev-test-api-server')
    j.setbranch('dev-test-api-server', "develop")


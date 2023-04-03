""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import requests
from connectors.core.connector import ConnectorError, get_logger
from integrations.crudhub import make_request

logger = get_logger('cuckoo')


class Cuckoo(object):
    def __init__(self, config):
        self.log = logger
        self._server_url = config.get('server_ip')
        self._port = config.get('port')
        self._url = '{0}:{1}'.format(self._server_url, self._port)
        if not self._url.startswith('http://'):
            self._url = 'https://' + self._url
        self._header = { "Authorization": "Bearer " + config.get('api_token') }

    def submit_sample(self, file_data):
        endpoint = self._url + "/tasks/create/file"
        files = {'file': file_data}
        try:
            response = requests.post(endpoint, headers=self._header, files=files, verify=False)
            self.log.info("response_content {0}".format(response.content))
            if response.ok:
                return response.json()
            else:
                self.log.debug("Exception in submit_sample: {}".format(str(response.status_code)))
                raise ConnectorError("Error in submit_sample")
        except Exception as err:
            self.log.exception('submit_sample: Exception occurred {}'.format(str(err)))
            raise ConnectorError('submit_sample: Exception occurred {}'.format(str(err)))

    def detonate_file(self, params):
        try:
            file_iri = params.get('file')
            self.log.debug("file_iri is {}".format(file_iri))
            if isinstance(file_iri, bytes):
                file_iri = file_iri.decode("utf-8")
            file_data = make_request(file_iri, "GET")
            return self.submit_sample(file_data)
        except Exception as err:
            self.log.exception('detonate_file: Exception occurred {}'.format(str(err)))
            raise ConnectorError('detonate_file: Exception occurred {}'.format(str(err)))

    '''
    This function submits the URL for detonation on Cuckoo Sandbox for analysis.
    '''

    def submit_url(self, params):
        url = "{0}".format(params.get('url'))
        data = {'url': url}
        endpoint_url = self._url + "/tasks/create/url"

        try:
            response = requests.post(endpoint_url, headers=self._header, data=data, verify=False)
            self.log.info("response_content {0}".format(response.json()))
            if response.ok:
                return response.json()
            else:
                self.log.debug("Exception in submit_url : Status_code {}".format(str(response.status_code)))
                raise ConnectorError("Error in submit_url")
        except Exception as err:
            self.log.exception('submit_url: Exception occurred {}'.format(err))
            raise ConnectorError('submit_url: Exception occurred {}'.format(err))

    '''
    This function retrieves the report based on the Task ID of the submitted sample to the Cuckoo.
    '''

    def get_report(self, params):
        task_id = params.get('taskid')
        if isinstance(task_id, bytes):
            task_id = task_id.decode("utf-8")
        endpoint = self._url + "/tasks/report/{0}".format(task_id)
        self.log.info("Endpoint URL : {0}".format(endpoint))
        try:
            response = requests.get(endpoint, headers=self._header, verify=False)
            if response.ok:
                return response.json()
            else:
                self.log.debug("Error in get_report: Status_code : {}".format(str(response.status_code)))
                self.log.error("Error in retrieving the report for the taskid:{0}".format(task_id))
                raise ConnectorError("Error in Get_Report")
        except Exception as e:
            self.log.exception('get_report:Exception occurred: {}'.format(str(e)))
            raise ConnectorError(e)

    def _check_health(self):
        endpoint = self._url + "/cuckoo/status"
        try:
            response = requests.get(endpoint, headers=self._header, verify=False)
            if response.json()["version"]:
                return True
            else:
                self.log.error("_check_health: Failed Please check the Configuration: Status_code : {}".format(
                    str(response.status_code)))
                raise ConnectorError("Invalid Configuration Parameters. Please check and try again.")
        except Exception as e:
            self.log.exception("_check_health() Exception is: %s".format(e))
            raise ConnectorError("Invalid Configuration Parameters. Please check and try again.")

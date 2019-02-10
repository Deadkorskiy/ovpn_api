import os
import sys
SRC_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.append(SRC_ROOT)

from src.bootstrap import bootstrap
bootstrap()

import requests
from src.tests.base import BaseTestCase
from src.settings.settings import TESTS_API_ADDRESS, TESTS_API_TOKEN
from src.settings import settings
import uuid
import logging


logger = logging.getLogger(__file__)


headers = {'Api-Key': TESTS_API_TOKEN}


class APIOpenVPNTestCase(BaseTestCase):

    client_name_prefix = 'UNITTEST_'

    def test_build(self):
        """
        Test build
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())
        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['errors_occured'] == []
        assert response.json()['data']['client_common']
        assert response.json()['data']['client_crt']
        assert response.json()['data']['client_name']  == client_name
        assert response.json()['data']['server_ca']
        assert response.json()['data']['server_ta_key']
        logger.debug(response.text)

    def test_twice_build(self):
        """
        Test twice build
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())
        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)

        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        assert response.json()['errors_occured'] == []
        assert response.json()['data']['client_common']
        assert response.json()['data']['client_crt']
        assert response.json()['data']['client_name']  == client_name
        assert response.json()['data']['server_ca']
        assert response.json()['data']['server_ta_key']


    def test_build_reversed_name(self):
        """
        Test that building crt with reserved name is not allowed
        :return:
        """
        client_name = settings.IGNORED_CLIENT_NAMES[0]

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400
        assert response.json()['errors_occured']


    def test_revoke(self):
        """
        Test build and revoke
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

    def test_revoke_reserved_crt(self):

        """
        Test that revoking crt with reserved name is not allowed
        :return:
        """
        client_name = settings.IGNORED_CLIENT_NAMES[0]

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400
        assert response.json()['errors_occured']


    def test_twice_revoke(self):
        """
        Test re revoke
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['data']['client_name'] == client_name


    def test_revoke_unexisted_crt(self):
        """
        Test revoke unexisted crt
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4()) + str(uuid.uuid4())

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400


    def test_remove_unrevoked_crt(self):
        """
        Test remove unexisted crt file
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/remove/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400


    def test_remove_crt(self):
        """
        Test remove crt file
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/remove/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()


    def test_remove_crt_reserved_file(self):
        """
        Test remove reserved crt file
        :return:
        """
        client_name = settings.IGNORED_CLIENT_NAMES[0]

        url = "{}/api/openvpn/client/remove/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_remove_unexisted_crt(self):
        """
        Test remove unexisted crt file
        :return:
        """
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/remove/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

    def test_load_reserved_crt(self):
        """
        Test load reserved
        :return:
        """
        client_name = settings.IGNORED_CLIENT_NAMES[0]

        url = "{}/api/openvpn/client/load/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_load_with_existing_name_but_different_content(self):
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        client_name2 = self.client_name_prefix + str(uuid.uuid4())
        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name2)
        response2 = requests.request("POST", url, headers=headers)
        logger.debug(response2.text)
        response2.raise_for_status()

        url = "{}/api/openvpn/client/load/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers, json=response2.json())
        logger.debug(response.text)
        assert response.status_code == 400

    def test_build_and_load_same_as_revoked(self):
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/load/{}".format(TESTS_API_ADDRESS, client_name)
        payload = response.json()
        payload['data']['is_revoked'] = True
        response = requests.request("POST", url, headers=headers, json=payload)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['data']['is_revoked'] == True

    def test_build_revoke_and_load_as_unrevoked(self):
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        build_response = requests.request("POST", url, headers=headers)
        logger.debug(build_response.text)
        build_response.raise_for_status()

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/load/{}".format(TESTS_API_ADDRESS, client_name)
        payload = build_response.json()
        payload['data']['is_revoked'] = False
        response = requests.request("POST", url, headers=headers, json=payload)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['data']['is_revoked'] == False

    def test_build_and_get_client(self):
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['data']['is_revoked'] == False

    def test_get_reserved_client(self):
        client_name = settings.IGNORED_CLIENT_NAMES[0]

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_get_unexisted_client(self):
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_build_revoke_get(self):
        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['data']['is_revoked'] == True

        url = "{}/api/openvpn/client/remove/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_restore_reserved_crt(self):
        """
        Test load reserved
        :return:
        """
        client_name = settings.IGNORED_CLIENT_NAMES[0]

        url = "{}/api/openvpn/client/restore/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_build_revoke_restore(self):

        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()


        url = "{}/api/openvpn/client/revoke/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/restore/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/get/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()
        assert response.json()['data']['is_revoked'] == False

    def test_build_and_restore(self):

        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/build/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        response.raise_for_status()

        url = "{}/api/openvpn/client/restore/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

    def test_restore_unexisted(self):

        client_name = self.client_name_prefix + str(uuid.uuid4())

        url = "{}/api/openvpn/client/restore/{}".format(TESTS_API_ADDRESS, client_name)
        response = requests.request("POST", url, headers=headers)
        logger.debug(response.text)
        assert response.status_code == 400

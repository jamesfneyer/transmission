import copy
from unittest import mock

import requests
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
import httpretty
import json

from apps.shipments.models import Shipment, Location, LoadShipment, FundingType, EscrowStatus, ShipmentStatus
from apps.shipments.rpc import ShipmentRPCClient
from django.contrib.gis.geos import Point
from apps.utils import AuthenticatedUser, random_id
from tests.utils import replace_variables_in_string, create_form_content

VAULT_ID = 'b715a8ff-9299-4c87-96de-a4b0a4a54509'
CARRIER_WALLET_ID = '3716ff65-3d03-4b65-9fd5-43d15380cff9'
SHIPPER_WALLET_ID = '48381c16-432b-493f-9f8b-54e88a84ec0a'
STORAGE_CRED_ID = '77b72202-5bcd-49f4-9860-bc4ec4fee07b'
LOCATION_NAME = "Test Location Name"
LOCATION_CITY = 'City'
LOCATION_STATE = 'State'
LOCATION_NUMBER = "555-555-5555"


class ShipmentAPITests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_1 = AuthenticatedUser({
            'user_id': '5e8f1d76-162d-4f21-9b71-2ca97306ef7b',
            'username': 'user1@shipchain.io',
            'email': 'user1@shipchain.io',
        })

    def set_user(self, user, token=None):
        self.client.force_authenticate(user=user, token=token)

    def create_shipment(self):
        self.shipments = []
        self.shipments.append(Shipment.objects.create(vault_id=VAULT_ID,
                                                      carrier_wallet_id=CARRIER_WALLET_ID,
                                                      shipper_wallet_id=SHIPPER_WALLET_ID,
                                                      storage_credentials_id=STORAGE_CRED_ID,
                                                      owner_id=self.user_1.id,
                                                      load_data=self.load_datas[0]))

    def create_load_data(self):
        self.load_datas = []
        self.load_datas.append(LoadShipment.objects.create(shipment_id=1,
                                                           shipment_amount=0,
                                                           paid_amount=0,
                                                           paid_tokens="0.000000000000000000",
                                                           shipper=SHIPPER_WALLET_ID,
                                                           carrier=CARRIER_WALLET_ID,
                                                           contract_funded=False,
                                                           shipment_created=True,
                                                           valid_until=24,
                                                           funding_type=FundingType.SHIP,
                                                           escrow_status=EscrowStatus.CONTRACT_INITIATED,
                                                           shipment_status=ShipmentStatus.PENDING,
                                                           start_block=6))

    def test_list_empty(self):
        """
        Test listing requires authentication
        """

        # Unauthenticated request should fail with 403
        url = reverse('shipment-list', kwargs={'version': 'v1'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticated request should succeed
        self.set_user(self.user_1)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        # No devices created should return empty array
        self.assertEqual(len(response_data['data']), 0)
    #
    # def test_create(self):
    #     url = reverse('shipment-list', kwargs={'version': 'v1'})
    #
    #     # Unauthenticated request should fail with 403
    #     response = self.client.patch(url, '{}', content_type='application/vnd.api+json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     parameters = {
    #         '_vault_id': VAULT_ID,
    #         '_carrier_wallet_id': CARRIER_WALLET_ID,
    #         '_shipper_wallet_id': SHIPPER_WALLET_ID,
    #         '_storage_credentials_id': STORAGE_CRED_ID,
    #         '_async_hash': 'txHash'
    #     }
    #
    #     post_data = '''
    #         {
    #           "data": {
    #             "type": "Shipment",
    #             "attributes": {
    #               "carrier_wallet_id": "<<_carrier_wallet_id>>",
    #               "shipper_wallet_id": "<<_shipper_wallet_id>>",
    #               "storage_credentials_id": "<<_storage_credentials_id>>"
    #             }
    #           }
    #         }
    #     '''
    #
    #     # Mock RPC calls
    #     mock_rpc_client = ShipmentRPCClient
    #
    #     mock_rpc_client.create_vault = mock.Mock(return_value=parameters['_vault_id'])
    #     mock_rpc_client.add_shipment_data = mock.Mock(return_value={'hash': 'txHash'})
    #     mock_rpc_client.create_shipment_transaction = mock.Mock(return_value=('version', {}))
    #     mock_rpc_client.sign_transaction = mock.Mock(return_value=({}, 'txHash'))
    #     mock_rpc_client.send_transaction = mock.Mock(return_value={
    #         "blockHash": "0xccb595947a121e37df8bf689c3f88c6d9c7fb56070c9afda38551540f9e231f7",
    #         "blockNumber": 15,
    #         "contractAddress": None,
    #         "cumulativeGasUsed": 138090,
    #         "from": "0x13b1eebb31a1aa2ecaa2ad9e7455df2f717f2143",
    #         "gasUsed": 138090,
    #         "logs": [],
    #         "logsBloom": "0x0000000000",
    #         "status": True,
    #         "to": "0x25ff5dc79a7c4e34254ff0f4a19d69e491201dd3",
    #         "transactionHash": parameters['_async_hash'],
    #         "transactionIndex": 0
    #     })
    #
    #     # Authenticated request should succeed
    #     self.set_user(self.user_1)
    #
    #     post_data = replace_variables_in_string(post_data, parameters)
    #
    #     response = self.client.post(url, post_data, content_type='application/vnd.api+json')
    #     print(response.content)
    #
    #     response_data = response.json()
    #     self.assertEqual(response_data['data']['attributes']['carrier_wallet_id'], parameters['_carrier_wallet_id'])
    #     self.assertEqual(response_data['data']['attributes']['shipper_wallet_id'], parameters['_shipper_wallet_id'])
    #     self.assertEqual(response_data['data']['attributes']['storage_credentials_id'], parameters['_storage_credentials_id'])
    #     self.assertEqual(response_data['data']['attributes']['vault_id'], parameters['_vault_id'])
    #     self.assertEqual(response_data['data']['meta']['transaction_id'], parameters['_async_hash'])

    # def test_get_device_request_url(self):
    #     from conf.test_settings import PROFILES_URL
    #
    #     _shipment_id = 'b715a8ff-9299-4c87-96de-a4b0a4a54509'
    #     _vault_id = '01fc36c4-63e5-4c02-943a-b52cd25b235b'
    #     shipment = Shipment.objects.create(id=_shipment_id, vault_id=_vault_id)
    #
    #     profiles_url = shipment.get_device_request_url()
    #
    #     # http://INTENTIONALLY_DISCONNECTED:9999/api/v1/device/?on_shipment=b715a8ff-9299-4c87-96de-a4b0a4a54509
    #     self.assertIn(PROFILES_URL, profiles_url)
    #     self.assertIn(f"?on_shipment={_vault_id}", profiles_url)
    #
    # def test_get_tracking(self):
    #     self.create_load_data()
    #     self.create_shipment()
    #
    #     url = reverse('shipment-tracking', kwargs={'version': 'v1', 'pk': self.shipments[0].id})
    #
    #     class DeviceForShipmentResponse(object):
    #         status_code = status.HTTP_200_OK
    #
    #         @staticmethod
    #         def json():
    #             return {
    #                 'data': [
    #                     {
    #                         'type': 'Device'
    #                     }
    #                 ]
    #             }
    #
    #     tracking_data = [
    #                 {
    #                     'coordinates': [33.018413333333335, -80.123635],
    #                     'fix_date': '270718',
    #                     'fix_time': '210714.000',
    #                     'has_gps': 'A',
    #                     'source': 'gps',
    #                     'uncertainty': 0
    #                 },
    #                 {
    #                     'coordinates': [34.018413333333335, -81.123635],
    #                     'fix_date': '280718',
    #                     'fix_time': '210714.000',
    #                     'source': 'gps',
    #                     'uncertainty': 0
    #                 },
    #             ]
    #
    #     geo_json = {
    #         'type': 'FeatureCollection',
    #         'features': [
    #             {
    #                 'type': 'Feature',
    #                 'geometry': {
    #                     'type': 'LineString',
    #                     'coordinates': [
    #                         [
    #                             -80.123635,
    #                             33.018413333333335
    #                         ],
    #                         [
    #                             -81.123635,
    #                             34.018413333333335
    #                         ]
    #                     ]
    #                 },
    #                 'properties': {
    #                     'linestringTimestamps': [
    #                         '2018-07-27T21:07:14',
    #                         '2018-07-28T21:07:14'
    #                     ]
    #                 }
    #             },
    #             {
    #                 'type': 'Feature',
    #                 'geometry': {
    #                     'type': 'Point',
    #                     'coordinates': [
    #                         -80.123635,
    #                         33.018413333333335
    #                     ]
    #                 },
    #                 'properties': {
    #                     'time': '2018-07-27T21:07:14',
    #                     'uncertainty': 0,
    #                     'has_gps': 'A',
    #                     'source': 'gps'
    #                 }
    #             },
    #             {
    #                 'type': 'Feature',
    #                 'geometry': {
    #                     'type': 'Point',
    #                     'coordinates': [
    #                         -81.123635,
    #                         34.018413333333335
    #                     ]
    #                 },
    #                 'properties': {
    #                     'time': '2018-07-28T21:07:14',
    #                     'uncertainty': 0,
    #                     'has_gps': None,
    #                     'source': 'gps'
    #                 }
    #             }
    #         ]
    #     }
    #
    #     # Unauthenticated request should fail with 403
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     # Mock Requests calls
    #     mock_requests = requests
    #     mock_requests.get = mock.Mock(return_value=DeviceForShipmentResponse)
    #
    #     # Mock RPC calls
    #     mock_rpc_client = ShipmentRPCClient
    #     mock_rpc_client.get_tracking_data = mock.Mock(return_value=tracking_data)
    #
    #     # Authenticated request should succeed, pass in token so we can pull it from request.auth
    #     self.set_user(self.user_1, b'a1234567890b1234567890')
    #
    #     response = self.client.get(url)
    #     response_data = response.json()
    #
    #     self.assertEqual(response_data['data'], geo_json)
    #
    #     # Test ?as_point
    #     response = self.client.get(f'{url}?as_point')
    #     response_data = response.json()
    #
    #     geo_json_point = copy.deepcopy(geo_json)
    #     del geo_json_point['features'][0]
    #
    #     self.assertEqual(response_data['data'], geo_json_point)
    #
    #     # Test ?as_line
    #     response = self.client.get(f'{url}?as_line')
    #     response_data = response.json()
    #
    #     geo_json_line = copy.deepcopy(geo_json)
    #     del geo_json_line['features'][2]
    #     del geo_json_line['features'][1]
    #
    #     self.assertEqual(response_data['data'], geo_json_line)
    #
    # def test_shipment_update(self):
    #     self.create_load_data()
    #     self.create_shipment()
    #     url = reverse('shipment-detail', kwargs={'version': 'v1', 'pk': self.shipments[0].id})
    #
    #     # Unauthenticated request should fail with 403
    #     response = self.client.put(url, '{}', content_type='application/vnd.api+json')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     parameters = {
    #         '_vault_id': VAULT_ID,
    #         '_carrier_wallet_id': CARRIER_WALLET_ID,
    #         '_shipper_wallet_id': SHIPPER_WALLET_ID,
    #         '_storage_credentials_id': STORAGE_CRED_ID,
    #         '_async_hash': 'txHash',
    #         '_shipment_id': self.shipments[0].id,
    #         '_carrier_scac': 'test_scac'
    #     }
    #
    #     post_data = '''
    #                 {
    #                   "data": {
    #                     "type": "Shipment",
    #                     "id": "<<_shipment_id>>",
    #                     "attributes": {
    #                       "carrier_scac": "test_scac"
    #                     }
    #                   }
    #                 }
    #             '''
    #
    #     # Mock RPC calls
    #     mock_rpc_client = ShipmentRPCClient
    #
    #     mock_rpc_client.add_shipment_data = mock.Mock(return_value={"hash": "txHash"})
    #     mock_rpc_client.sign_transaction = mock.Mock(return_value={})
    #     mock_rpc_client.send_transaction = mock.Mock(return_value={
    #         "blockHash": "0xccb595947a121e37df8bf689c3f88c6d9c7fb56070c9afda38551540f9e231f7",
    #         "blockNumber": 15,
    #         "contractAddress": None,
    #         "cumulativeGasUsed": 138090,
    #         "from": "0x13b1eebb31a1aa2ecaa2ad9e7455df2f717f2143",
    #         "gasUsed": 138090,
    #         "logs": [],
    #         "logsBloom": "0x0000000000",
    #         "status": True,
    #         "to": "0x25ff5dc79a7c4e34254ff0f4a19d69e491201dd3",
    #         "transactionHash": parameters['_async_hash'],
    #         "transactionIndex": 0
    #     })
    #     mock_rpc_client.update_vault_hash_transaction = mock.Mock(return_value={
    #         "nonce": "0x2",
    #         "chainId": 1337,
    #         "to": "0x25Ff5dc79A7c4e34254ff0f4a19d69E491201DD3",
    #         "gasPrice": "0x4a817c800",
    #         "gasLimit": "0x7a120",
    #         "value": "0x0",
    #         "data": "0x002"
    #     })
    #
    #     # Authenticated request should succeed
    #     self.set_user(self.user_1)
    #
    #     post_data = replace_variables_in_string(post_data, parameters)
    #     print('load_data: ', self.shipments[0].load_data)
    #     response = self.client.put(url, post_data, content_type='application/vnd.api+json')
    #
    #     response_data = response.json()
    #     print(response_data)
    #     self.assertEqual(response_data['data']['attributes']['carrier_wallet_id'], parameters['_carrier_wallet_id'])
    #     self.assertEqual(response_data['data']['attributes']['shipper_wallet_id'], parameters['_shipper_wallet_id'])
    #     self.assertEqual(response_data['data']['attributes']['storage_credentials_id'],
    #                      parameters['_storage_credentials_id'])
    #     self.assertEqual(response_data['data']['attributes']['carrier_scac'], parameters['_carrier_scac'])
    #     self.assertEqual(response_data['data']['attributes']['vault_id'], parameters['_vault_id'])
    #     self.assertEqual(response_data['data']['meta']['transaction_id'], parameters['_async_hash'])


class LocationAPITests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_1 = AuthenticatedUser({
            'user_id': '5e8f1d76-162d-4f21-9b71-2ca97306ef7b',
            'username': 'user1@shipchain.io',
            'email': 'user1@shipchain.io',
        })

    def set_user(self, user, token=None):
        self.client.force_authenticate(user=user, token=token)

    def create_location(self):
        self.locations = []
        self.locations.append(Location.objects.create(name=LOCATION_NAME,
                                                      owner_id='5e8f1d76-162d-4f21-9b71-2ca97306ef7b'))

    def test_list_empty(self):
        """
        Test listing requires authentication
        """

        # Unauthenticated request should fail with 403
        url = reverse('location-list', kwargs={'version': 'v1'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticated request should succeed
        self.set_user(self.user_1)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()

        # No devices created should return empty array
        self.assertEqual(len(response_data['data']), 0)

    @httpretty.activate
    def test_create_location(self):
        url = reverse('location-list', kwargs={'version': 'v1'})
        valid_data, content_type = create_form_content({'name': LOCATION_NAME, 'city': LOCATION_CITY,
                                                        'state': LOCATION_STATE})
        body_obj = {'results': [{'address_components': [{'types': []}], 'geometry': {'location': {'lat': 12, 'lng': 23}}}]}
        body_string = json.dumps(body_obj)
        http_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={LOCATION_CITY}+{LOCATION_STATE}&key=mock'

        # Unauthenticated request should fail with 403
        response = self.client.post(url, body_string, content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_user(self.user_1)

        # Authenticated request without name parameter should fail
        response = self.client.post(url, '{}', content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        httpretty.register_uri(httpretty.GET, http_url, body=body_string)

        # Authenticated request with name parameter should succeed
        response = self.client.post(url, valid_data, content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertEqual(response_data['data']['attributes']['name'], LOCATION_NAME)
        self.assertEqual(response_data['data']['attributes']['geometry']['coordinates'], [12.0, 23.0])

    @httpretty.activate
    def test_update_existing_location(self):
        self.create_location()
        url = reverse('location-detail', kwargs={'version': 'v1', 'pk': self.locations[0].id})
        valid_data, content_type = create_form_content({'phone_number': LOCATION_NUMBER, 'city': LOCATION_CITY,
                                                        'state': LOCATION_STATE})
        body_obj = {
            'results': [{'address_components': [{'types': []}], 'geometry': {'location': {'lat': 12, 'lng': 23}}}]}
        body_string = json.dumps(body_obj)
        http_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={LOCATION_CITY}+{LOCATION_STATE}&key=mock'

        # Unauthenticated request should fail with 403
        response = self.client.patch(url, valid_data, content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_user(self.user_1)
        httpretty.register_uri(httpretty.GET, http_url, body=body_string)

        # Authenticated request with name parameter should succeed
        response = self.client.patch(url, valid_data, content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['data']['attributes']['phone_number'], LOCATION_NUMBER)
        self.assertEqual(response_data['data']['attributes']['geometry']['coordinates'], [12.0, 23.0])

    def test_update_nonexistent_location(self):
        self.create_location()
        url = reverse('location-detail', kwargs={'version': 'v1', 'pk': random_id()})
        valid_data, content_type = create_form_content({'phone_number': LOCATION_NUMBER})

        # Unauthenticated request should fail with 403
        response = self.client.patch(url, valid_data, content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_user(self.user_1)

        # Authenticated request should fail
        response = self.client.patch(url, valid_data, content_type=content_type)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_location(self):
        self.create_location()
        url = reverse('location-detail', kwargs={'version': 'v1', 'pk': self.locations[0].id})

        # Unauthenticated request should fail with 403
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_user(self.user_1)

        # Authenticated request should succeed
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure location does not exist
        self.assertEqual(Location.objects.count(), 0)

    def test_delete_nonexistent_location(self):
        self.create_location()
        url = reverse('location-detail', kwargs={'version': 'v1', 'pk': random_id()})

        # Unauthenticated request should fail with 403
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_user(self.user_1)

        # Authenticated request should fail
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

import logging
import sys
import time

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from shipchain_common.exceptions import RPCError

from apps.eth.models import EthAction
from apps.eth.rpc import EventRPCClient
from apps.jobs.models import AsyncJob, Message, MessageType
from apps.jobs.tasks import AsyncTask
from apps.shipments.models import Shipment


logger = logging.getLogger('transmission')
logger.setLevel(settings.LOG_LEVEL)


class Command(BaseCommand):
    help = 'Replicate shipment related transactions to the sidechain.'
    rpc_client = None
    successful_shipments = set()
    unsuccessful_shipments = set()
    async_job = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--shipment_id',
            type=str,
            default=None,
            help='Replicate specific shipment instead of all of them.',
        )

    def _replicate_shipment(self, shipment):
        for async_job in AsyncJob.objects.filter(shipment=shipment):
            try:
                message = Message.objects.filter(async_job=async_job,
                                                 type=MessageType.ETH_TRANSACTION).order_by('created_at').last()
                if message and 'cumulativeGasUsed' in message.body and message.body['cumulativeGasUsed'] == '0':
                    continue
                logger.info(f'Performing action for shipment: {shipment.id}')
                for eth_action in EthAction.objects.filter(async_job=async_job):
                    logger.info(f'Deleting Eth Action: {eth_action.transaction_hash}')
                    eth_action.delete()
                AsyncTask(async_job.id).rerun()
                self.successful_shipments.add(shipment.id)
                self.async_job = async_job

            # pylint:disable=broad-except
            except Exception as exc:
                logger.info(f'Error replicating shipment transactions: {shipment.id}')
                self.successful_shipments.discard(shipment.id)
                self.unsuccessful_shipments.add(shipment.id)
                logger.error(exc)

    def _unsubscribe(self):
        self.rpc_client = EventRPCClient()
        try:
            self.rpc_client.unsubscribe("LOAD", settings.LOAD_VERSION)
        except RPCError as exc:
            if 'Error: EventSubscription not found' not in exc.detail:
                raise exc

    def _resubscribe(self):
        if not self.async_job:
            logger.warning('Unable to find last blockheight to subscribe to. '
                           'Need to manually subscribe to latest blockheight')
            return

        message = Message.objects.filter(async_job=self.async_job).order_by('created_at').last()
        if "blockNumber" not in message.body:
            time.sleep(15)
            message = Message.objects.filter(async_job=self.async_job).order_by('created_at').last()
        if "blockNumber" in message.body:
            self.rpc_client.subscribe("LOAD", settings.LOAD_VERSION, last_block=message.body["blockNumber"])
        else:
            logger.warning('Unable to find last blockheight to subscribe to. '
                           'Need to manually subscribe to latest blockheight')

    def handle(self, *args, **options):
        cache.set('REPLICATE_SHIPMENTS_LOCK', True, None)
        self._unsubscribe()
        if options['shipment_id']:
            shipment = Shipment.objects.filter(id=options['shipment_id']).first()
            if not shipment:
                logger.error(f'Invalid shipment id: {options["shipment_id"]} supplied')
                sys.exit()

            self._replicate_shipment(shipment)

        else:
            shipments = Shipment.objects.all()
            logger.info(f'Total shipments: {shipments.count()}')
            for shipment in shipments:
                self._replicate_shipment(shipment)

        logger.info(f'Successful shipments count: {len(self.successful_shipments)}')
        logger.debug(f'Successful shipments: {self.successful_shipments}')

        logger.warning(f'Unsuccessful shipments count: {len(self.unsuccessful_shipments)}')
        logger.warning(f'Unsuccessful shipments: {self.unsuccessful_shipments}')

        cache.delete_pattern('REPLICATE_SHIPMENTS_LOCK')
        self._resubscribe()

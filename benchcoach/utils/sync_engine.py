from abc import ABC, abstractmethod

import django.db.models
from django.db.models import QuerySet
from typing import List, Tuple

class AbstractSyncEngine(ABC):
    models: List[django.db.models.Model]

    @abstractmethod
    def sync(self, qs: django.db.models.QuerySet = None, instance: django.db.models.Model = None, direction='download') -> List[Tuple[django.db.models.Model, bool]]:
        '''
        Syncs the input from/to the service. Either a query set or instance should be provided, but not both.
        :param qs: the queryset to be updated. If set to 'download', it will be updated from the service, if set to uplad, its contents
        will be sent to the server
        :param instance: the instance to be updated. If set to 'download', it will be updated from the service, if set to uplad, its contents
        will be sent to the server.
        :param direction: the sync direction, either 'download' or 'upload'.
        :return: a list of tuples in the form of (created/updated object, true if created/false if not)
        '''

    @abstractmethod
    def import_items(self):
        '''
        Imports the items from the service.
        :return: a list of tuples in the form of (created/updated object, true if created/false if not)
        '''
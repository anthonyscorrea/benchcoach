from abc import ABC, abstractmethod

import django.db.models
from django.db.models import QuerySet
from typing import List, Tuple
import benchcoach.models

class AbstractSyncEngine(ABC):
    '''
    Class used for importing and syncing Bench Coach models.
    '''
    models: List[benchcoach.models.BenchcoachModel]

    @abstractmethod
    def sync(self, qs: django.db.models.QuerySet = None, instance: benchcoach.models.BenchcoachModel = None, direction='download') -> List[Tuple[django.db.models.Model, bool]]:
        '''
        Syncs the input from/to the service. Either a query set or instance should be provided, but not both.
        It does not create Bench Coach objects.
        :param qs: the queryset to be updated.
        :param instance: the instance to be updated.
        :param direction: the sync direction, either 'download' or 'upload'. If set to 'download', it will be updated from the service, if set to upload, its contents
        will be sent to the service
        :return: a list of BenchCoach objects that have been iterated (but not necessarily changed) during sync.
        '''

    @abstractmethod
    def import_items(self):
        '''
        Imports the items from the service. It imports all models specified in the class property 'model'.
        It creates BenchCoach objects, but should not create duplicates.
        :return: a list of BenchCoach objects that have been iterated (but not necessarily changed) during import.
        '''
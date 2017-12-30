#from django.utils import timezone
from django.db import models
import uuid


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Artefact(models.Model):
    number = models.UUIDField(primary_key=True, default=uuid.uuid4)
    keeper = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    title = models.CharField(max_length=256, default='noname')
    pages = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now=True)

    #---------------------------------------------------------------------------
    def accepted(self, title):
        self.title = title
        self.save()

    #---------------------------------------------------------------------------
    def __str__(self):
        return self.title

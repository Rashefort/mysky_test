from django.db import models

import hashlib
import time



#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
# Если у pdf имя набрано кириллицей, то pgmagick (сука такая) вываливается
# с ошибкой, поэтому переименовываем файл (upload_to=artefact_rename).
def artefact_rename(instance, filename):
    instance.title = filename
    return hashlib.md5(f'{time.time()}'.encode()).hexdigest()


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Artefact(models.Model):
    keeper = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    artefact = models.FileField(upload_to=artefact_rename)
    title = models.CharField(max_length=256)
    pages = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)


    #---------------------------------------------------------------------------
    def __str__(self):
        return self.title

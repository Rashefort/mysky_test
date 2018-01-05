from django.db import models


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Artefact(models.Model):
    keeper = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    artefact = models.FileField()
    pages = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)


    #---------------------------------------------------------------------------
    def __str__(self):
        return self.title

from django.db import models


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class Artefact(models.Model):
    keeper = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    pages = models.IntegerField(default=0)

    #---------------------------------------------------------------------------
    def accepted(self):
        self.save()

    #---------------------------------------------------------------------------
    def __str__(self):
        return self.title

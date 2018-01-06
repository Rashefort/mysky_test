from django.contrib import admin
from .models import Artefact


class ArtefactAdmin(admin.ModelAdmin):
    fields = ['article_title', 'article_text', 'article_date']


admin.site.register(Artefact)

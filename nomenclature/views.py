from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from .models import Artefact


#-------------------------------------------------------------------------------
def artefact_list(request):
    artefacts = Artefact.objects.filter(created__lte=timezone.now()).order_by('created')
    return render(request, 'nomenclature/artefact_list.html', {'artefacts': artefacts})

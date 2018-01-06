from django.contrib.auth.decorators import login_required #@login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from .forms import ArtefactForm
from .models import Artefact
import PyPDF2


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def nomenclature(request):
    artefacts = Artefact.objects.filter(created__lte=timezone.now()).order_by('created')
    return render(request, 'nomenclature.html', {'artefacts': artefacts, 'form': ArtefactForm()})


#-------------------------------------------------------------------------------
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)

            return redirect('/')

    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


#-------------------------------------------------------------------------------
def upload(request):
    if request.method == 'POST':
        form = ArtefactForm(request.POST, request.FILES)

        print(request.FILES['artefact'])

        if form.is_valid():
            file = PyPDF2.PdfFileReader(request.FILES['artefact'])

            artefact = form.save(commit=False)
            artefact.keeper = request.user
            artefact.created = timezone.now()
            artefact.pages = file.getNumPages()
            artefact.save()

            return redirect('/')

    return redirect(request.REQUEST.get(REDIRECT_FIELD_NAME, reverse('frontend:index')))

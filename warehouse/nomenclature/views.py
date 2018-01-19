from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from .forms import ArtefactForm
from .models import Artefact

import os

import pgmagick
import PyPDF2



#-------------------------------------------------------------------------------
def nomenclature(request):
    artefacts = Artefact.objects.all()
    form = ArtefactForm()

    return render(request, 'nomenclature.html', {'artefacts': artefacts, 'form': form})


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

        if form.is_valid():
            try:
                file = PyPDF2.PdfFileReader(request.FILES['artefact'])

                artefact = form.save(commit=False)
                artefact.keeper = request.user
                artefact.created = timezone.now()
                artefact.pages = file.getNumPages()
                artefact.save()

            except Exception as line:
                print(line)

            finally:
                return redirect('/')

    return redirect(request.REQUEST.get(REDIRECT_FIELD_NAME, reverse('frontend:index')))


#-------------------------------------------------------------------------------
def images(request):
    try:
        id = int(request.GET['id'])
    except:
        id = Artefact.objects.all()[0].id

    artefact = Artefact.objects.get(id=id)
    pages = artefact.pages

    try:
        page = int(request.GET['page'])
    except:
        page = 1

    page = min(page, pages)
    page = max(1, page)

    back_page = page - 1
    next_page = page + 1 if page != pages else 0

    ext = str(page).rjust(len(str(pages)), '0')

    current_dir = os.getcwd()
    media_dir = os.path.join(current_dir, 'media')
    pages_dir = os.path.join(current_dir, 'static', 'pages')

    pdf_name = f'{artefact.title}_{ext}.png'
    hash_name = f'{artefact.artefact.name}_{ext}.png'
    hash_file = os.path.join(pages_dir, hash_name)

    if not os.path.exists(hash_file):
        name = os.path.join(media_dir, f'{artefact.artefact.name}[{page-1}]')
        file = pgmagick.Image(name)
        file.write(hash_file)

    data = {
        'id': id,
        'pages': pages,
        'name': pdf_name,
        'image': hash_name,
        'back': back_page,
        'next': next_page,
    }

    return render(request, 'images.html', data)

#from django.contrib.auth.decorators import login_required #@login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from .models import Artefact


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
def nomenclature(request):
    artefacts = Artefact.objects.filter(created__lte=timezone.now()).order_by('created')
    return render(request, 'nomenclature.html', {'artefacts': artefacts})

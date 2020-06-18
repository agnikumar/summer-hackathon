from django.shortcuts import render
from dappx.forms import UserForm, UserProfileInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from square.client import Client
import uuid

def index(request):
    return render(request,'dappx/index.html')

# TODO: add login_required
def payments(request):
    if request.method == 'POST':
        nonce = request.POST.get("nonce")
        access_token = "EAAAEIH1Nl_wGkMWzrIOCBTihP5VLjVvKc1r8ZCEDwE-T_O2-eCkAqHb3b6pnbRm"
        environment = "sandbox"
        client = Client(access_token=access_token, environment=environment)
        idempotency_key = str(uuid.uuid1())

        amount = {'amount': 100, 'currency': 'USD'}
        body = {'idempotency_key': idempotency_key, 'source_id': nonce, 'amount_money': amount}
        api_response = client.payments.create_payment(body)
        if api_response.is_success():
            res = api_response.body['payment']
        elif api_response.is_error():
            res = "Exception when calling PaymentsApi->create_payment: {}".format(api_response.errors)
        print(res)

        return render(request, 'dappx/index.html')
    else:
        return render(request, 'dappx/payments.html')

@login_required
def special(request):
    return HttpResponse("You are logged in !")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        info_form = UserProfileInfoForm()
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            info = info_form.save(commit=False)
            info.user = user
            info.save()
            registered = True
        else:
            print(user_form.errors)
            print(info_form.errors)
    else:
        user_form = UserForm()
        info_form = UserProfileInfoForm()
    return render(request,'dappx/registration.html',
                          {'user_form':user_form, 'info_form': info_form,
                           'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'dappx/login.html', {})

def profile(request):
    return render(request, 'dappx/profile.html')



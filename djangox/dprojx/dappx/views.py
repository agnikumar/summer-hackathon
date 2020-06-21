from django.shortcuts import render
from dappx.forms import UserForm, UserProfileInfoForm, ClientInfoForm, ContractorInfoForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from square.client import Client as squareClient
from django.contrib.auth.models import User, Group
import uuid
from dappx.models import Client, Contractor, Transaction
import datetime

def index(request):
    return render(request,'dappx/index.html')

# TODO: Add in Transactions
@login_required
def payments(request):
    if request.method == 'POST':
        # we have to forward to the recipient
        recipient = request.POST.get("recipient")
        payment = request.POST.get("payment")
        nonce = request.POST.get("nonce")
        access_token = "EAAAEIH1Nl_wGkMWzrIOCBTihP5VLjVvKc1r8ZCEDwE-T_O2-eCkAqHb3b6pnbRm"
        environment = "sandbox"
        client = squareClient(access_token=access_token, environment=environment)
        idempotency_key = str(uuid.uuid1())

        amount = {'amount': int(payment), 'currency': 'USD'}
        body = {'idempotency_key': idempotency_key, 'source_id': nonce, 'amount_money': amount}
        api_response = client.payments.create_payment(body)
        if api_response.is_success():
            res = api_response.body['payment']
        elif api_response.is_error():
            res = "Exception when calling PaymentsApi->create_payment: {}".format(api_response.errors)
        print(res)

        Transaction.objects.create(client=request.user.username, contractor=recipient, payment=payment, date=datetime.datetime.now().date())
        print("Done")

        return render(request, 'dappx/index.html')
    else:
        return render(request, 'dappx/payments.html')

@login_required
def search(request):
    vals = Contractor.objects.values_list("categories", flat=True).distinct()
    values = [x[0] for x in vals]
    print(values)
    return render(request, 'dappx/search.html', {'categories': values})

@login_required
def special(request):
    return HttpResponse("You are logged in !")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    registered = False
    user_type = None
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
            user_type = request.POST.get("user_type")
            if user_type == "CL":
                group, created = Group.objects.get_or_create(name='Client')
                user.groups.add(group)
                return render(request,'dappx/info.html', {'user_type': user_type, 'info_form': ClientInfoForm(), 'user': user})
            else:
                group, created = Group.objects.get_or_create(name='Contractor')
                user.groups.add(group)
                return render(request,'dappx/info.html', {'user_type': user_type, 'info_form': ContractorInfoForm(), 'user': user})
        else:
            print(user_form.errors)
            print(info_form.errors)
            return render(request,'dappx/registration.html',
                          {'user_form':user_form, 'info_form': info_form,
                           'registered':registered})
    else:
        user_form = UserForm()
        info_form = UserProfileInfoForm()
        return render(request,'dappx/registration.html',
                          {'user_form':user_form, 'info_form': info_form,
                           'registered':registered})


def info(request):
    # client
    name = request.POST.get("name")
    business_id = request.POST.get("business_id")
    address = request.POST.get("address")
    state = request.POST.get("state")
    city = request.POST.get("state")
    postal_code = request.POST.get("postal_code")

    username  = request.POST.get("username")
    user = User.objects.get(username=username)

    if business_id is None:
        client = Client.objects.create(user=user, name=name, state=state, city=city, postal_code=postal_code)
        client.save()
    else:
        contractor = Contractor.objects.create(user=user, name=name, state=state, city=city, postal_code=postal_code, business_id=business_id, address=address, stars=0, review_count=0, categories=[])
        contractor.save()

    print("Created")
    registered = True
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

def transactions(request):
    transactions = Transaction.objects.filter(contractor=request.user.username)
    return render(request, 'dappx/transactions.html', {'transactions':transactions})

def notes(request):
    return render(request, 'dappx/notes.html')


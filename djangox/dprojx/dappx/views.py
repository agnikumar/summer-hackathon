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

from dappx.recommender import *
import os
import random

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

#data_path = 'data/yelp_network_data.csv'
data_path = open(os.path.dirname(os.path.realpath(__file__)) + '/data/yelp_network_data.csv', "r")
network_df = get_network_df(data_path) # global
network_df_list = get_network_df_list(network_df) # global

@login_required
def search(request):
    vals = Contractor.objects.values_list("categories", flat=True).distinct()
    values = [x[0] for x in vals if len(x) > 0 and x[0] not in ["plumbing", "extermination"]]
    values = sorted(list(set(values)))
    #############################
    submitted = False
    output = ''
    selected_category = ''
    if request.method == 'POST':
        # calling recommender model
        submitted = True
        client = Client.objects.get(user=request.user)
        user_id = str(getattr(client, "uid")) 
        print('USER ID:', user_id)
        category = request.POST['dropdown']
        k = 20
        
        try:
            output = to_html(recommend(network_df, network_df_list, user_id, category, k))
        except ValueError:
            pass
        
        selected_category = category
    #############################
    return render(request, 'dappx/search.html', {'categories': values, 'output':output, 'submitted':submitted, 'selected_category': selected_category})

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
        contractor = Contractor.objects.create(user=user, name=name, state=state, city=city, postal_code=postal_code, business_id=business_id, address=address, covid_safety=0, review_count=0, categories=[])
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

def add_friends(request):
    try:
        client = Client.objects.get(user=request.user)
        categories = getattr(client, "friends")
        new_categories = categories + [Client.objects.get(name=request.POST.get("friend")).uid]
        client.friends = new_categories
        client.save()
        print(Client.objects.get(name=request.POST.get("friend")).uid)
    except Exception as e:
        pass
    return HttpResponseRedirect(reverse('dappx:friends'))

def remove_friends(request):
    client = Client.objects.get(user=request.user)
    friends = getattr(client, "friends")
    new_friends = []
    for i in friends:
        try:
            if Client.objects.get(uid=i).name != request.POST.get("friend"):
                new_friends.append(i)
        except Exception as e:
            pass
    client.friends = new_friends
    client.save()
    return HttpResponseRedirect(reverse('dappx:friends'))

def add_category(request):
    contractor = Contractor.objects.get(user=request.user)
    categories = getattr(contractor, "categories")
    new_categories = categories + [request.POST.get("category")]
    contractor.categories = new_categories
    contractor.save()
    return HttpResponseRedirect(reverse('dappx:profile'))

def remove_category(request):
    contractor = Contractor.objects.get(user=request.user)
    categories = getattr(contractor, "categories")
    new_categories = [i for i in categories if i != request.POST.get("category")]
    contractor.categories = new_categories
    contractor.save()
    return HttpResponseRedirect(reverse('dappx:profile'))

def profile(request):
    new_client_info, new_contractor_info = {}, {}
    print("yea")
    try:
        cl = Client.objects.get(user=request.user)
        client_fields = [field.name for field in Client._meta.get_fields()]
        client_info = [getattr(cl, i) for i in client_fields]
        new_client_info = {client_fields[i]:client_info[i] for i in range(len(client_fields)) if client_fields[i] not in ["user", "friends"]}
    except Exception as e:
        pass
    try:
        contractor = Contractor.objects.get(user=request.user)
        contractor_fields = [field.name for field in Contractor._meta.get_fields()]
        print(contractor_fields)
        contractor_info = [getattr(contractor, i) for i in contractor_fields]
        new_contractor_info = {contractor_fields[i]:contractor_info[i] for i in range(len(contractor_fields)) if contractor_fields[i] != "user"}
    except Exception as e:
        print(e)
    vals = Contractor.objects.values_list("categories", flat=True).distinct()
    print(vals)
    values = [x[0] for x in vals if len(x) > 0 and x[0] not in ["plumbing", "extermination"]]
    values = sorted(list(set(values)))
    return render(request, 'dappx/profile.html', {'client_info': new_client_info, 'contractor_info': new_contractor_info,
                                                  'categories':values})

def transactions(request):
    transactions = Transaction.objects.filter(contractor=request.user.username)
    return render(request, 'dappx/transactions.html', {'transactions':transactions})

def notes(request):
    return render(request, 'dappx/notes.html')

#friends_data_path = open(os.path.dirname(os.path.realpath(__file__)) + '/data/client_data.csv', "r")
#df_friends = get_network_df(friends_data_path)
#df_friends['user_id'] = df_friends['user_id'].str.strip()
#dict_friends = dict(zip(df_friends.user_id, df_friends.name))

def friends(request):
    friends = getattr(Client.objects.get(user=request.user), "friends")
    print("hee")
    print(friends)
    #friends_stripped = list(map(str.strip, friends))
    #friends_names_map = list(map(dict_friends.get, friends_stripped))
    #friends_names = ['' if x is None else x for x in friends_names_map]
    #friends_names = [i for i in friends_names_map if i]
    #print(friends_stripped)
    #print(friends_names)
    friend_names = []
    for friend in friends:
        name = ""
        try:
            name = Client.objects.get(uid=friend).name
        except Exception as e:
            pass
        friend_names.append(name)
    print(friend_names)
    friends_names = [i for i in friend_names if len(i) != 0]
    #rand_int = random.randint(1,16)
    #profile_pic_path = 'images/friends/' +  str(rand_int) + '.png'
    profile_pic_path = 'images/profile-pic.jpg'
    print(friends_names)
    return render(request, 'dappx/friends.html', {"friends":friends, "profile_pic_path":profile_pic_path, "friends_names":friends_names})


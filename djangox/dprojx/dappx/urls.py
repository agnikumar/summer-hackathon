# dappx/urls.py
from django.conf.urls import url
from dappx import views
# SET THE NAMESPACE!
app_name = 'dappx'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url(r'^register/$',views.register,name='register'),
    url(r'^user_login/$',views.user_login,name='user_login'),
    url(r'^payments/$', views.payments,name='payments'),
    url(r'^profile/$', views.profile,name='profile'),
    url(r'^transactions/$', views.transactions,name='transactions'),
    url(r'^notes/$', views.notes,name='notes'),
    url(r'^info/$', views.info,name='info'),
    url(r'^search/$', views.search,name='search'),
    url(r'^friends/$', views.friends,name='friends'),
url(r'^add_category/$', views.add_category,name='add_category'),
]
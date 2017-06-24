from django.conf.urls import url
from core.views import people, index, signup, username_validate, search
from django.contrib.auth import views as auth_views
from core.views import communities

urlpatterns = [

    url(r'^$', index, name='index'),
    url(r'^people/$', people, name='people'),
    url(r'^communities/$', communities, name='all_communities'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^search/$', search, name='search'),
    url(r'^v/username/$', username_validate, name='username_validate'),

]
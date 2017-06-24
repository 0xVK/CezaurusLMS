from django.conf.urls import url
from profiler.views import *
from messenger.views import *


urlpatterns = [

    url(r'^friends/$', friends, name='friends'),
    url(r'^friends/requests/$', friends_requests, name='friends_requests'),
    url(r'^friends/sent_requests/$', friends_sent_requests, name='friends_sent_requests'),

    url(r'^a/send_friend_request/$', action_send_friend_request, name='send_friend_request'),
    url(r'^a/cancel_friend_request/$', action_cancel_friend_request, name='cancel_friend_request'),
    url(r'^a/accept_friend_request/$', action_accept_friend_request, name='accept_friend_request'),
    url(r'^a/reject_friend_request/$', action_reject_friend_request, name='reject_friend_request'),
    url(r'^a/delete_wall_post/(?P<username>[^/]+)/(?P<p_id>\d+)/$', action_delete_wall_post, name='delete_wall_post'),
    url(r'^a/remove_friend/$', action_remove_friend, name='remove_friend'),
    url(r'^a/send_message/$', send_message, name='send_message'),

    url(r'^settings/$', settings_profile, name='settings_profile'),
    url(r'^settings/picture/$', settings_picture, name='settings_picture'),
    url(r'^settings/upload_picture/$', upload_picture, name='upload_picture'),
    url(r'^settings/save_uploaded_picture/$', save_uploaded_picture, name='save_uploaded_picture'),
    url(r'^settings/password/$', settings_password, name='settings_password'),


    url(r'^(?P<username>[^/]+)/$', profile_wall_posts, name='profile'),
    url(r'^(?P<username>[^/]+)/friends/$', profile_friends, name='profile_friends'),
    url(r'^(?P<username>[^/]+)/communities/$', profile_communities, name='profile_communities'),
    url(r'^(?P<username>[^/]+)/awards/$', profile_awards, name='profile_awards'),
    url(r'^(?P<username>[^/]+)/add_post/$', add_wallpost, name='add_wallpost'),

]
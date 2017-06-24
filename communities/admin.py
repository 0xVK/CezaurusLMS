from django.contrib import admin
from communities.models import *

admin.site.register(Community)
admin.site.register(CommunityInvite)
admin.site.register(CommunityWallPost)
admin.site.register(Discussion)
admin.site.register(DiscussionComment)

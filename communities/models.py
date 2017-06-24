from django.db import models
from django.contrib.auth.models import Group, User, Permission
from communities.exceptions import *
from django.utils.translation import ugettext as _
from django.shortcuts import reverse, redirect


class CommunityManager(models.Manager):

    @staticmethod
    def is_member(user, community):
        """ > user model, community"""
        return user.profile in community.get_members.all()

    @staticmethod
    def get_invites(user):
        """return list user invites to communities"""
        return CommunityInvite.objects.filter(to_user=user)

    @staticmethod
    def sent_invites(community):
        pass

    def invite(self, user, community):

        if self.is_member(user, community):
            raise AlreadyMemberError(_('Цей користувач вже в спільноті.'))

        c_invite, created = CommunityInvite.objects.get_or_create(to_user=user, from_community=community)

        if not created:
            raise InviteAlreadyExistsError(_('Запрошення вже було відправлено!'))


class Community(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=250, null=True, blank=True)
    administrators = models.ManyToManyField(User)
    invitation_code = models.CharField(null=True, blank=True, max_length=5)

    objects = CommunityManager()

    def __str__(self):
        return self.name

    def generate_invitation_code(self):

        import random
        import string

        while True:
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

            if not Community.objects.filter(invitation_code=code).exists():
                self.invitation_code = code
                self.save()
                break

    def get_sent_invites(self):
        return CommunityInvite.objects.filter(from_community=self)

    def get_absolute_url(self):
        return reverse('community', args=[self.id])


class CommunityInvite(models.Model):
    to_user = models.ForeignKey(User)
    from_community = models.ForeignKey(Community, on_delete=models.CASCADE)

    def __str__(self):
        return '{} > {}'.format(self.from_community, self.to_user)

    def reject(self):
        self.delete()

    def accept(self):
        self.to_user.profile.communities.add(self.from_community)
        self.delete()


class CommunityWallPost(models.Model):
    to_community = models.ForeignKey(Community, related_name='get_wallposts', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='+')
    text = models.TextField(max_length=1000)
    publication_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-publication_date', )


class Discussion(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_topics')
    author = models.ForeignKey(User)
    title = models.CharField(max_length=80)
    text = models.TextField(max_length=2500)
    publication_time = models.DateTimeField(auto_now_add=True)
    last_message = models.CharField(default='-', max_length=40)  # !!!!!!!!!

    class Meta:
        ordering = ('-publication_time', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('discussion', args=[self.community.id, self.id])

    def get_comments(self):
        return DiscussionComment.objects.filter(to_discussion=self)

    def comments_count(self):
        return DiscussionComment.objects.filter(to_discussion=self).count()

    def last_comment(self):
        if DiscussionComment.objects.filter(to_discussion=self).exists():
            return DiscussionComment.objects.filter(to_discussion=self)[0]
        return False


class DiscussionComment(models.Model):
    to_discussion = models.ForeignKey(Discussion, related_name='+', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='+')
    text = models.TextField(max_length=1000)
    publication_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Обговорення: {}, від: {}, текст: {}'.format(self.to_discussion.title, self.from_user.get_full_name(),
                                                            self.text[:150])

    # def save(self, *args, **kwargs):
    #
    #     super(DiscussionComment, self).save(*args, **kwargs)
    #     self.discussion.last_message = '{}, {}'.format(self.from_user.get_full_name(),
    #                                                    self.publication_date.strftime('%d %B, %H:%M'))
    #     self.discussion.save()

    class Meta:
        ordering = ('-publication_date', )


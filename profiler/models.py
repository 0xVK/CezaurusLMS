from django.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from profiler.exceptions import AlreadyExistsError, AlreadyFriendsError, AlreadySentRequestToYouError
from django.conf import settings
from communities.models import Community
import os


# ========================================================================================== #
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(_('Фотографія'), blank=True, null=True)
    sex = models.CharField('Стать', choices=(('M', 'Чоловік'), ('W', 'Жінка')), max_length=1)
    birthday = models.DateField(_('Дата народження'), blank=True, null=True)
    status = models.CharField(_('Статус'), max_length=140, blank=True, null=True)
    communities = models.ManyToManyField(Community, related_name='get_members', blank=True, null=True)
    is_expanded = models.BooleanField(_('Розришений профіль'), default=False)
    is_online = models.BooleanField(_('Онлайн'), default=False)
    location = models.CharField(_('Місто'), max_length=20, blank=True, null=True)
    school = models.CharField(_('Школа'), max_length=38, blank=True, null=True)
    form = models.CharField(_('Клас'), max_length=15, blank=True, null=True)

    class Meta:
        db_table = 'auth_profile'

    def __str__(self):
        return 'profile: {}'.format(self.user.username)

    def get_wall_posts(self):
        return ProfileWallPost.objects.filter(to_user=self.user)

    def get_friends(self):
        return Friendship.objects.filter(to_user=self.user)

    def get_communities(self):
        return self.communities.all()

    def get_picture(self):
        no_picture = 'http://i.imgur.com/CyZ1Gh3.png'

        try:
            filename = settings.MEDIA_ROOT + '/profile_pictures/' + self.user.username + '.jpg'
            picture_url = settings.MEDIA_URL + 'profile_pictures/' + self.user.username + '.jpg'

            if os.path.isfile(filename):
                return picture_url
            else:
                return no_picture

        except Exception as e:

            return no_picture


# ========================================================================================== #
class ProfileWallPost(models.Model):
    to_user = models.ForeignKey(User, related_name='get_wall_posts')
    from_user = models.ForeignKey(User, related_name='get_to_others_wall_posts')
    text = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-publication_date', )

    def __str__(self):
        return '{} {} -> {} {} : {}'.format(self.from_user.last_name,
                                            self.from_user.first_name[0],
                                            self.to_user.last_name,
                                            self.to_user.first_name[0],
                                            self.text[:120])


# ========================================================================================== #
class FriendshipManager(models.Manager):

    def get_friends(self, user):

        fr_list = []
        frs = self.filter(to_user=user)
        for fr in frs:
            fr_list.append(fr.from_user)
        return fr_list

    @staticmethod
    def requests(user):

        requests_list = []
        reqs = FriendshipRequest.objects.filter(to_user=user)
        for r in reqs:
            requests_list.append(r.from_user)
        return requests_list

    @staticmethod
    def sent_requests(user):

        sent_requests_list = []
        sent_requests = FriendshipRequest.objects.filter(from_user=user)
        for r in sent_requests:
            sent_requests_list.append(r.to_user)
        return sent_requests_list

    @staticmethod
    def is_sent_request(to_user, from_user):
        return FriendshipRequest.objects.filter(from_user=from_user, to_user=to_user).exists()

    def add_friend_request(self, to_user, from_user):

        if from_user == to_user:
            raise ValidationError(_('Не можна відправити запит самому собі!'))

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError(_('Цей користувач вже є Вашим другом.'))

        if self.is_sent_request(to_user=from_user, from_user=to_user):
            raise AlreadySentRequestToYouError(_('Цей користувач вже відправив Вам запит!'))

        f_request, created = FriendshipRequest.objects.get_or_create(from_user=from_user, to_user=to_user)

        if not created:
            raise AlreadyExistsError(_('Запит вже відправлено!'))

        return f_request

    def remove_friend(self, user1, user2):
        if self.are_friends(user1, user2):
            relation1 = Friendship.objects.get(to_user=user1, from_user=user2)
            relation2 = Friendship.objects.get(to_user=user2, from_user=user1)

            relation1.delete()
            relation2.delete()

            return True
        return False

    def are_friends(self, user1, user2):

        return self.filter(to_user=user1, from_user=user2).exists()


class Friendship(models.Model):

    to_user = models.ForeignKey(User, related_name='+')
    from_user = models.ForeignKey(User, related_name='+')

    objects = FriendshipManager()

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return '{} {} -> {} {}'.format(self.from_user.last_name,
                                       self.from_user.first_name[0],
                                       self.to_user.last_name,
                                       self.to_user.first_name[0])


# ========================================================================================== #
class FriendshipRequest(models.Model):

    to_user = models.ForeignKey(User, related_name='friendship_requests_received')
    from_user = models.ForeignKey(User, related_name='friendship_requests_sent')

    def accept(self):

        Friendship.objects.create(to_user=self.to_user, from_user=self.from_user).save()
        Friendship.objects.create(to_user=self.from_user, from_user=self.to_user).save()

        self.delete()

    def reject(self):

        self.delete()

    def cancel(self):

        self.delete()

    def __str__(self):
        return '{} {} -> {} {}'.format(self.from_user.last_name,
                                       self.from_user.first_name[0],
                                       self.to_user.last_name,
                                       self.to_user.first_name[0])


# ========================================================================================== #
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

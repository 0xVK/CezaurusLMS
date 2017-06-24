from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class MessageManager(models.Manager):

    def get_inbox(self, user):
        return self.filter(to_user=user)

    def get_outbox(self, user):
        return self.filter(from_user=user)


class Message(models.Model):

    to_user = models.ForeignKey(User, related_name='+')
    from_user = models.ForeignKey(User, related_name='+')
    text = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    objects = MessageManager()

    class Meta:
        ordering = ('-date',)
        db_table = 'user_messages'

    def __str__(self):
        return '{} -> {} - {}'.format(self.from_user.get_full_name(), self.to_user.get_full_name(), self.text[:100])

    def get_absolute_url(self):
        return reverse('show_message', args=[self.id])

from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

    class Meta(object):
        ordering = ("name",)

class Bookmark(models.Model):

    url = models.CharField(max_length=1000, blank=False)
    comment = models.TextField(blank=True)
    title = models.CharField(max_length=1000, blank=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    user = models.ForeignKey('auth.User', related_name="bookmarks", on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.url

    class Meta:
        unique_together = ("user", "url")

from django.db import models


class Comment(models.Model):
    author_id = models.IntegerField()
    post_id = models.IntegerField()
    message = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.message

from django.contrib.auth.models import User
from django.db.models import Sum

from django.db import models


class Author(models.Model):
    rating = models.SmallIntegerField(default=0)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def update_rating(self):
        post_rating = self.post_set.aggregate(rating=Sum('rating')).get('rating')
        if post_rating is None:
            post_rating = 0

        author_comments_rating = self.user.comment_set.aggregate(rating=Sum('rating')).get('rating')
        if author_comments_rating is None:
            author_comments_rating = 0

        users_comments_rating = 0
        for post in self.post_set.all():
            rating = post.comment_set.aggregate(rating=Sum('rating')).get('rating')
            if rating is None:
                rating = 0
            users_comments_rating += rating

        self.rating = post_rating * 3 + author_comments_rating + users_comments_rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    news = 'N'
    article = 'A'
    TYPES = (
        (news, 'НОВОСТЬ'),
        (article, 'СТАТЬЯ')
    )
    category_type = models.CharField(max_length=1, choices=TYPES, default=article)

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_category = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        if len(self.text) > 124:
            return f'{self.text[:124]}...'
        return f'{self.text}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

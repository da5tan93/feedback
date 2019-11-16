from django.db import models
from django.contrib.auth.models import User


cats = (
    (1, 'PC'),
    (2, 'Laptop'),
    (3, 'Monitor'),
    (3, 'bla bla')
)


class Product(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, verbose_name='Название')
    category = models.CharField(max_length=500,blank=False, null=False, choices=cats,
                                default=1, verbose_name='Категория')
    pro_text = models.TextField(max_length=2000, blank=True, verbose_name='')
    pro_image = models.ImageField(upload_to='images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')


Rating = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5)
)


class Review(models.Model):
    author = models.ForeignKey(User, null=True, blank=True, default=None, verbose_name='Автор',
                               on_delete=models.CASCADE, related_name='comments')
    email = models.EmailField(max_length=150, null=False, blank=False,default=None, verbose_name='e-mail')
    product = models.ForeignKey('webapp.Product', verbose_name='Товар', on_delete=models.CASCADE, related_name='товар')
    rev_text = models.TextField(max_length=3000, blank=False)
    score =  models.IntegerField(choices=Rating, blank=False, default=1)


class Categories(models.Model):
    name = models.CharField(max_length=20, verbose_name='Категории')

    def __str__(self):
        return self.name

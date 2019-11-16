from django import forms
from webapp.models import Product, Review, Categories
from django.core.exceptions import ValidationError


class ProductForm(forms.ModelForm):
    categories = forms.CharField(max_length=255, label='Categories', required=False)

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.fields['categories'].queryset = name.categories.all()

    class Meta:
        model = Product
        exclude = ['name', 'category']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tags = tags.split(',')
        tags = [tag.strip() for tag in tags]
        tags = filter(lambda tag: len(tag) > 0, tags)
        return tags

    def clean_title(self):
        title = self.cleaned_data['title']
        min_length = 10
        if len(title) < min_length:
            raise ValidationError(
                'Title name should be at least %(length)s symbols long.',
                code='title_too_short',
                params={'length': min_length}
            )
        return title.capitalize()

    def clean(self):
        super().clean()
        title = self.cleaned_data.get('title', '')
        text = self.cleaned_data.get('text', '')
        if title.lower() == text.lower():
            raise ValidationError('Text should not duplicate title name')
        return self.cleaned_data


class ReviewForm(forms.ModelForm):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.fields['product'].queryset = Product.objects.filter(
            category=Categories,
        ).exclude(name=name)

    class Meta:
        model = Review
        exclude = ['product', 'author', 'score']


class ProductCommentForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
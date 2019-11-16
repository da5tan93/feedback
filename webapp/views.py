from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import TemplateView, DetailView, CreateView,\
    UpdateView, DeleteView, FormView, ListView as DjangoListView
from webapp.models import Product, Review, Categories
from webapp.forms import ProductForm, ProductCommentForm, ReviewForm
# Create your views here.


class IndexView():
    template_name = 'product/index.html'
    context_object_name = 'product'
    model = Product
    ordering = ['-created_at']
    paginate_by = 5
    paginate_orphans = 1


class ProductView(DetailView):
    template_name = 'product/product.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['form'] = ProductCommentForm()
        comments = product.comments.order_by('-created_at')
        self.paginate_comments_to_context(comments, context)
        return context

    def paginate_comments_to_context(self, comments, context):
        paginator = Paginator(comments, 3, 0)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        context['paginator'] = paginator
        context['page_obj'] = page
        context['comments'] = page.object_list
        context['is_paginated'] = page.has_other_pages()


class ProductCreateView(CreateView):
    form_class = ProductForm
    model = Product
    template_name = 'product/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['name'] = self.request.name
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.name = self.request.name
        self.object.save()
        self.save_tags(form.cleaned_data.get('categories'))
        return HttpResponseRedirect(self.get_success_url())

    def save_tags(self, categories):
        for cat in categories:
            category, _ = Categories.objects.get_or_create(name=cat)
            self.object.categories.add(category)

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.pk})


class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'product/update.html'
    form_class = ProductForm
    context_object_name = 'product'

    def get_initial(self):
        return {'categories': self.get_category_string()}

    def get_category_string(self):
        categories = self.object.categories.all()
        cats = [category.name for category in categories]
        return ', '.join(cats)

    def form_valid(self, form):
        categories = form.cleaned_data.pop('categories')

        self.save_categories(categories)
        return super().form_valid(form)

    def save_categories(self, categories):
        self.object.categories.clear()
        for cat in categories:
            category, _ = Categories.objects.get_or_create(name=cat)
            self.object.categories.add(category)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['name'] = self.request.name
        return kwargs

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product/delete.html'
    context_object_name = 'product'
    success_url = reverse_lazy('webapp:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.categories = Categories
        self.object.save()
        return redirect(self.get_success_url())


class ListView(TemplateView):
    context_key = 'objects'
    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_key] = self.get_objects()
        return context

    def get_objects(self):
        return self.model.objects.all()


class DetailView(TemplateView):
    context_key = 'object'
    model = None
    key_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_key] = self.get_object()
        return context

    def get_object(self):
        pk = self.kwargs.get(self.key_kwarg)
        return get_object_or_404(self.model, pk=pk)


class CreateView(View):
    form_class = None
    template_name = None
    model = None
    redirect_url = None

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_redirect_url(self):
        return self.redirect_url

    def form_valid(self, form):
        self.object = self.model.objects.create(**form.cleaned_data)
        return redirect(self.get_redirect_url())

    def form_invalid(self, form):
        return render(self.request, self.template_name, context={'form': form})


class UpdateView(View):
    form_class = None
    template_name = None
    redirect_url = ''
    model = None
    key_kwarg = 'pk'
    context_key = 'object'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(initial=self.get_form_initial())
        context = self.make_context(form)
        return render(request, self.template_name, context=context)

    def get_form_initial(self):
        model_fields = [field.name for field in self.model._meta.fields]
        initial = {}
        for field in model_fields:
            initial[field] = getattr(self.object, field)
        print(initial)
        return initial

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = self.get_object()
        for field, value in form.cleaned_data.items():
            setattr(self.object, field, value)
        self.object.save()
        return redirect(self.get_redirect_url())

    def form_invalid(self, form):
        context = self.make_context(form)
        return render(self.request, self.template_name, context=context)

    def get_object(self):
        pk = self.kwargs.get(self.key_kwarg)
        return get_object_or_404(self.model, pk=pk)

    def make_context(self, form):
        return {
            'form': form,
            self.context_key: self.object
        }

    def get_redirect_url(self):
        return self.redirect_url


class DeleteView(View):
    template_name = None
    confirm_deletion = True
    model = None
    key_kwarg = 'pk'
    context_key = 'object'
    redirect_url = ''

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.confirm_deletion:
            return render(request, self.template_name, self.get_context_data())
        else:
            self.perform_delete()
            return redirect(self.get_redirect_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.perform_delete()
        return redirect(self.get_redirect_url())

    def perform_delete(self):
        self.object.delete()

    def get_context_data(self, **kwargs):
        return {self.context_key: self.object}

    def get_object(self):
        pk = self.kwargs.get(self.key_kwarg)
        return get_object_or_404(self.model, pk=pk)

    def get_redirect_url(self):
        return self.redirect_url


class ReviewListView(ListView):
    template_name = 'comment/list.html'
    model = Review
    context_object_name = 'comments'
    ordering = ['-created_at']
    paginate_by = 10
    paginate_orphans = 3


class ReviewForProductCreateView(CreateView):
    model = Review
    template_name = 'comment/create.html'
    form_class = ProductCommentForm

    def dispatch(self, request, *args, **kwargs):
        self.product = self.get_product()
        if self.product.is_categories:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = self.product.comments.create(
            author=self.request.user,
            **form.cleaned_data
        )
        return redirect('webapp:product_view', pk=self.product.pk)

    def get_product(self):
        product_pk = self.kwargs.get('pk')
        return get_object_or_404(Product, pk=product_pk)


class ReviewCreateView(CreateView):
    model = Review
    template_name = 'comment/create.html'
    form_class = ReviewForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.product.pk})


class ReviewUpdateView(UpdateView):
    model = Review
    template_name = 'comment/update.html'
    form_class = ProductCommentForm
    context_object_name = 'comment'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author \
               or self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.product.is_categories:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.product.pk})


class CommentDeleteView(DeleteView):
    model = Review

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author \
               or self.request.user.is_superuser

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.product.is_categories:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('webapp:product_view', kwargs={'pk': self.object.product.pk})

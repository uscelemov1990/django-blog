from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from myblog.models import Post
from myblog.forms import SigUpForm, SignInForm, FeedBackForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from taggit.models import Tag


class MainView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        paginator = Paginator(posts, 6)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
        }

        return render(request, 'myblog/home.html', context)


class PostDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, url=slug)
        common_tags = Post.tag.most_common()
        last_posts = Post.objects.all().order_by('-id')[:5]
        context = {
            'post': post,
            'common_tags': common_tags,
            'last_posts': last_posts
        }
        return render(request, 'myblog/post_detail.html', context)


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SigUpForm()
        context = {
            'form': form,
        }
        return render(request, 'myblog/signup.html', context)

    def post(self, request, *args, **kwargs):
        form = SigUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form,
        }
        return render(request, 'myblog/signup.html', context)


class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        context = {
            'form': form,
        }
        return render(request, 'myblog/signin.html', context)

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {
            'form': form,
        }
        return render(request, 'myblog/signin.html', context)


class FeedBackView(View):
    def get(self, request, *args, **kwargs):
        form = FeedBackForm()
        context = {
            'form': form,
            'title': 'Написать мне'
        }
        return render(request, 'myblog/contact.html', context)

    def post(self, request, *args, **kwargs):
        form = FeedBackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(f'От {name} | {subject}', message, from_email, ['amromashov@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Невалидный заголовок')
            return HttpResponseRedirect('success')
        context = {
            'form': form,
        }
        return render(request, 'myblog/contact.html', context)


class SuccessView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Спасибо'
        }
        return render(request, 'myblog/success.html', context)


class SearchResultsView(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        results = ""
        if query:
            results = Post.objects.filter(
                Q(h1__icontains=query) | Q(content__icontains=query)
            )
        paginator = Paginator(results, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'title': 'Поиск',
            'results': page_obj,
            'count': paginator.count
        }
        return render(request, 'myblog/search.html', context)


class TagView(View):
    def get(self, request, slug, *args, **kwargs):
        tag = get_object_or_404(Tag, slug=slug)
        posts = Post.objects.filter(tag=tag)
        common_tags = Post.tag.most_common()
        context = {
            'title': f'#ТЕГ {tag}',
            'posts': posts,
            'common_tags': common_tags
        }
        return render(request, 'myblog/tag.html', context)
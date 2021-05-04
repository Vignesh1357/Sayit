from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Post, Inbox, Profile
from django.views.generic import ListView, CreateView
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import os, random, string
from django.urls import reverse_lazy


# Inbox view at home page
class InboxListView(LoginRequiredMixin, ListView):
    model = Inbox
    template_name = 'user/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inboxes'] = Inbox.objects.filter(user=self.request.user.id)
        context['url'] = self.request.get_host() + '/' + 'sayit/message/'
        context['user_id'] = self.request.user.id
        return context

    context_object_name = 'inbox'


# Inbox creation view
class InboxCreateView(LoginRequiredMixin, CreateView):
    model = Inbox
    fields = ['inbox_name']
    template_name = 'user/new_inbox.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = Profile.objects.get(pk=self.request.user.id)
        return super(InboxCreateView, self).form_valid(form)


# link generation
def inbox(request, pk):
    inbox_obj = Inbox.objects.get(pk=pk)

    def inbox_url():
        x = ''.join(random.choice(string.ascii_uppercase) for i in range(16))
        return x

    inbox_obj.inbox_url = inbox_url()
    inbox_obj.save()
    return redirect('home')


# Message send view
class MsgCreateView(CreateView):
    model = Post
    fields = ['content']
    template_name = 'user/New_message.html'

    def form_valid(self, form):
        if self.request.user.id == self.kwargs.get('id'):
            messages.error(self.request, 'You cannot send messages to yourself')
            return super(MsgCreateView, self).form_invalid(form)
        else:
            form.instance.inbox_url = self.kwargs.get("message")
            form.save()
            return super(MsgCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Message sent!')
        return reverse_lazy('message', args=[self.kwargs.get('id'), self.kwargs.get('message')])


# Message view inside inbox
class MsgListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model = Post
    template_name = 'user/inbox.html'
    ordering = ['-date_posted']
    def test_func(self):
        try:
            if Inbox.objects.get(inbox_url=self.kwargs.get('message')).user.user == self.request.user:
                return True
            else:
                return False
        except:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(inbox_url=self.kwargs.get('message'))

        if self.kwargs.get('message') == 'None':
            context['message_box'] = False

        else:
            context['posts'] = posts
            context['first_post'] = posts.first()
            context['message_box'] = True
        return context



# User registration view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your account has been created! You are now able to login')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})


# User profile view
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if request.POST.get('update'):
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, f'Your account has been updated!')
                return redirect('profile')
        if request.POST.get('delete'):
            if request.user.profile.image.url == '/media/default.jpg':
                pass
            else:
                os.remove("C:\\Users\\vignesh\PycharmProjects\Sayit\sayit" + '\\' + request.user.profile.image.url)

            for inbox in Inbox.objects.filter(user=request.user.id):
                x = Post.objects.filter(inbox_url=inbox.inbox_url)
                x.delete()
            for inbox in Inbox.objects.filter(user=request.user.id):
                inbox.delete()
            request.user.delete()
            messages.success(request, f'Your account has been successfully deleted!')
            return redirect('login')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'user/profile.html', context)

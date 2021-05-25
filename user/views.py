from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import Post, Inbox, Profile
from django.views.generic import ListView, CreateView
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import os, random, string, boto3
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
        context['inbox_count'] = Inbox.objects.filter(user=self.request.user.id).count()

        return context

    context_object_name = 'inbox'

# Maximum inbox
def  max_inbox(request):
    return render(request,'user/max_inbox.html')
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
class MsgListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
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

    # adding context to req
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

    # deleting inbox and posts
    def post(self, request, *args, **kwargs):
        inbox = Inbox.objects.get(pk=self.kwargs.get('pk'))
        inbox.delete()
        try:
            posts = Post.objects.filter(inbox_url=self.kwargs.get('message'))
            for post in posts:
                post.delete()

        except:
            pass
        messages.success(request, f'Inbox deleted successfully')
        return redirect('home')

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
        u_form = UserUpdateForm(request.POST, instance=request.user)  # basic info update form
        # image update form
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        s3_object = boto3.client("s3")  # getting s3 bucket object from aws

        # Update info
        if request.POST.get('update'):
            if request.user.profile.image == 'default.jpg':
                picture = None
            else:
                picture = str(request.user.profile.image)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                if picture is None or p_form.cleaned_data['image'] == request.user.profile.image:
                    pass
                else:
                    # deleting previous profile picture
                    s3_object.delete_object(Bucket=os.environ.get('AWS_STORAGE_BUCKET_NAME'),
                                            Key=picture)
                    p_form.save()

                messages.success(request, f'Your account has been updated!')
                return redirect('profile')
        # delete account
        if request.POST.get('delete'):
            if request.user.profile.image == 'default.jpg':
                pass

            else:
                # deleting profile picture from aws s3 bucket
                s3_object.delete_object(Bucket=os.environ.get('AWS_STORAGE_BUCKET_NAME'),
                                        Key=str(request.user.profile.image))

            # deleting inbox urls, inbox, user
            for inbox in Inbox.objects.filter(user=request.user.id):
                posts = Post.objects.filter(inbox_url=inbox.inbox_url)
                for post in posts:
                    post.delete()
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


# To delete profile picture
def delete_profile(request, pk):
    obj = Profile.objects.get(pk=pk)
    if obj.image == 'default.jpg':
        pass
    else:
        s3_object = boto3.client("s3")
        s3_object.delete_object(Bucket=os.environ.get('AWS_STORAGE_BUCKET_NAME'),
                                Key=str(request.user.profile.image))
        obj.image = 'default.jpg'
        obj.save()
        messages.success(request, f'Profile picture has been successfully deleted!')
    return redirect('profile')

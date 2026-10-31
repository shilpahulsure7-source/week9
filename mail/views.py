from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings

from .forms import MailForm, RegisterForm
from .models import Mail


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inbox')
    else:
        form = RegisterForm()

    return render(request, 'mail/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect('inbox')
    else:
        form = AuthenticationForm()

    return render(request, 'mail/login.html', {'form': form})


@login_required
def inbox_view(request):
    mails = Mail.objects.filter(
        owner=request.user
    ).order_by('-timestamp')

    return render(
        request,
        'mail/inbox.html',
        {'mails': mails}
    )


@login_required
def compose_view(request):
    if request.method == 'POST':
        form = MailForm(request.POST)

        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']

            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient],
                    fail_silently=False,
                )
            except Exception as error:
                form.add_error(
                    None,
                    f'Unable to send mail: {error}'
                )
            else:
                mail = form.save(commit=False)
                mail.sender = request.user.email or settings.DEFAULT_FROM_EMAIL
                mail.owner = request.user
                mail.save()

                return redirect('inbox')
    else:
        form = MailForm()

    return render(
        request,
        'mail/compose.html',
        {'form': form}
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
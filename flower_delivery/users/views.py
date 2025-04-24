# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # Добавьте этот импорт
from users.forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required  # Только для авторизованных пользователей
def profile(request):
    return render(request, 'users/profile.html', {
        'catalog_url': '/catalog/',  # URL для каталога товаров
        'order_history_url': '/orders/history/',  # URL для истории заказов
    })
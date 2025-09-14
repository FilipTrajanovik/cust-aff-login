from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from .forms import CustomerForm, CustomerEditForm, CustomerCashOutForm, CryptoTransferForm, ConversionForm
from .models import Customer, ManagerProfile, UserWallet, Cryptocurrency, CryptoConvert, CryptoTransfer, ChatRoom, \
    ChatMessage
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from datetime import timedelta
from django.utils import timezone
from django.db import transaction

from .utils import fetch_crypto_news, summarize_text
from django.utils.timezone import now

from django.http import JsonResponse
from django.db.models import Q


# Create your views here.
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('/')


# MANAGER LOGIN
def manager_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and hasattr(user, 'managerprofile'):
            login(request, user)
            return redirect('manager_dashboard')
        else:
            return render(request, 'manager_login.html', {'error': 'invalid_credentials'})
    return render(request, 'manager_login.html')


# MANAGER DASHBOARD
@login_required(login_url='/manager/login')
def manager_dashboard(request):
    if not hasattr(request.user, 'managerprofile'):
        return redirect('manager_login')
    profile = ManagerProfile.objects.get(user=request.user)
    query = request.GET.get('q')
    if query:
        customers = Customer.objects.filter(
            manager=profile,
            username__icontains=query
        ) | Customer.objects.filter(
            manager=profile,
            email__icontains=query
        ) | Customer.objects.filter(
            manager=profile,
            phone__icontains=query
        )
    else:
        customers = Customer.objects.filter(manager=profile)

    total_unread_count = ChatMessage.objects.filter(
        room__customer__manager=profile,
        sender_customer__isnull=False,  # Messages from customers
        is_read=False
    ).count()

    return render(request, 'manager_dashboard.html', {'customers': customers
                                                      , 'total_unread_count': total_unread_count})


# CUSTOMER LOGIN
def customer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            customer = Customer.objects.get(username=username)

            if customer.is_locked:
                return render(request, 'customer_locked.html', {
                    'customer': customer,
                    'locked_reason': customer.locked_reason,
                    'locked_at': customer.locked_at
                })

            if check_password(password, customer.password) or password == customer.raw_password:
                request.session['customer_id'] = customer.id
                return redirect('customer_dashboard')
            else:
                return render(request, 'customer_login.html', {'error': 'Invalid credentials'})
        except Customer.DoesNotExist:
            return render(request, 'customer_login.html', {'error': 'Invalid credentials'})

    return render(request, 'customer_login.html')


# CUSTOMER DASHBOARD
def customer_dashboard(request):
    customer_id = request.session['customer_id']
    if not customer_id:
        return redirect('customer_login')
    customer = Customer.objects.get(id=customer_id)
    context = {
        'customer': customer,
        "btc_amount": round(customer.balance / 65000, 2),
        "eth_amount": round(customer.balance / 3700, 2),
        "xrp_amount": round(customer.balance / 0.5, 2),
        "xlm_amount": round(customer.balance / 0.3, 2),
    }
    return render(request, 'customer_dashboard.html', context)


# CUSTOMER CREATION
@login_required(login_url='/manager/login')
def create_customer(request):
    if not hasattr(request.user, 'managerprofile'):
        return redirect('manager_login')

    raw_password = None

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            manager_profile = ManagerProfile.objects.get(user=request.user)
            customer, raw_password = form.save(manager=manager_profile)
            messages.success(request, 'Customer created successfully!')
            return render(request, 'customer_created.html', {'raw_password': raw_password, 'customer': customer})
    else:
        form = CustomerForm()

    return render(request, 'create_customer.html', {'form': form})


# VIEW CUSTOMER INFO
@login_required(login_url='/manager/login/')
def view_customer(request, id):
    customer = Customer.objects.get(id=id)
    return render(request, 'customer_detail.html', {'customer': customer})


@login_required(login_url='/manager/login/')
def edit_customer(request, id):
    customer = Customer.objects.get(id=id)

    if request.method == 'POST':
        form = CustomerEditForm(request.POST, instance=customer)
        if form.is_valid():
            updated_customer = form.save()

            if updated_customer.can_cashout:
                return redirect('confirm_cashout', id=updated_customer.id)

            updated_customer.password = make_password(updated_customer.raw_password)
            updated_customer.save()
            return redirect('manager_dashboard')
    else:
        form = CustomerEditForm(instance=customer)

    messages.success(request, 'Customer updated successfully!')

    return render(request, 'edit_customer.html', {'form': form, 'customer': customer})


@login_required(login_url='/manager/login/')
def confirm_cashout(request, id):
    customer = Customer.objects.get(id=id)
    # if request.method == 'POST':
    #        form = CustomerCashOutForm(request.POST, instance=customer)
    #       if form.is_valid():
    #          customer = form.save(commit=False)
    #         customer.payout_date = timezone.now().date() + timedelta(30)
    #        customer.save()
    #       messages.success(request, 'Customer cash out successfully!')
    #      return redirect('manager_dashboard')
    # else:
    #    form = CustomerCashOutForm(instance=customer)
    # customer.payout_date = timezone.now().date() + timedelta(days=30)

    customer.payout_date = timezone.now().date() + timedelta(days=45)
    customer.save()

    return redirect('manager_dashboard')


@login_required(login_url='/manager/login/')
def delete_customer(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    messages.success(request, 'Customer deleted successfully.')
    return redirect('manager_dashboard')


@login_required(login_url='/customers/login/')
def withdraw_page(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)

    if customer.has_withdrawn:
        messages.info(request, "⚠️ You have already withdrawn your funds.")
        return redirect('crypto_wallets')

    with transaction.atomic():
        btc = Cryptocurrency.objects.get(name__iexact="Bitcoin")
        btc_wallet, _ = UserWallet.objects.get_or_create(customer=customer, cryptocurrency=btc)

        total_usd = 0
        for wallet in customer.wallets.select_related('cryptocurrency'):
            print(f"{wallet.cryptocurrency.name}: {wallet.balance}")
            if wallet.cryptocurrency != btc and wallet.balance > 0:
                total_usd += wallet.balance * wallet.cryptocurrency.value_usd
                wallet.balance = 0
                wallet.save()

        btc_amount = total_usd / btc.value_usd if btc.value_usd else 0
        print("Converted BTC amount:", btc_amount)

        btc_wallet.balance += btc_amount
        btc_wallet.save()

        customer.has_withdrawn = True
        customer.save()

    messages.success(request, f"✅ Withdraw successful! {btc_amount:.6f} BTC added.")
    return redirect('crypto_wallets')


@login_required(login_url='/customers/login/')
def crypto_home(request):
    customer_id = request.session['customer_id']
    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)
    wallets = customer.wallets.select_related('cryptocurrency')

    context = {
        'customer': customer,
        'wallets': wallets
    }
    return render(request, 'crypto_dashboard.html', context)


@login_required(login_url='/customers/login/')
def crypto_transfer(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)

    if request.method == 'POST':
        form = CryptoTransferForm(customer, request.POST)
        if form.is_valid():
            receiver = form.cleaned_data['receiver']
            cryptocurrency = form.cleaned_data['cryptocurrency']
            amount = form.cleaned_data['amount']

            # Get sender wallet
            try:
                sender_wallet = UserWallet.objects.get(customer=customer, cryptocurrency=cryptocurrency)
            except UserWallet.DoesNotExist:
                messages.error(request, "You don't have a wallet for this cryptocurrency.")
                return redirect('crypto_transfer')

            if sender_wallet.balance < amount:
                messages.error(request, "Insufficient funds")
                return redirect('crypto_transfer')

            # Get or create receiver wallet
            receiver_wallet, _ = UserWallet.objects.get_or_create(
                customer=receiver,
                cryptocurrency=cryptocurrency,
                defaults={'balance': 0}
            )

            # Perform the transfer
            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            sender_wallet.save()
            receiver_wallet.save()

            # Save transfer
            transfer = form.save(commit=False)
            transfer.sender = customer
            transfer.receiver = receiver
            transfer.save()

            messages.success(request, f"✅ Sent {amount} {cryptocurrency.name} to {receiver.username}")
            return redirect('display_wallets')
    else:
        form = CryptoTransferForm(customer)

    return render(request, 'crypto_transfer.html', {'form': form, 'customer': customer})


@login_required(login_url='/customers/login/')
def display_wallets(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)
    wallets = customer.wallets.select_related('cryptocurrency')

    for wallet in wallets:
        wallet.estimated_value = wallet.balance * wallet.cryptocurrency.value_usd

    context = {
        'customer': customer,
        'wallets': wallets
    }
    return render(request, 'crypto_wallets.html', context)


@login_required(login_url='/customers/login/')
def crypto_profile(request):
    customer_id = request.session['customer_id']
    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)

    transfers = CryptoTransfer.objects.filter(sender=customer).select_related('cryptocurrency', 'receiver').order_by(
        "-id")
    conversions = CryptoConvert.objects.filter(customer=customer).select_related('from_crypto', 'to_crypto').order_by(
        "-id")

    context = {
        'customer': customer,
        'transfers': transfers,
        'conversions': conversions
    }
    return render(request, 'crypto_profile.html', context)


@login_required(login_url='/customers/login/')
def crypto_conversion(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = Customer.objects.get(id=customer_id)

    if request.method == 'POST':
        form = ConversionForm(customer, request.POST)  # ✅ pass request.POST here

        if form.is_valid():  # ✅ validate the form before using cleaned_data
            from_crypto = form.cleaned_data['from_crypto']
            to_crypto = form.cleaned_data['to_crypto']
            amount = form.cleaned_data['amount']

            if from_crypto == to_crypto:
                messages.error(request, "Cannot convert to same cryptocurrency")
                return redirect('crypto_convert')

            from_wallet = UserWallet.objects.get(cryptocurrency=from_crypto, customer=customer)
            if from_wallet.balance < amount:
                messages.error(request, "Insufficient funds")
                return redirect('crypto_convert')

            fee = amount * 0.10
            amount_after_fee = amount - fee

            from_price = from_crypto.value_usd
            to_price = to_crypto.value_usd

            usd_value = amount_after_fee * from_price
            converted_amount = usd_value / to_price

            to_wallet, _ = UserWallet.objects.get_or_create(
                cryptocurrency=to_crypto, customer=customer,
                defaults={'balance': 0}
            )

            from_wallet.balance -= amount
            to_wallet.balance += converted_amount

            from_wallet.save()
            to_wallet.save()

            CryptoConvert.objects.create(
                customer=customer,
                from_crypto=from_crypto,
                to_crypto=to_crypto,
                amount=amount,
                fee=fee
            )
            messages.success(
                request,
                f"✅ Successfully converted {amount} {from_crypto.name} ➝ {converted_amount:.6f} {to_crypto.name} (fee: {fee:.4f})"
            )
            return redirect('display_wallets')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = ConversionForm(customer)

    context = {
        'form': form,
        'customer': customer,
        'now': now()
    }
    return render(request, 'crypto_convert.html', context)


@login_required(login_url='/customers/login/')
def ai_news_recommendation(request):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    wallets = customer.wallets.select_related('cryptocurrency')

    news_feed = []
    for wallet in wallets:
        crypto_name = wallet.cryptocurrency.name
        articles = fetch_crypto_news(crypto_name)
        for article in articles:
            news_feed.append({
                'crypto': crypto_name,
                'title': article['title'],
                'url': article['url'],
                'source': article['source']['name'],
                'published_at': article['publishedAt'],
                'description': article['description'],
            })

    return render(request, 'crypto_news.html', {
        'customer': customer,
        'news': news_feed
    })


@login_required(login_url='/customers/login/')
def summarize_news(request):
    if request.method == 'POST':
        text = request.POST.get("text", "")
        if text:
            summary = summarize_text(text)
            return JsonResponse({'summary': summary})
    return JsonResponse({"summary": "InvalidResponse"}, status=400)


@login_required(login_url='/manager/login/')
def lock_customer(request, id):
    if not hasattr(request.user, 'managerprofile'):
        return redirect('manager_login')

    customer = Customer.objects.get(id=id)
    manager_profile = ManagerProfile.objects.get(user=request.user)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Account locked by manager')

        customer.is_locked = True
        customer.locked_reason = reason
        customer.locked_at = timezone.now()
        customer.save()

        messages.success(request, f'Customer {customer.username} has been locked out.')
        return redirect('manager_dashboard')

    return render(request, 'lock_customer.html', {'customer': customer})


@login_required(login_url='/manager/login/')
def unlock_customer(request, id):
    if not hasattr(request.user, 'managerprofile'):
        return redirect('manager_login')

    customer = Customer.objects.get(id=id)
    customer.is_locked = False
    customer.locked_reason = None
    customer.locked_at = None
    customer.locked_by = None
    customer.save()

    messages.success(request, f'Customer {customer.username} has been unlocked.')
    return redirect('manager_dashboard')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')


@login_required(login_url='/customers/login/')
def start_chat(request):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    room, created = ChatRoom.objects.get_or_create(
        customer=customer,
        is_active=True,
        defaults={
            'customer' : customer,
            'subject' : 'Support Chat'
        })

    return redirect('chat_room', room_id = room.id)

@login_required(login_url='/customers/login/')
def chat_room(request, room_id):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    room = ChatRoom.objects.get(id=room_id, customer=customer)

    mess = room.messages.order_by('created_at')

    return render(request, 'chat_room.html', {
        'room': room,
        'messages': mess,
        'customer': customer
    })

@login_required(login_url='/customers/login/')
def send_customer_message(request):
    if request.method == 'POST':
        customer = Customer.objects.get(id=request.session['customer_id'])
        room_id = request.POST.get('room_id')
        message_text = request.POST.get('message')

        if message_text and room_id:
            room = ChatRoom.objects.get(id=room_id, customer=customer)
            message = ChatMessage.objects.create(
                room = room,
                sender_customer = customer,
                message = message_text
            )
            room.last_message_at = timezone.now()
            room.save()
            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'timestamp': message.created_at.strftime('%H:%M')
            })

    return JsonResponse({'success': False})


@login_required(login_url='/customers/login/')
def get_chat_messages(request, room_id):
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)
    room = ChatRoom.objects.get(id=room_id, customer=customer)

    last_message_id = request.GET.get('last_id', 0)
    messages = room.messages.filter(id__gt=last_message_id)

    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'message': msg.message,
            'timestamp': msg.created_at.strftime('%H:%M'),
            'is_manager': bool(msg.sender_manager),
            'sender_name': msg.sender_manager.user.username if msg.sender_manager else msg.sender_customer.username
        })

    return JsonResponse({'messages': messages_data})


# Manager Views
@login_required(login_url='/manager/login')
def manager_chat_list(request):
    if not hasattr(request.user, 'managerprofile'):
        return redirect('manager_login')

    manager_profile = ManagerProfile.objects.get(user=request.user)

    # Get all chat rooms from manager's customers
    chat_rooms = ChatRoom.objects.filter(
        customer__manager=manager_profile,
        is_active=True
    ).annotate(
        unread_count=models.Count('messages', filter=models.Q(
            messages__sender_customer__isnull=False,
            messages__is_read=False
        ))
    ).order_by('-last_message_at')

    return render(request, 'manager_chat_list.html', {
        'chat_rooms': chat_rooms,
        'manager': manager_profile
    })


@login_required(login_url='/manager/login')
def manager_chat_room(request, room_id):
    if not hasattr(request.user, 'managerprofile'):
        return redirect('manager_login')

    manager_profile = ManagerProfile.objects.get(user=request.user)
    room = ChatRoom.objects.get(
        id=room_id,
        customer__manager=manager_profile
    )

    # Assign manager to room if not already assigned
    if not room.manager:
        room.manager = manager_profile
        room.save()

    messages = room.messages.order_by('created_at')

    return render(request, 'manager_chat_room.html', {
        'room': room,
        'messages': messages,
        'manager': manager_profile
    })


@login_required(login_url='/manager/login')
def send_manager_message(request):
    if request.method == 'POST':
        if not hasattr(request.user, 'managerprofile'):
            return JsonResponse({'success': False})

        manager_profile = ManagerProfile.objects.get(user=request.user)
        room_id = request.POST.get('room_id')
        message_text = request.POST.get('message')

        if message_text and room_id:
            room = ChatRoom.objects.get(
                id=room_id,
                customer__manager=manager_profile
            )
            message = ChatMessage.objects.create(
                room=room,
                sender_manager=manager_profile,
                message=message_text
            )
            room.last_message_at = timezone.now()
            room.save()

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'timestamp': message.created_at.strftime('%H:%M')
            })

    return JsonResponse({'success': False})
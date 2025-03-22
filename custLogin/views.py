from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from .forms import CustomerForm, CustomerEditForm, CustomerCashOutForm
from .models import Customer, ManagerProfile
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from datetime import timedelta
from django.utils import timezone


# Create your views here.
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('/')


# MANAGER LOGIN
def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
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
            manager = profile,
            phone__icontains=query
        )
    else:
        customers = Customer.objects.filter(manager=profile)
    return render(request, 'manager_dashboard.html', {'customers': customers})


# CUSTOMER LOGIN
def customer_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            customer = Customer.objects.get(username=username)
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
    return render(request, 'customer_dashboard.html', {'customer': customer})


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
            return render(request, 'customer_created.html', {'raw_password': raw_password, 'customer': customer})
    else:
        form = CustomerForm()

    messages.success(request, 'Customer created successfully!')
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
    if request.method == 'POST':
        form = CustomerCashOutForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.payout_date = timezone.now().date() + timedelta(30)
            customer.save()
            messages.success(request, 'Customer cash out successfully!')
            return redirect('manager_dashboard')
    else:
        form = CustomerCashOutForm(instance=customer)

    return render(request, 'confirm_cashout.html', {'form': form, 'customer': customer})

@login_required(login_url='/manager/login/')
def delete_customer(request, id):
    customer = Customer.objects.get(id=id)
    customer.delete()
    messages.success(request, 'Customer deleted successfully.')
    return redirect('manager_dashboard')
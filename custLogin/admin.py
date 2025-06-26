from django.contrib import admin

from custLogin.models import Customer, ManagerProfile, Cryptocurrency, UserWallet
from custLogin.utils import update_crypto_prices
from django.contrib import messages


# Register your models here.
class WalletInline(admin.TabularInline):
    model = UserWallet
    extra = 0
    readonly_fields = ['cryptocurrency', 'balance']


class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'coingecko_id', 'value_usd')
    actions = ['update_prices']

    @admin.action(description="🔄 Update cryptocurrency prices")
    def update_prices(self, request, queryset):
        update_crypto_prices()
        self.message_user(request, " Cryptocurrency prices updated successfully!", level=messages.SUCCESS)


class CustomerProfileAdmin(admin.ModelAdmin):
    exclude = ['manager', ]
    inlines = [WalletInline]
    actions = ['initialize_missing_wallets']

    def save_model(self, request, obj, form, change):
        obj.manager = request.user
        return super().save_model(request, obj, form, change)

    @admin.action(description="🛠 Initialize missing wallets for selected customers")
    def initialize_missing_wallets(self, request, queryset):
        cryptos = Cryptocurrency.objects.all()
        created_total = 0
        skipped_total = 0
        for customer in queryset:
            wallets = UserWallet.objects.filter(customer=customer)
            if any(wallet.balance > 0 for wallet in wallets):
                skipped_total += 1
                continue

            for crypto in cryptos:
                wallet, created = UserWallet.objects.update_or_create(
                    customer=customer,
                    cryptocurrency=crypto,
                    defaults={"balance": 0}
                )
                if created:
                    created_total += 1

        self.message_user(
            request,
            f"✅ {created_total} wallet(s) created. Skipped {skipped_total} customer(s) with existing funds.",
            level=messages.SUCCESS
        )


admin.site.register(Customer, CustomerProfileAdmin)
admin.site.register(ManagerProfile)
admin.site.register(Cryptocurrency, CryptocurrencyAdmin)
admin.site.register(UserWallet)

from django.contrib import admin

from custLogin.models import Customer, ManagerProfile

# Register your models here.

class CustomerProfileAdmin(admin.ModelAdmin):

    exclude=['manager', ]

    def save_model(self, request, obj, form, change):
        obj.manager = request.user
        return super().save_model(request, obj, form, change)

admin.site.register(Customer, CustomerProfileAdmin)
admin.site.register(ManagerProfile)
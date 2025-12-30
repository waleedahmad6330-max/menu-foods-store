from django.contrib import admin
from .models import Membership

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_paid', 'joined_at')
    list_filter = ('is_paid',)
    search_fields = ('user__username', 'phone', 'user__email')

admin.site.register(Membership, MembershipAdmin)
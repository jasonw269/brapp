from django.contrib import admin
from .models import Membership, MembershipLevel

admin.site.register(MembershipLevel)
admin.site.register(Membership)

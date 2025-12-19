"""
Django Admin Configuration for CalmSpace
"""

from django.contrib import admin
from .models import (
    User, Profile, Assessment, HealthData, Feedback,
    Professional, Appointment, UserAppointment, Clinic, Article, ChatMessage, Therapist
)
from .subscription_models import (
    SubscriptionPlan, UserSubscription, SubscriptionTransaction,
    Entitlement, UserEntitlement
)


# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'user_type', 'is_active', 'is_email_verified', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_email_verified']
    search_fields = ['email', 'name']
    ordering = ['-created_at']


# Therapist Admin
@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'specialization', 'created_at']
    search_fields = ['email', 'name', 'specialization']


# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'created_at']
    search_fields = ['user__email', 'location']


# Professional Admin
@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'created_at']
    search_fields = ['user__email', 'specialization']


# Appointment Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'professionals', 'start_time', 'end_time', 'status']
    list_filter = ['status']
    search_fields = ['user__email']


# User Appointment Admin
@admin.register(UserAppointment)
class UserAppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'therapist', 'start_time', 'end_time', 'status']
    list_filter = ['status']
    search_fields = ['user__email', 'therapist__name']


# Clinic Admin
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'address']
    search_fields = ['name', 'email']


# Article Admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id']


# Assessment Admin
@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'created_at']
    list_filter = ['type']
    search_fields = ['user__email']


# Health Data Admin
@admin.register(HealthData)
class HealthDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'created_at']
    search_fields = ['user__email']


# Feedback Admin
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__email']


# Chat Message Admin
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'therapist', 'created_at']
    search_fields = ['user__email', 'therapist__name']


# ==========================================
# SUBSCRIPTION ADMIN CLASSES
# ==========================================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'plan_type', 'price', 'currency', 
        'unlimited_appointments', 'premium_therapists', 'is_active'
    ]
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name', 'revenuecat_product_id']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'plan_type', 'revenuecat_product_id', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Features', {
            'fields': (
                'unlimited_appointments', 'premium_therapists',
                'unlimited_chat', 'priority_support', 'exclusive_content'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan', 'status', 'is_premium', 
        'expires_at', 'store', 'last_synced_at'
    ]
    list_filter = ['status', 'is_premium', 'store']
    search_fields = ['user__email', 'revenuecat_app_user_id']
    raw_id_fields = ['user', 'plan']
    readonly_fields = ['created_at', 'updated_at', 'last_synced_at']
    fieldsets = (
        ('User & Plan', {
            'fields': ('user', 'plan')
        }),
        ('RevenueCat', {
            'fields': ('revenuecat_app_user_id', 'revenuecat_customer_id')
        }),
        ('Status', {
            'fields': ('status', 'is_premium', 'store')
        }),
        ('Dates', {
            'fields': (
                'original_purchase_date', 'expires_at',
                'unsubscribe_detected_at', 'billing_issue_detected_at',
                'last_synced_at', 'created_at', 'updated_at'
            )
        }),
    )


@admin.register(SubscriptionTransaction)
class SubscriptionTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user_subscription', 'event_type',
        'product_id', 'price', 'store', 'created_at'
    ]
    list_filter = ['event_type', 'store']
    search_fields = ['transaction_id', 'product_id', 'user_subscription__user__email']
    raw_id_fields = ['user_subscription']
    readonly_fields = ['created_at', 'raw_payload']


@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ['name', 'revenuecat_entitlement_id', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'revenuecat_entitlement_id']


@admin.register(UserEntitlement)
class UserEntitlementAdmin(admin.ModelAdmin):
    list_display = ['user', 'entitlement', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'entitlement']
    search_fields = ['user__email', 'entitlement__name']
    raw_id_fields = ['user', 'entitlement']

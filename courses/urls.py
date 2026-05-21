from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.course_list,             name='course_list'),
    path('<int:pk>/apply/',                     views.course_apply,            name='course_apply'),
    path('applied/',                            views.course_applied,          name='course_applied'),
    path('details/<uuid:token>/',               views.applicant_detail_form,   name='applicant_detail_form'),
    path('details/<uuid:token>/submitted/',     views.course_details_submitted,name='course_details_submitted'),
    path('manage/',                             views.course_manage,           name='course_manage'),
    path('create/',                             views.course_create,           name='course_create'),
    path('<int:pk>/applications/',              views.course_applications,     name='course_applications'),
    path('application/<int:pk>/update/',        views.application_update,      name='application_update'),
    path('application/<int:pk>/resend/',        views.resend_acceptance_email, name='resend_acceptance_email'),
    path('application/<int:pk>/confirm-payment/', views.confirm_payment,       name='confirm_payment'),
]

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class BaseProtectedView(LoginRequiredMixin, TemplateView):
    """
    Base view that requires authentication.
    All protected views should inherit from this class.
    """
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

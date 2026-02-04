from django.shortcuts import redirect
from django.contrib import messages

def verified_farmer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('farmer_login')

        if not hasattr(request.user, 'farmerprofile'):
            messages.error(request, "Farmer access only")
            return redirect('farmer_login')

        if not request.user.farmer_profile.is_verified:
            return redirect('verification_pending')

        return view_func(request, *args, **kwargs)

    return wrapper

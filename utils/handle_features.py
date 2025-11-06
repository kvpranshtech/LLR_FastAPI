from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404

from dashboard.models import Feature, FeaturePermission

# def feature_required(feature_name):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             if not request.user.is_authenticated or not request.user.profile.features.filter(name=feature_name).exists():
#                 return HttpResponseForbidden("You do not have access to this feature.")
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

# def feature_required(feature_name):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#
#             fea = UserProfile.objects.filter(user = request.user).first()
#             print(fea.features)
#             if request.user.is_authenticated and request.user.profile.features.filter(name=feature_name).exists():
#                 print("=================permission granted !!")
#                 return view_func(request, *args, **kwargs)
#             print("=============================permission not granted !!")
#             return HttpResponseForbidden("You do not have access to this feature.")
#         return _wrapped_view
#     return decorator

from dashboard.models import UserProfile

# def feature_required(feature_name):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             user_profile = request.user  # Assuming each user has a related UserProfile
#             print('==========', request.user)
#             print('==========', user_profile)
#             feature = Feature.objects.filter(name=feature_name).first()  # Find the feature by name
#             user_feature = UserProfile.objects.filter(user=request.user,
#                                                       features=Feature.objects.filter(name=feature_name))
#             print("==-=--=-=-=-=-=-=-=-=-=-=-", user_feature)
#             if user_feature:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return JsonResponse({"message": "Feature not available"}, status=400)
#
#         return _wrapped_view
#
#     return decorator

from functools import wraps
from django.core.exceptions import PermissionDenied


# def feature_required(feature_name):
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             # Get the current user
#             user = request.user
#             try:
#                 user_profile = user
#                 user_features = user_profile.features.values_list('name', flat=True)
#                 # Check if the feature_name exists in the list of features
#                 if feature_name not in user_features:
#                     raise PermissionDenied(f"Feature '{feature_name}' is required.")
#             except UserProfile.DoesNotExist:
#                 # Handle case where the user does not have a profile
#                 raise PermissionDenied("User profile not found.")
#             # If the feature exists, continue with the view
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

# --------------------------
# def feature_required(feature_name):
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             if not request.user.is_authenticated:
#                 return JsonResponse({'error': 'Authentication required'}, status=403)
#
#             feature = get_object_or_404(Feature, name=feature_name)
#
#             if not request.user.profile.features.filter(id=feature.id).exists():
#                 return JsonResponse({'error': f'Feature "{feature_name}" is not available for this user.'}, status=403)
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

def feature_required(feature_name):
    """
    Decorator to check if a user has the required feature.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Please login to access .")

            # Check if the feature exists
            try:
                feature = Feature.objects.get(name=feature_name)
            except Feature.DoesNotExist:
                return HttpResponseForbidden("You do not have access to this feature.")

            # Check if the user has permission for the feature
            has_permission = FeaturePermission.objects.filter(user=request.user, feature=feature).exists()
            if not has_permission:
                # return JsonResponse({'error': f'Feature "{feature_name}" is not available for this user.'}, status=403)
                return HttpResponseForbidden("You do not have access to this feature.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


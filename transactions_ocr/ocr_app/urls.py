from django.urls import path
from .views import FileUploadView

app_name = 'ocr_app'

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
]

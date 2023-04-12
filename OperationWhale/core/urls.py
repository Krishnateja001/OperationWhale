from django.urls import path

from core.views import detect_whale_sound,train_model,index,recorder,simple_upload

urlpatterns = [
    path('',index,name='indexpage'),
    path('apps/usersound/',simple_upload,name='sound file upload'),
    path('apps/recorder.html',recorder,name='recorderpage'),
    path('detect/',detect_whale_sound,name='detect whale'),
    path('train/',train_model,name='train model')
]
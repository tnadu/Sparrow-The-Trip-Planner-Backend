from django.urls import path
from .views import SmallMemberViewSet


app_name = 'core'

smallMemberList = SmallMemberViewSet.as_view({
    'get': 'list'
})

smallMemberDetail = SmallMemberViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    path('member/list/', smallMemberList, name='small-member-list'),
    path('member/detail/<int:pk>/', smallMemberDetail, name='small-member-detail'),
]

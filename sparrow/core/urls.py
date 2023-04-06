from django.urls import path
from .views import SmallMemberViewSet, GroupViewSet


app_name = 'core'

smallMemberList = SmallMemberViewSet.as_view({
    'get': 'list'
})

smallMemberDetail = SmallMemberViewSet.as_view({
    'get': 'retrieve'
})

groupList = GroupViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

groupDetail = GroupViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    path('member/list/', smallMemberList, name='small-member-list'),
    path('member/detail/<int:pk>/', smallMemberDetail, name='small-member-detail'),
    path('group/list/', groupList, name='group-list'),
    path('group/detail/<int:pk>/', groupDetail, name='group-detail'),
]

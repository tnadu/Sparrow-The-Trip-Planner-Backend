from django.urls import path
from .views import *


app_name = 'core'


groupList = GroupViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

groupDetail = GroupViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

memberList = MemberViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

memberDetail = MemberViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

login = LoginViewSet.as_view({
    'post': 'post'
})

logout = LogoutView.as_view()

changePassword = ChangePasswordViewSet.as_view({
    'put': 'update'
})

##### Attraction #####
######################

attractionList = AttractionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

attractionDetail = AttractionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
})

##### BelongsTo #####
#####################

belongsToList = BelongsToViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

belongsToDetail = BelongsToViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
})

belongsToGroupMembers = BelongsToViewSet.as_view({
    'get': 'get_group_members'
})

belongsToAllGroupsForMember = BelongsToViewSet.as_view({
    'get': 'get_all_groups_for_member'
})

urlpatterns = [
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),

    path('member/list/', memberList, name='member-list'),
    path('member/detail/<int:pk>/', memberDetail, name='member-detail'),
    path('member/change-password/<int:pk>/', changePassword, name='member-change-password'),
    
    path('group/list/', groupList, name='group-list'),
    path('group/detail/<int:pk>/', groupDetail, name='group-detail'),
    
    path('attraction/list/', attractionList, name='attraction-list'),
    path('attraction/detail/<int:pk>/', attractionDetail, name='attraction-detail'),

    path('belongsTo/list/', belongsToList, name="belongsTo-list"),
    path('belongsTo/detail/<int:pk>/', belongsToDetail, name='belongsTo-detail'),
    path('belongsTo/getMembers/<int:pk>/', belongsToGroupMembers, name='belongsTo-get-group-members'),
    path('belongsTo/getGroups/<int:pk>/', belongsToAllGroupsForMember, name='belongsTo-get-all-groups-for-member')    
]

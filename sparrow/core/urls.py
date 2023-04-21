from django.urls import path
from .views import *


app_name = 'core'

routeList = RouteViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

# only needs to respond to write actions, patch & put
routeVerify = RouteViewSet.as_view({
    'patch': 'verifiy',
    'put': 'verifiy',
})
routeDetail = RouteViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
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
    'put': 'create'
})

belongsToDetail = BelongsToViewSet.as_view({
    'put': 'update',
    'delete': 'destroy'
})

# backup plan for belongsTo
# belongsToGroupMembers = BelongsToViewSet.as_view({ 'get': 'get_group_members'})
# belongsToAllGroupsForMember = BelongsToViewSet.as_view({'get': 'get_all_groups_for_member'})

##### Status #####
##################

statusList = StatusViewSet.as_view({
    'put': 'create'
})

statusDetail = StatusViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'deleta': 'destroy'
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
    
    path('route/list/', routeList, name='route-list'),
    path('route/detail/<int:pk>/', routeDetail, name='route-detail'),
    path('route/verify/<int:pk>/', routeVerify, name='route-verify'),

    path('belongsTo/list/', belongsToList, name="belongsTo-list"),
    path('belongsTo/detail/<int:pk>/', belongsToDetail, name='belongsTo-detail'),

    path('status/list/', statusList, name='status-list'),
    path('status/detail/', statusDetail, name='status-detail')
]

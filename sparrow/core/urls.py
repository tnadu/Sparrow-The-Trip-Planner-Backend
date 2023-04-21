from django.urls import path
from .views import *


app_name = 'core'
##### Route #####
######################
routeList = RouteViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

# only needs to respond to write actions, patch & put
routePublicToggle = RouteViewSet.as_view({
    'put': 'update',
    'get': 'retrieve'
})
routeDetail = RouteViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

##### Group #####
######################
groupList = GroupViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

groupDetail = GroupViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})
##### Member #####
######################
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
    'get': 'list'
})

statusDetail = StatusViewSet.as_view({
    'get': 'retrieve'
})

##### Notebook #####
#####################

notebookList = NotebookViewSet.as_view({
    'get' : 'list',
    'post' : 'create'
})
notebookDetail = NotebookViewSet.as_view({
    'get' : 'retrieve',
    'put' : 'update',
    'delete' : 'destroy'
})

isWithinList = IsWithinViewSet.as_view({
    'get': 'list',
    'delete': 'destroy'
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
    path('route/publicToggle/<int:pk>/', routePublicToggle, name='route-public-toggle'),

    path('belongsTo/list/', belongsToList, name="belongsTo-list"),
    path('belongsTo/detail/<int:pk>/', belongsToDetail, name='belongsTo-detail'),

    path('notebook/list/', notebookList, name='notebook-list'),
    path('notebook/detail/<int:pk>/', notebookDetail, name='notebook-detail'),

    path('status/list/', statusList, name='status-list'),
    path('status/detail/<int:pk>/', statusDetail, name='status-detail'),

    path('isWithin/delete/', isWithinList, name='ceva')
]   

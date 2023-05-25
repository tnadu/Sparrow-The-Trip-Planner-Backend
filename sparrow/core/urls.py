from django.urls import path
from .views import *

app_name = 'core'


##### Route #####
#################

routeList = RouteViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

routeDetail = RouteViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


##### Group #####
#################

groupList = GroupViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

groupDetail = GroupViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


##### Member #####
##################

memberList = MemberViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

memberDetail = MemberViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

removeProfilePhoto = MemberViewSet.as_view({
    'post': 'removeProfilePhoto'
})

changePassword = ChangePasswordViewSet.as_view({
    'put': 'update'
})

login = LoginViewSet.as_view({
    'post': 'post'
})

logout = LogoutView.as_view()


##### Attraction #####
######################

attractionList = AttractionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

attractionDetail = AttractionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})


##### BelongsTo #####
#####################

belongsToList = BelongsToViewSet.as_view({
    'post': 'create'
})

belongsToDetail = BelongsToViewSet.as_view({
    'get' : 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})


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
    'patch': 'partial_update',
    'delete' : 'destroy'
})

##### IsWithin #####
#####################

IsWithinList = IsWithinViewSet.as_view({
    'post' : 'create',
    'get': 'list'
})

IsWithinDetail = IsWithinViewSet.as_view({
    'put' : 'update',
    'patch': 'partial_update',
    'delete' : 'destroy'
})


##### RatingFlag #####
######################

RatingFlagList = RatingFlagViewSet.as_view({
    'get': 'list',
    'post' : 'create'
})

RatingFlagDetail = RatingFlagViewSet.as_view({
    'put' : 'update',
    'patch': 'partial_update',
    'delete' : 'destroy'
})


##### RatingFlagType #####
#####################

RatingFlagTypeList = RatingFlagTypeViewSet.as_view({
    'get': 'list'
})
RatingFlagTypeDetail = RatingFlagTypeViewSet.as_view({
    'get' : 'retrieve',
})


##### Tag #####
#####################

TagList = TagViewSet.as_view({
    'get': 'list'
})

TagDetail = TagViewSet.as_view({
    'get' : 'retrieve',
})


##### IsTag #####
#####################

IsTaggedList = IsTaggedViewSet.as_view({
    'post': 'create'
})

IsTaggedDetail = IsTaggedViewSet.as_view({
    'get' : 'retrieve',
    'delete': 'destroy'
})



urlpatterns = [
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),

    path('member/list/', memberList, name='member-list'),
    path('member/detail/<int:pk>/', memberDetail, name='member-detail'),
    path('member/change-password/<int:pk>/', changePassword, name='member-change-password'),
    path('member/remove-profile-photo/<int:pk>/', removeProfilePhoto, name='member-remove-profile-photo'),
    
    path('group/list/', groupList, name='group-list'),
    path('group/detail/<int:pk>/', groupDetail, name='group-detail'),
    
    path('attraction/list/', attractionList, name='attraction-list'),
    path('attraction/detail/<int:pk>/', attractionDetail, name='attraction-detail'),
    
    path('route/list/', routeList, name='route-list'),
    path('route/detail/<int:pk>/', routeDetail, name='route-detail'),

    path('belongsTo/list/', belongsToList, name="belongsTo-list"),
    path('belongsTo/detail/<int:pk>/', belongsToDetail, name='belongsTo-detail'),

    path('notebook/list/', notebookList, name='notebook-list'),
    path('notebook/detail/<int:pk>/', notebookDetail, name='notebook-detail'),

    path('status/list/', statusList, name='status-list'),
    path('status/detail/<int:pk>/', statusDetail, name='status-detail'),

    path('isWithin/list/', IsWithinList, name='isWithin-list'),
    path('isWithin/detail/<int:pk>/', IsWithinDetail, name='isWithin-detail'),

    path('ratingFlag/list/', RatingFlagList, name='ratingFlag-list'),
    path('ratingFlag/detail/<int:pk>/', RatingFlagDetail, name='ratingFlag-detail'),

    path('ratingFlagType/list/', RatingFlagTypeList, name='ratingFlagType-list'),
    path('ratingFlagType/detail/<int:pk>/', RatingFlagTypeDetail, name='ratingFlagType-detail'),

    path('tag/list/', TagList, name='tag-list'),
    path('tag/detail/<int:pk>/', TagDetail, name='tag-detail'),

    path('isTagged/list/', IsTaggedList, name='isTagged-list'),
    path('isTagged/detail/<int:pk>/', IsTaggedDetail, name='isTagged-detail')
]

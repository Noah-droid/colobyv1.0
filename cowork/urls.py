from django.urls import path
from django.views.generic import TemplateView
from cowork import views
# from .views import (
#     UploadFileView,
#     SwitchBranchView,
#     BranchList,
#     BranchDetail,
#     UploadedFileVersionList,
#     UploadedFileVersionDetail,
#     CommitList,
#     CommitDetail,
# )

urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html"), name='index'),
    path("room/<str:room_slug>/", views.RoomDetailView.as_view(), name='chat'),
    path("room/", views.RoomCreateJoinView.as_view(), name='room-create-join'),
    # path('public-room/<slug:slug>/', views.public_chat, name='public-room'),
    # path('post_message/', views.post_message, name='post-message'),
    path('room/<str:room_slug>/tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('room/<str:room_slug>/tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('room/<str:room_slug>/tasks/<int:pk>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    path('room/<str:room_slug>/comments/<int:pk>/', views.CommentRetrieveUpdateDestroyView.as_view(), name='comment-detail'),
    path('room/like/<str:room_slug>/', views.like_room, name='like-room'),
    path('room/tasks/<str:room_slug>/', views.RoomTasksView.as_view(), name='room_task'),
    # path('room/count/', views.UserRoomsView.as_view(), name='user_rooms'),

    # usernote endpoints (To F.Es the feature requires autosave 😉)
    path('user/notes/', views.UserNoteCreateView.as_view(), name='usernote-list-create'),
    path('user/notes/<int:pk>/', views.UserNoteRetrieveUpdateDestroyView.as_view(), name='usernote-retrieve-update-destroy'),


    # feature requests
    path('rooms/<int:room_id>/feature-requests/', views.FeatureRequestListCreateView.as_view(), name='feature-request-list-create'),
    path('rooms/<int:room_id>/feature-requests/<int:pk>/', views.FeatureRequestRetrieveUpdateDestroyView.as_view(), name='feature-request-retrieve-update-destroy'),


    # Search 
    path('search/', views.SearchAPIView.as_view(), name='search'),

    path('userdata', views.user_data, name='userdata'),

    #  path('send-email/', views.send_email_view, name='send_email'),
    path('protected/', views.ProtectedAPIView.as_view(), name='protected'),
    path('generate-api-key/', views.GenerateAPIKeyView.as_view(), name='generate_api_key'),


    path('notifications/', views.NotificationList.as_view(), name='notification-list'),
    path('notifications/<int:pk>/', views.NotificationDetail.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/mark-as-read/', views.MarkNotificationAsRead.as_view(), name='mark-notification-as-read'),

    path('room/<str:room_slug>/upload/', views.UploadFileView.as_view(), name='upload_file'),
    path('room/<str:room_slug>/staged/', views.StagedFilesView.as_view(), name='stage_file'),
    path('room/<str:room_slug>/stage/<int:staged_file_id>/decision/', views.StageFileDecisionView.as_view(), name='stage_file_decision'),
    path('room/<str:room_slug>/room-files/', views.RoomFilesView.as_view(), name='room_files'),

    # path('room/<str:room_slug>/upload/', views.UploadFileView.as_view(), name='upload_file'),
    # path('room/<str:room_slug>/staged-files/', views.ListStagedFilesView.as_view(), name='list_staged_files'),
    # path('room/<str:room_slug>/stage/', views.StageFileView.as_view(), name='stage_file'),
    # path('room/<str:room_slug>/stage/<int:staged_file_id>/decision/', views.StageFileDecisionView.as_view(), name='stage_file_decision'),
    # path('room/<str:room_slug>/branches/<int:branch_id>/merge/', views.MergeStagedFilesView.as_view(), name='merge_staged_files'),
    # path('room/<str:room_slug>/branches/create/', views.CreateBranchView.as_view(), name='create_branch'),
    # path('room/upload/file/<str:room_slug>/', UploadFileView.as_view(), name='upload_file'),
    # path('room/switch/branch/<str:room_slug>/<int:file_id>/<int:branch_id>/', SwitchBranchView.as_view(), name='switch_branch'),

    # # Branch endpoints
    # path('room/branches/<str:room_slug>/', BranchList.as_view(), name='branch_list'),
    # path('room/branches/<str:room_slug>/<int:pk>/', BranchDetail.as_view(), name='branch_detail'),

    # # UploadedFileVersion endpoints
    # path('room/file_versions/<str:room_slug>/', UploadedFileVersionList.as_view(), name='file_version_list'),
    # path('room/file_versions/<str:room_slug>/<int:pk>/', UploadedFileVersionDetail.as_view(), name='file_version_detail'),

    # # Commit endpoints
    # path('room/commits/<str:room_slug>/', CommitList.as_view(), name='commit_list'),
    # path('room/commits/<str:room_slug>/<int:pk>/', CommitDetail.as_view(), name='commit_detail'),
    
    # path('room/send/<str:room_slug>/', views.send_message, name='send-message'), 
    # path('room/get/<str:room_slug>/', views.get_message, name='get-message'),
]



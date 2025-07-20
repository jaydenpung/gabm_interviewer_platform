"""
URL configuration for gabm_infra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, re_path, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from pages import views as pages_views

pages_urlpatterns = [
  re_path(r'^$', pages_views.home, name='home'),
  re_path(r'^login$', pages_views.login, name='login'),
  re_path(r'^create_avatar$', pages_views.create_avatar, name='create_avatar'),
  re_path(r'^interview/(?P<script_v>[^/]+)/$', pages_views.interview, name='interview'),
  re_path(r'^summary$', pages_views.summary, name='summary'),
  re_path(r'^summary_unprocessed_v1$', pages_views.summary_unprocessed_v1, name='summary_unprocessed_v1'),
  re_path(r'^download_p_data/(?P<participant_username>[^/]+)/(?P<script_v>[^/]+)/$', pages_views.download_p_data, name='download_p_data'),
  re_path(r'^download_p_audio_data/(?P<participant_username>[^/]+)/(?P<script_v>[^/]+)/$', pages_views.download_p_audio_data, name='download_p_audio_data'),
  re_path(r'^download_p_list_of_fin_interview/$', pages_views.download_p_list_of_fin_interview, name='download_p_list_of_fin_interview'),
  re_path(r'^force_proceed_survey_pt1/(?P<participant_username>[^/]+)/$', pages_views.force_proceed_survey_pt1, name='force_proceed_survey_pt1'),
  re_path(r'^transcript/(?P<participant_username>[^/]+)/(?P<script_v>[^/]+)/$', pages_views.transcript, name='transcript'),
  re_path(r'^handler_consent$', pages_views.handler_consent, name='handler_consent'),
  re_path(r'^handler_calibration$', pages_views.handler_calibration, name='handler_calibration'),
  re_path(r'^handler_take_one_step$', pages_views.handler_take_one_step, name='handler_take_one_step'),
  re_path(r'^handler_upload_spritesheet$', pages_views.handler_upload_spritesheet, name='handler_upload_spritesheet'),
  re_path(r'^handler_upload_surveycode$', pages_views.handler_upload_surveycode, name='handler_upload_surveycode'),
  re_path(r'^handler_upload_experiment_code$', pages_views.handler_upload_experiment_code, name='handler_upload_experiment_code'),
  re_path(r'^handler_download_summaries/(?P<starting_index>[^/]+)/(?P<desired_count>[^/]+)/$', pages_views.handler_download_summaries, name='handler_download_summaries'),

  re_path(r'^zipped_reset_check/(?P<participant_username>[^/]+)/(?P<script_v>[^/]+)/$', pages_views.zipped_reset_check, name='zipped_reset_check'),
]

urlpatterns = [
  path('admin/', admin.site.urls),
  path('accounts/', include('allauth.urls')),
  # Custom media serving - put first for priority
  re_path(r'^media/(?P<path>.*)$', pages_views.serve_media, name='serve_media'),
]

# Serve static files (always, regardless of DEBUG setting) 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += pages_urlpatterns




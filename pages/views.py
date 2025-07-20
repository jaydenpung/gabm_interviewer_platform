import os
import re
import json
import time
import base64
import io
import random
import string
import zipfile
import csv

from django.contrib.staticfiles.storage import staticfiles_storage
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, FileResponse, Http404
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from django.templatetags.static import static
from django.core.files.storage import default_storage

from global_methods import *
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageSequence
from pydub import AudioSegment
from allauth.account.signals import user_logged_in, user_signed_up
from interviewer_agent.interviewer_utils.settings import *
from interviewer_agent.agent_modules.vocalize import *
from interviewer_agent.agent_modules.transcribe import *

from .forms import *
from .models import *
from .interview_settings import *


from allauth.account.signals import user_signed_up
from django.dispatch import receiver


def serve_media(request, path):
    """Custom view to serve media files"""
    try:
        import os
        media_root = settings.MEDIA_ROOT
        file_path = os.path.join(media_root, path)
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(open(file_path, 'rb'))
        else:
            raise Http404("File not found")
    except Exception as e:
        raise Http404("File not found")


def controlled_randomness(weight):
  """
  Returns True or False based on the given weight.
  
  Parameters:
  - weight (float): A float value between 0 and 1 inclusive, where 0 means 
                    the function returns False 100% of the time,
                    1 means it returns True 100% of the time, and 0.5 means 
                    a 50% chance of True or False.
                    
  Returns:
  - bool: True or False based on the input weight.
  """
  # Check if the weight is at the boundaries
  if weight <= 0:
    return False
  elif weight >= 1:
    return True
  
  # Generate a random float between 0 and 1 and compare with the weight
  return random.random() < weight

def generate_random_string(n):
  return ''.join(random.choice('AB') for _ in range(n))

@receiver(user_signed_up)
def user_signed_up_request(sender, **kwargs):
  user = kwargs.pop('user')
  request = kwargs.pop('request')
  # Your custom logic here
  print(f"User {user.username} signed up.")
  # # For example, initializing user profile or setting default preferences.
  # if controlled_randomness(behavioral_study_activation_rate): 
  #   behs_module = BehavioralStudyModule.objects.create()
  #   behs_module.initialize()
  #   behs_module.save()
  #   user.behavioral_activated = True
  #   user.behavioral_module = behs_module
  #   user.save()

  user.camerer_activated = generate_random_string(5)
  user.save()

def jsp_log(message): 
  from datetime import datetime
  formatted_time = datetime.now().strftime("%H:%M:%S")
  print (f'[views.py] {formatted_time} -- {message}')


def generate_random_alphanumeric(length):
  # Combining letters and digits
  characters = string.ascii_letters + string.digits
  # Generating a random string of the given length
  random_string = ''.join(random.choice(characters) for i in range(length))
  return random_string


def extract_base_url(url):
    """
    Extract a specific substring from a URL.

    Args:
    url (str): The URL string.

    Returns:
    str: The extracted substring.
    """
    # Find the position of "/static/" and the start of the query string
    static_pos = url.find('/static/')
    query_start = url.find('?')

    # Extract the substring
    if static_pos != -1 and query_start != -1:
        return url[static_pos + len('/static/'):query_start]
    elif static_pos != -1:
        return url[static_pos + len('/static/'):]
    else:
        return "Invalid URL format"


def replace_file_num(url: str, new_num: int) -> str:
    """
    Replaces the number in the file path segment /5/ with a new number.

    Args:
    url (str): The original file path.
    new_num (int): The new number to replace with.

    Returns:
    str: The modified file path with the replaced number.
    """
    # Using regex to replace the number
    modified_url = re.sub(r'(\d+)(?=/\d{2}[A-Za-z]+/\d+\.)', 
                          str(new_num), url, 1)
    return modified_url


def get_curr_module(curr_user, list_completed_modules): 
  curr_ordered_modules = ordered_modules
  if curr_user.behavioral_activated: 
    curr_ordered_modules = ordered_modules_behavioral
  if curr_user.camerer_activated != "": 
    curr_ordered_modules = fin_ordered_modules

  for m in curr_ordered_modules: 
    if m not in list_completed_modules: 
      return m
  else: 
    return None


def home(request, det=None):
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  completed_modules = request.user.get_completed_modules()
  curr_module = get_curr_module(request.user, completed_modules)

  started_interviews = Interview.objects.filter(participant=request.user)
  started_interviews_scripts = [i.script_v for i in started_interviews]

  curr_timer = TimeoutTimer.objects.filter(participant=request.user)
  if curr_timer: 
    curr_timer = curr_timer[0]
  else: 
    curr_timer = None

  context = {"consent_form": ConsentForm(),  
             "survey_one_completion_form": SurveyCompletionForm(), 
             "survey_two_completion_form": SurveyCompletionForm(), 
             "Experiment_One_CodeForm": ExperimentCodeForm(),
             "Experiment_Two_CodeForm": ExperimentCodeForm(),
             "completed_modules": completed_modules, 
             "curr_module": curr_module,
             "started_interviews_scripts": started_interviews_scripts,
             "curr_timer": curr_timer}
  
  if det: 
    if "GSS_PT_1" in det: 
      context["survey_one_completion_form"] = det["GSS_PT_1"]
    elif "GSS_PT_2" in det: 
      context["survey_two_completion_form"] = det["GSS_PT_2"]

  template = "pages/home/home.html"
  return render(request, template, context)


def create_avatar(request):
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  image_paths = {
    'base': [static(f'gabm/img/pipoya-sprites/5/00Skin/{i+1}.png') 
             for i in range(4)],
    'clothes': [static(f'gabm/img/pipoya-sprites/5/01Costume/{i+1}.png') 
                for i in range(46)],
    'eyes': [static(f'gabm/img/pipoya-sprites/5/02Eye/{i+1}.png') 
             for i in range(23)],
    'hair': [static(f'gabm/img/pipoya-sprites/5/03Hair/{i+1}.png') 
             for i in range(34)],
    'hat': [static(f'gabm/img/pipoya-sprites/5/05Hat/{i+1}.png') 
            for i in range(15)],
    'glasses': [static(f'gabm/img/pipoya-sprites/5/06Glasses/{i+1}.png') 
                for i in range(11)],
    'beard': [static(f'gabm/img/pipoya-sprites/5/09Beard/{i+1}.png') 
              for i in range(5)]}

  image_paths_all = dict()
  for key, frame_five_aws_paths in image_paths.items(): 
    for frame_five_aws_path in frame_five_aws_paths: 
      image_paths_all[frame_five_aws_path] = dict()
      for frame in range(1, 13): 
        base_url = extract_base_url(frame_five_aws_path)
        replace_file_num(base_url, frame)      
        image_paths_all[frame_five_aws_path][str(frame)] = static(
          f'{replace_file_num(base_url, frame)}')

  context = {"curr_user": request.user,
             'image_paths': image_paths,
             'image_paths_all': image_paths_all,
             'empty_path': static(f'gabm/img/pipoya-sprites/5/empty.png') }
  template = "pages/create_avatar/create_avatar.html"
  return render(request, template, context)


def interview(request, script_v):
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  try: 
    interview = Interview.objects.get(participant=request.user,  
                                      script_v=script_v)
    interview.completed_sec = interview.completed_module_sec
    interview.completed_question_sec = interview.completed_module_sec
    interview.save()
  except: 
    interview = None

  interview_completed = False 
  if not interview:
    interview_completed = True
  else: 
    if interview.completed: 
      interview_completed = interview.completed

  context = {"interview_completed": interview_completed,
             "interviewer_turn": None, 
             "interviewer_utt": None,
             "curr_module": None,
             "script_v": script_v,
             "user_avatar": request.user.avatar}

  template = "pages/interview/interview.html"
  return render(request, template, context)


def summary(request):
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  all_interviews = Interview.objects.all().order_by("-created")

  context = {"curr_user": request.user, 
             "all_interviews": all_interviews}
  template = "pages/summary/summary.html"
  return render(request, template, context)


def summary_unprocessed_v1(request):
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  all_interviews = Interview.objects.filter(completed_sec=2709).filter(zipped_main=False).order_by("-created")

  context = {"curr_user": request.user, 
             "all_interviews": all_interviews}
  template = "pages/summary/summary.html"
  return render(request, template, context)


def download_p_data(request, participant_username, script_v): 
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  # Loading the current user and preparing the context to return.
  curr_user = Participant.objects.get(username=participant_username)
  try: 
    curr_interview = Interview.objects.get(participant=curr_user,
                                            script_v=script_v)
    curr_interview.zipped_main = True
    curr_interview.save()
  except: 
    curr_interview = None

  if not curr_interview:
    context = {}
    template = "pages/home/content.html"
    return render(request, template, context)

  qs = (InterviewQuestion.objects.filter(interview=curr_interview)
                                 .order_by('global_question_id'))
  transcript = ""
  for q in qs: 
    transcript += q.convo + "\n"

  meta = {"user_name": participant_username, 
          "email": curr_user.email, 
          "script_v": script_v, 
          "first_name": curr_user.first_name,
          "last_name": curr_user.last_name,
          "completed_modules": curr_user.completed_modules,
          "camerer_activated": curr_user.camerer_activated, 
          "created": curr_user.created,
          "audio_calibration_float": curr_user.audio_calibration_float}
  meta['created'] = meta['created'].isoformat()

  # Create a byte stream to hold the ZIP file
  in_memory_zip = io.BytesIO()

  # Create a ZIP file
  with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('interview.txt', transcript)
    # Convert the Python dictionary to a JSON string
    json_str = json.dumps(meta, indent=4)  # Use `indent` for pretty printing
    # Write the JSON string to a text file in the ZIP
    zf.writestr('meta.json', json_str)

  # Prepare the response, setting Content-Type and Content-Disposition
  # headers to trigger a file download
  response = HttpResponse(in_memory_zip.getvalue(), content_type='application/zip')
  response['Content-Disposition'] = f'attachment; filename="{participant_username}.zip"'
  # Make sure to seek to the start of the stream
  in_memory_zip.seek(0)

  return response


# def download_p_audio_data(request, participant_username, script_v): 
#   if not request.user.is_authenticated:
#     context = {}
#     template = "pages/home/landing.html"
#     return render(request, template, context)

#   # Loading the current user and preparing the context to return.
#   curr_user = Participant.objects.get(username=participant_username)
#   try: 
#     curr_interview = Interview.objects.get(participant=curr_user,
#                                             script_v=script_v)
#   except: 
#     curr_interview = None

#   if not curr_interview:
#     return sumary(request)

#   qs = (InterviewQuestion.objects.filter(interview=curr_interview)
#                                  .order_by('global_question_id'))
#   audios = []
#   for q in qs: 
#     x = InterviewAudio.objects.filter(question=q).order_by("created")
#     for i in x: 
#       audios += [i.audio_file]

#   print (audios)
#   # Start by checking if there's at least one file
#   if not audios or len(audios) == 0:
#       return HttpResponse("No audio files provided", status=400)
  
#   # Initialize combined_audio with the first file
#   try:
#     print ("HERE May: ", audios[0].name)
#     with default_storage.open(audios[0].name, 'rb') as f:
#         combined_audio = AudioSegment.from_file(f)
#     print ("HERE END May: ", audios[0].name)
#   except Exception as e:
#     return HttpResponse(f"Failed to load the first audio file: {str(e)}", status=500)

#   # Loop through the rest of the FieldFiles and combine
#   for field_file in audios[1:]:
#     try:
#       with default_storage.open(field_file.name, 'rb') as f:
#           audio_segment = AudioSegment.from_file(f)
#           combined_audio += audio_segment
#     except Exception as e:
#         return HttpResponse(f"Error processing file {field_file.name}: {str(e)}", status=500)



#   # Export combined audio to a byte stream
#   combined_audio_buffer = io.BytesIO()
#   combined_audio.export(combined_audio_buffer, format='wav')
#   combined_audio_buffer.seek(0)

#   # Create a byte stream for the ZIP file
#   in_memory_zip = io.BytesIO()

#   # Create a ZIP file
#   with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
#       # Add the combined audio file to the ZIP
#       zf.writestr('combined_audio.wav', combined_audio_buffer.getvalue())

#   # Prepare the response, setting Content-Type and Content-Disposition headers
#   response = HttpResponse(in_memory_zip.getvalue(), content_type='application/zip')
#   response['Content-Disposition'] = 'attachment; filename="combined_audio_files.zip"'

#   # Make sure to seek to the start of the stream
#   in_memory_zip.seek(0)
  
#   return response


def download_p_audio_data(request, participant_username, script_v): 
  if not request.user.is_authenticated:
      context = {}
      template = "pages/home/landing.html"
      return render(request, template, context)

  # Loading the current user and preparing the context to return.
  curr_user = Participant.objects.get(username=participant_username)
  try: 
      curr_interview = Interview.objects.get(participant=curr_user, script_v=script_v)
      curr_interview.zipped_audio = True
      curr_interview.save()
  except: 
      curr_interview = None

  if not curr_interview:
      return summary(request)

  qs = InterviewQuestion.objects.filter(interview=curr_interview).order_by('global_question_id')
  audio_file_names = []
  for q in qs: 
      x = InterviewAudio.objects.filter(question=q).order_by("created")
      for i in x: 
          audio_file_names.append(i.audio_file.name)

  if not audio_file_names or len(audio_file_names) == 0:
      return HttpResponse("No audio files provided", status=400)

  # Convert the list of audio file names to JSON format
  json_content = json.dumps({'audio_files': audio_file_names})

  # Create a response with appropriate headers to prompt a file download
  response = HttpResponse(json_content, content_type='application/json')
  response['Content-Disposition'] = f'attachment; filename="{curr_user.email}.json"'
  
  return response



def cleanup_interview(interview):
  new_interview = ""
  interview = interview.split("\n\n")

  for i_count, module in enumerate(interview): 
    module = module.split("\n")

    if module: 
      if module[-1][:len("Interviewer: Thank you")].lower() == "Interviewer: Thank you".lower(): 
        module = module[:-1]

    module = "\n".join(module)

    if module: 
      new_interview += module.strip() + "\n\n"

  return new_interview


def transcript(request, participant_username, script_v):
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  # Loading the current user and preparing the context to return.
  curr_user = Participant.objects.get(username=participant_username)
  try: 
    curr_interview = Interview.objects.get(participant=curr_user,
                                            script_v=script_v)
  except: 
    curr_interview = None

  if not curr_interview:
    context = {}
    template = "pages/home/content.html"
    return render(request, template, context)

  qs = (InterviewQuestion.objects.filter(interview=curr_interview)
                                 .order_by('global_question_id'))
  transcript = ""
  for q in qs: 
    transcript += q.convo + "\n"
  transcript = cleanup_interview(transcript)

  context = {"curr_user": curr_user,
             "curr_interview": curr_interview, 
             "transcript": transcript,
             "script_v": script_v}
  template = "pages/transcript/transcript.html"
  return render(request, template, context)


def login(request):
  context = {}
  template = "pages/login/login.html"
  return render(request, template, context)


def handler_consent(request):
  if request.method == 'POST':
    form = ConsentForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      curr_user = request.user
      curr_user.first_name = first_name
      curr_user.last_name = last_name
      curr_user.module_completed("Consent")
      curr_user.save()
      return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
  else:
    form = ConsentForm()
  return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def handler_calibration(request):
  if request.method == 'POST':
    curr_user = request.user
    calibration_float = float(request.POST.get('audioCalibrationFloat'))
    curr_user.audio_calibration_float = calibration_float
    curr_user.save()
    script_v = str(request.POST.get('script_v')).strip()
    return redirect('interview', script_v)  
  return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def handler_upload_spritesheet(request):
  if request.method == 'POST':
    form = SpriteSheetForm(request.POST, request.FILES)

    if form.is_valid():
      curr_user = request.user
      if not curr_user.avatar: 
        curr_user.avatar = Avatar.objects.create()

      # Save spritesheet
      spritesheet_image = form.cleaned_data.get('spritesheet')
      curr_filename = f"avatar{curr_user.avatar.id}/spritesheet.png"
      curr_user.avatar.sprite_sheet.save(curr_filename, 
        spritesheet_image, save=True)

      # Save front png
      curr_png = form.cleaned_data.get('front')
      curr_filename = f"avatar{curr_user.avatar.id}/front.png"
      curr_user.avatar.front_static.save(curr_filename, curr_png, save=True)

      # Save gifs
      curr_gif = form.cleaned_data.get('right_gif')
      curr_filename = f"avatar{curr_user.avatar.id}/right_gif.gif"
      curr_user.avatar.right_gif.save(curr_filename, curr_gif, save=True)

      curr_gif = form.cleaned_data.get('left_gif')
      curr_filename = f"avatar{curr_user.avatar.id}/left_gif.gif"
      curr_user.avatar.left_gif.save(curr_filename, curr_gif, save=True)

      curr_gif = form.cleaned_data.get('front_gif')
      curr_filename = f"avatar{curr_user.avatar.id}/front_gif.gif"
      curr_user.avatar.front_gif.save(curr_filename, curr_gif, save=True)

      curr_gif = form.cleaned_data.get('back_gif')
      curr_filename = f"avatar{curr_user.avatar.id}/back_gif.gif"
      curr_user.avatar.back_gif.save(curr_filename, curr_gif, save=True)

      # Finish
      curr_user.module_completed("Avatar")
      curr_user.save()

  return home(request)
  

def handler_take_one_step(request): 
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)
  if request.method != 'POST':
    return JsonResponse({})

  jsp_log(f"Starting handler_take_one_step -- step 1: load var")

  # Convert the string to JSON (Python dictionary). This is what is retrieved
  # from the frontend. 
  # Note that curr_POST_body is a dictionary of the following form: 
  # var newData = {
  #               started: false, 
  #               user_utt: null, 
  #               script_v: "{{script_v}}", 
  #               mime_type: null
  #             };
  # where started is only True for the very first signal of the session
  # (important: not of the interview, but of the currently connected currently
  #  -- this is used for hading the reloading of the page), and where user_utt
  # is the user's response in audio form. 
  curr_POST_body = json.loads(request.body.decode('utf-8'))

  curr_script_path = f"{INTERVIEW_AGENT_PATH}/interview_script/"
  curr_script_path += curr_POST_body["script_v"]
  interview_meta = read_json_file(f"{curr_script_path}/meta.json")
  try: 
    curr_interview = Interview.objects.get(
                       participant=request.user,
                       script_v=curr_POST_body["script_v"])
  except: 
    # If not curr_interview, this means we need to create the Interview
    # objcet for the participant. So we do that here. 
    curr_interview = Interview.objects.create(
      participant=request.user,
      script_v=curr_POST_body["script_v"],
      interviewer_summary=json.dumps(interview_meta["interviewer_summary"]), 
      module_count=interview_meta["module_count"],
      p_notes="{ }",
      pruned_p_notes="{ }",
      optional_key_phrases=f"My name is {request.user.get_full_name()}.")

  jsp_log(f"Starting handler_take_one_step -- step 2: start process_one_step")
  # [RUNNING THE MAIN ONE_STEP FUNCTION]
  step_packet = curr_interview.process_one_step(request.user,  
                                                curr_POST_body["started"],
                                                curr_POST_body["user_utt"],
                                                curr_POST_body["mime_type"],
                                                curr_POST_body["script_v"],
                                                interview_meta["total_sec"])

  jsp_log(f"Starting handler_take_one_step -- step 3: progress viz prep")
  progress_circle_rad = int(360 
    * (step_packet["completed_sec"]/interview_meta["total_sec"]))
  if progress_circle_rad > 360: progress_circle_rad = 360
  progress_circle_url = f"{settings.STATIC_URL}gabm/img/progress_arcs_thick/"
  progress_circle_url += f"{progress_circle_rad}.png"
  step_packet.update({"progress_circle_rad": progress_circle_rad,
                      "progress_circle_url": progress_circle_url})

  fin_percent = int(
    step_packet["completed_sec"]/interview_meta["total_sec"] * 90)
  if fin_percent == 0: fin_percent = 1
  step_packet.update({"fin_percent": fin_percent})

  jsp_log(f"Starting handler_take_one_step -- step 4: fin")
  # time.sleep(10)
  return JsonResponse(step_packet)


def handler_upload_surveycode(request):
  if request.method != 'POST':
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

  survey_part = None
  survey_code = None

  form = SurveyCompletionForm(request.POST)
  if form.is_valid():
    survey_part = form.cleaned_data['survey_part']
    survey_code_pt1 = form.cleaned_data['survey_code_pt1'].lower().strip()
    survey_code_pt2 = form.cleaned_data['survey_code_pt2'].lower().strip()

    survey_code = survey_code_pt1 + " " + survey_code_pt2

    print (survey_part)
    print (survey_code)

    
    if survey_part == "1": 
      if "isabella" in survey_code and "party" in survey_code:
        request.user.module_completed("Survey Pt.1")
        # request.user.module_completed_det(f"Survey Pt.1::{survey_code}")
        # two_weeks_later = datetime.datetime.now() + timedelta(seconds=30)
        two_weeks_later = datetime.datetime.now() + timedelta(days=14)
        print (datetime.datetime.now())
        print (two_weeks_later)
        new_timeout_timer = TimeoutTimer.objects.create(
          participant=request.user,
          endtime=two_weeks_later,
          cause="Survey Pt.2 wait time")
        new_timeout_timer.save()
        print (new_timeout_timer)
      else: 
        # The form will contain errors here
        det = {"GSS_PT_1": form}
        if survey_part == "2": 
          det = {"GSS_PT_2": form}
        return home(request, det)

    else: 
      if "maria" in survey_code and "isabella" in survey_code:
        request.user.module_completed("Survey Pt.2")
        request.user.module_completed_det(f"Survey Pt.2::{survey_code}")
      else: 
        # The form will contain errors here
        det = {"GSS_PT_1": form}
        if survey_part == "2": 
          det = {"GSS_PT_2": form}
        return home(request, det)

    # if "isabella" in survey_code and "party" in survey_code:
    #   if survey_part == "1": 
    #     request.user.module_completed("Survey Pt.1")
    #     # request.user.module_completed_det(f"Survey Pt.1::{survey_code}")
    #     two_weeks_later = datetime.datetime.now() + timedelta(seconds=30)
    #     two_weeks_later = datetime.datetime.now() + timedelta(days=14)
    #     print (datetime.datetime.now())
    #     print (two_weeks_later)
    #     new_timeout_timer = TimeoutTimer.objects.create(
    #       participant=request.user,
    #       endtime=two_weeks_later,
    #       cause="Survey Pt.2 wait time")
    #     new_timeout_timer.save()
    #     print (new_timeout_timer)
    #   else: 
    #     request.user.module_completed("Survey Pt.2")
    #     request.user.module_completed_det(f"Survey Pt.2::{survey_code}")

    # if (len(survey_code.strip()) == len(first_survey_code) 
    #   or len(survey_code.strip()) == len(second_survey_code)):
    #   if survey_part == "1": 
    #     if first_survey_code in survey_code: 
    #       request.user.module_completed("Survey Pt.1")
    #       request.user.module_completed_det(f"Survey Pt.1::{survey_code}")
    #       two_weeks_later = datetime.datetime.now() + timedelta(seconds=60)
    #       # two_weeks_later = datetime.datetime.now() + timedelta(days=14)
    #       print (datetime.datetime.now())
    #       print (two_weeks_later)
    #       new_timeout_timer = TimeoutTimer.objects.create(
    #         participant=request.user,
    #         endtime=two_weeks_later,
    #         cause="Survey Pt.2 wait time")
    #       new_timeout_timer.save()
    #       print (new_timeout_timer)
    #   else: 
    #     if first_survey_code in survey_code: 
    #       request.user.module_completed("Survey Pt.2")
    #       request.user.module_completed_det(f"Survey Pt.2::{survey_code}")

  return home(request)



def handler_upload_experiment_code(request): 
  if request.method == 'POST':
    form = ExperimentCodeForm(request.POST)
    if form.is_valid():
      code = form.cleaned_data['code']
      curr_user = request.user

      completed_modules = curr_user.get_completed_modules()
      curr_module = get_curr_module(curr_user, completed_modules)

      curr_round = 1
      if "Behavioral Study Pt.2" == curr_module: 
        curr_round = 2
      
      curr_behavioral_mod = curr_user.behavioral_module
      if curr_behavioral_mod.get_verify_code(code, curr_round): 
        curr_behavioral_mod.get_move_to_next_study(curr_round)

      if curr_behavioral_mod.get_check_if_fin(curr_round): 
        curr_user.module_completed(curr_module)
        
      curr_behavioral_mod.save()
      curr_user.save()
  return home(request)


def handler_download_summaries(request, starting_index, desired_count): 
  # Fetching the interviews
  all_interviews = list(Interview.objects.all().order_by("-created"))[int(starting_index):int(starting_index) + int(desired_count)]

  # Create an in-memory bytes buffer to store the zip file
  zip_buffer = io.BytesIO()



  # Create a zip file in the buffer
  with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
      for interview in all_interviews:
          interview_summary = interview.p_notes
          participant_email = interview.participant.email.lower()
          file_name = f"{participant_email}.txt"
          
          # Write each interview summary to a file within the zip
          zip_file.writestr(file_name, interview_summary)

  # Set the buffer position to the beginning
  zip_buffer.seek(0)

  # Serve the zip file as a downloadable response
  response = HttpResponse(zip_buffer, content_type='application/zip')
  response['Content-Disposition'] = 'attachment; filename=interview_summaries.zip'
  
  return response















def force_proceed_survey_pt1(request, participant_username):
  # Loading the current user and preparing the context to return.
  curr_user = Participant.objects.get(username=participant_username)
  print ("????", curr_user.get_curr_modules())
  if "Interview" in curr_user.get_curr_modules():
    print ("??")
    curr_user.module_completed("Survey Pt.1")
    two_weeks_later = datetime.datetime.now() + timedelta(days=14)
    print (datetime.datetime.now())
    print (two_weeks_later)
    new_timeout_timer = TimeoutTimer.objects.create(
      participant=curr_user,
      endtime=two_weeks_later,
      cause="Survey Pt.2 wait time")
    new_timeout_timer.save()
    print (new_timeout_timer)

  return summary_unprocessed_v1(request)


def download_p_list_of_fin_interview(request): 
  if not request.user.is_authenticated:
    context = {}
    template = "pages/home/landing.html"
    return render(request, template, context)

  # Loading the current user and preparing the context to return.
  all_users = Participant.objects.all().order_by("created")

  rows = []
  for curr_user in all_users:
    curr_row = []
    try: 
      if "Survey Pt.1" in curr_user.get_completed_modules(): 
        curr_interview = Interview.objects.get(participant=curr_user, script_v="new_avp_full_v1")
        if curr_interview.zipped_main: 
          curr_row += [curr_user.first_name, curr_user.last_name, curr_user.email, curr_user.created, curr_user.get_curr_modules()]
          rows += [curr_row]

    except: 
      pass
      

  # Create a buffer
  buffer = io.StringIO()
  # Create a CSV writer
  writer = csv.writer(buffer)
  # Write data to buffer
  for row in rows:
      writer.writerow(row)
  # Seek to the start of the stream
  buffer.seek(0)
  
  # Create a response
  response = HttpResponse(buffer, content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="participant_list.csv"'
  
  return response








def zipped_reset_check(request, participant_username, script_v): 
  if not request.user.is_authenticated:
      context = {}
      template = "pages/home/landing.html"
      return render(request, template, context)

  # Loading the current user and preparing the context to return.
  curr_user = Participant.objects.get(username=participant_username)
  try: 
      curr_interview = Interview.objects.get(participant=curr_user, script_v=script_v)
      curr_interview.zipped_audio = False
      curr_interview.zipped_main = False
      curr_interview.save()
  except: 
      curr_interview = None
  
  return summary(request)












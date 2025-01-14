from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from .models import Profile, File, Doctor, Patient, Invitation, Appointment
import os
from django.core.files import File as fileReader
import urllib.request
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import PIL
import random 
import string

URL="http://127.0.0.1:8000/"

@csrf_exempt
def check_user(request):
    data = JSONParser().parse(request)
    response = {
        "exists" : False,
        "validated" : False,
        "doctorId" : None,
        "type" : "doctor",
    }
    profiles = Profile.objects.filter(uid=data['uid'])
    if profiles.exists():
        profile = profiles.first()
        response["type"] = profile.type
        response["exists"] = True
        if (profile == "doctor"):
            doctor = Doctor.objects.get(id=profile.fid)
            response["validated"] = doctor.validated
    return JsonResponse(response)

@csrf_exempt
def register(request):
    data = JSONParser().parse(request)
    profile = Profile.objects.create(
        uid = data['uid'],
        name = data['name'],
        type = data['type'],
        avatarId = add_file(data['photoURL'], data['uid']),
    )
    if (data['type'] == "doctor"):
        profile.type = "doctor"
        profile.fid = create_doctor(data)
    else:
        profile.type = "patient"
        invitation = Invitation.objects.get(code=data['invitationCode'])
        data['doctorId'] = invitation.doctorId
        profile.fid = create_patient(data)
        invitation.delete()
    profile.save()
    response = {
        "uid" : profile.uid,
        "type" : profile.type,
        "name" : profile.name,
        "imageUrl" : get_file(profile.avatarId),
    }
    return JsonResponse(response)

@csrf_exempt
def get_user(request, uid):
    profiles = Profile.objects.filter(uid=uid)
    if not profiles.exists():
        return JsonResponse({})
    profile = profiles.first()
    response = {
        "uid" : profile.uid,
        "type" : profile.type,
        "name" : profile.name,
        "imageUrl" : get_file(profile.avatarId),
    }
    return JsonResponse(response)

def get_appointments(request, uid):
    profile = Profile.objects.get(uid=uid)
    if (profile.type == "doctor"):
        appointments = Appointment.objects.filter(doctorId=profile.fid).order_by('-scheduledDate')
    else:
        appointments = Appointment.objects.filter(patientId=profile.fid).order_by('-scheduledDate')
    response = []
    for appointment in appointments:
        response.append({
            "uid" : uid,
            "id" : appointment.id,
            "scheduledDate" : appointment.scheduledDate,
            "title" : appointment.title,
            "doctor" : {
                "name" : Profile.objects.filter(type="doctor").get(fid=appointment.doctorId).name,
                "imageUrl" : get_file(Profile.objects.filter(type="doctor").get(fid=appointment.doctorId).avatarId),
            },
            "patient" : {
                "id" : appointment.patientId,
                "name" : Profile.objects.filter(type="patient").get(fid=appointment.doctorId).name,
                "imageUrl" : get_file(Profile.objects.filter(type="patient").get(fid=appointment.patientId).avatarId),
            },
            "duration" : appointment.duration,
            "description" : appointment.description,
            "important" : appointment.important,
            "date" : appointment.date,
        })
    return JsonResponse(response, safe=False) 

def get_appointment(request, id):
    appointment = Appointment.objects.get(id=id)
    response = {
        "id" : appointment.id,
        "scheduledDate" : appointment.scheduledDate,
        "title" : appointment.title,
        "patient" : appointment.patientId,
        "duration" : appointment.duration,
        "description" : appointment.description,
        "important" : appointment.important,
    }
    return JsonResponse(response)

@csrf_exempt
def add_appointment(request):
    data = JSONParser().parse(request)
    appointment = Appointment.objects.create(
        doctorId = Profile.objects.get(uid=data['uid']).fid,
        patientId = data['patientId'],
        scheduledDate = data['scheduledDate'],
        duration = data['duration'],
        title = data['title'],
        description = data['description'],
        important = data['important'],
    )
    appointment.save()
    return JsonResponse({"success" : True})

@csrf_exempt
def update_appointment(request, id):
    data = JSONParser().parse(request)
    appointment = Appointment.objects.get(id=id)
    appointment.scheduledDate = data['scheduledDate']
    appointment.title = data['title']
    appointment.description = data['description']
    appointment.duration = data['duration']
    appointment.important = data['important']
    appointment.save()
    return JsonResponse({"success" : True})

@csrf_exempt
def delete_appointment(request, id):
    appointment = Appointment.objects.get(id=id)
    appointment.delete()
    return JsonResponse({"success" : True})


def create_doctor(data):
    doctor = Doctor.objects.create(
        birthday = data['birthday'],
        address = data['address'],
        phone = data['phone'],
        email = data['email'],
        validationImageId = data['validationImageId'],
    )
    doctor.save()
    return doctor.id

def get_doctor(request, uid):
    doctor = Doctor.objects.get(id=Profile.objects.get(uid=uid).fid)
    profile = Profile.objects.filter(type="doctor").filter(fid=doctor.id).first()
    response = {
        "uid" : uid,
        "id" : doctor.id,
        "name" : profile.name,
        "birthday" : doctor.birthday,
        "address" : doctor.address,
        "phone" : doctor.phone,
        "email" : doctor.email,
        "avatarId" : profile.avatarId,
    }
    return JsonResponse(response)

@csrf_exempt
def update_doctor(request, uid):
    data = JSONParser().parse(request)
    profile = Profile.objects.get(uid=uid)
    profile.name = data['name']
    profile.avatarId = data['avatarId']
    profile.save()
    doctor = Doctor.objects.get(id=profile.fid)
    doctor.birthday = data['birthday']
    doctor.address = data['address']
    doctor.phone = data['phone']
    doctor.email = data['email']
    doctor.save()
    return JsonResponse({"success": True})

def create_patient(data):
    patient = Patient.objects.create(
        birthday = data['birthday'],
        address = data['address'],
        phone = data['phone'],
        email = data['email'],
        doctorId = data['doctorId']
    )
    patient.save()
    return patient.id

def get_patients(request, uid):
    doctor = Doctor.objects.get(id=Profile.objects.get(uid=uid).fid)
    patients = Patient.objects.filter(doctorId=doctor.id)
    response = []
    for patient in patients:
        profile = Profile.objects.filter(type="patient").filter(fid=patient.id).first()
        response.append({
            "id" : patient.id,
            "uid" : profile.uid,
            "doctorId" : patient.doctorId,
            "name" : profile.name,
            "imageUrl" : get_file(profile.avatarId),
        })
    return JsonResponse(response, safe=False)

def get_patient(request, uid):
    profile = Profile.objects.get(uid=uid)
    patient = Patient.objects.get(id=profile.fid)
    response = {
        "uid" : uid,
        "id" : patient.id,
        "name" : profile.name,
        "birthday" : patient.birthday,
        "address" : patient.address,
        "phone" : patient.phone,
        "email" : patient.email,
        "avatarId" : profile.avatarId,
        "imageUrl" : get_file(profile.avatarId),
    }
    return JsonResponse(response)

@csrf_exempt
def transfer_patient(request):
    data = JSONParser().parse(request)
    patient = Patient.objects.get(id=Profile.objects.get(uid=data['patientUID']).fid)
    patient.doctorId = Profile.objects.get(uid=data['doctorUID']).fid
    patient.save()
    return JsonResponse({"success": True})

@csrf_exempt
def update_patient(request, uid):
    data = JSONParser().parse(request)
    profile = Profile.objects.get(uid=uid)
    profile.name = data['name']
    profile.avatarId = data['avatarId']
    profile.save()
    patient = Patient.objects.get(id=profile.fid)
    patient.birthday = data['birthday']
    patient.address = data['address']
    patient.phone = data['phone']
    patient.email = data['email']
    patient.save()
    return JsonResponse({"success": True})


def create_invitation(request, uid):
    doctor = Doctor.objects.get(id=Profile.objects.get(uid=uid).fid)
    invitation = Invitation.objects.create(
        doctorId = doctor.id,
        code = get_random_string(12),
    )
    invitation.save()
    return JsonResponse(invitation.code, safe=False)


@csrf_exempt
def upload_file(request):
    file = File.objects.create(file=request.FILES['file'])
    file.save()
    return JsonResponse(file.id, safe=False)

def add_file(imageUrl, uid):
    image = File.objects.create()
    result = urllib.request.urlretrieve(
        imageUrl + "?.jpg", settings.MEDIA_ROOT + "/" + uid + ".jpg")
    image.file = settings.MEDIA_ROOT + "/" + uid + ".jpg"
    image.save()
    return image.id

def get_file(id):
    return URL + "media/" + os.path.basename(File.objects.get(id=id).file.name)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
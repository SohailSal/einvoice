from icecream import ic
from django.db.models import Sum, Q, F
from django.db import transaction as trans
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


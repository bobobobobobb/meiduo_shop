from django.shortcuts import render
from django.views import View
from .models import Area
from django.http import JsonResponse, HttpResponseBadRequest
from utils.response_code import RETCODE

"""
前端:监测parent_id 是否发生变化, ajax
    /area/?parent_id = xxx

后端:parent_id 为空时, 返回省级地区
    parent_id  不为空时, 返回市县地区




"""


class AreasView(View):
    def get(self, request):
        parent_id = request.GET.get('parent_id')
        if parent_id is None:
            try:
                pros = Area.objects.filter(parent_id__isnull=True)
            except Area.DoesNotExist:
                return HttpResponseBadRequest('NOT FOUND')
            pro_list = []
            for pro in pros:
                pro_list.append({
                    "id": pro.id,
                    "name": pro.name
                })

            return JsonResponse({"pros": pro_list, "code": RETCODE.OK})

        else:
            try:
                areas = Area.objects.filter(parent_id=parent_id)

            except Area.DoesNotExist:
                return HttpResponseBadRequest('NOT FOUND')
            areas_list = []
            for area in areas:
                areas_list.append({
                    "id": area.id,
                    "name": area.name
                })
            return JsonResponse({"areas": areas_list, "code": RETCODE.OK})















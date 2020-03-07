from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template 

def other_page(request, page):
	try:
		template = get_template('bboard/' + page + '.html')
	except TemplateDoesNotExist:
		raise Http404
	return HttpResponse(template.render(request=request))

def index(request):
	return render(request, 'bboard/index.html')
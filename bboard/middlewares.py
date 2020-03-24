from .models import SubRubric

def avito_context_processor(request):
	context = {}
	context['rubrics'] = SubRubric.objects.all()
	return context
from django.shortcuts import render

from rest_framework.response  import Response 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from bboard.models import Bb, Comment
from .serializers import BbSerializers
from .serializers import BbDetailSerializers
from .serializers import CommentSerializers


#главная страница с объявлениями
@api_view(['GET'])
def bbs(request):
	if request.method == 'GET':
		bbs = Bb.objects.filter(is_active=True)[:10]
		serializers = BbSerializers(bbs, many=True)
		return Response(serializers.data)

#страница деталей объявлений
class BbDetailView(RetrieveAPIView):
	queryset = Bb.objects.filter(is_active=True)
	serializer_class = BbDetailSerializers

#страница комментариев
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def comments(request, pk):
	if request.method == 'POST':
		serializer = CommentSerializers(data = request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=HTTP_201_CREATED)
		else:
			return Response(serializer.errors, 
							status = HTTP_400_BAD_REQUEST)
	else:
		comments = Comment.objects.filter(is_active=True, bb=pk)
		serializer = CommentSerializers(comments, many = True)
		return Response(serializer.data)
from rest_framework import serializers
from bboard.models import Bb
from bboard.models import Comment

#форма для объявлений
class BbSerializers(serializers.ModelSerializer):
	class Meta:
		model = Bb
		fields = ('id', 'title', 'content', 'price', 'created_at')

#форма для деталей объявления
class BbDetailSerializers(serializers.ModelSerializer):
	class Meta:
		model = Bb
		fields = ('id', 'title', 'content', 'price', 'created_at',
					'contacts', 'image')

#форма для комментариев
class CommentSerializers(serializers.ModelSerializer):
	class Meta:
		model = Comment
		fields = ('bb', 'author', 'content', 'created_at')
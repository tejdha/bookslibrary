from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.name

from accounts.models import User

class Book(models.Model):
    title = models.CharField(max_length=100,)
    author = models.CharField(max_length=50,blank=True)
    description = models.TextField()
    pdf = models.FileField(upload_to='books/')
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='books')
    uploaded_time = models.DateTimeField(auto_now_add=True)
    pages = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
        ]


    def __str__(self):
        return f'{self.title} - {self.uploaded_by}'

    class Meta:
        ordering = ["-uploaded_time"]
    
from django.conf import settings

class Action(models.TextChoices):
        CREATED = 'CREATED','created'
        UPDATED = 'UPDATED','updated'
        DELETED = 'DELETED','deleted'

class ActivityLog(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='activities')
    action = models.CharField(max_length=20,choices=Action.choices)
    book = models.CharField(max_length=255,blank=True,null=True)
    changes = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} - {self.action}'

class Notificaton(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications')
    action = models.CharField(max_length=20,choices=Action.choices)
    field_name = models.CharField(max_length=100,blank=True)
    book_title=models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}{self.action}{self.book_title}'







    


# from rest_framework import serializers
# from .models import Category, Book
# from pypdf import PdfReader

# class CategorySerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Category
#         fields = ['id','name']

# class BookCreateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Book
#         fields = ['title','author','description','pdf','category']

#     def validate(self,attrs):
#         if Book.objects.filter(
#             title=attrs['title'],
#             author=attrs['author'],
#             ).exists():
#             raise serializers.ValidationError("A book with this title and author already exists.")
#         return attrs
    
#     def validate_pdf(self, value):

#         MAX_FILE_SIZE = 20 * 1024 * 1024

#         if value.size > MAX_FILE_SIZE :
#             raise serializers.ValidationError(
#                 "File size must not exceed 20 MB."
#             )
#         try:
#             reader = PdfReader(value)            
#         except Exception:
#             raise serializers.ValidationError(
#                 "Invalid or corrupted PDF file."
#             )
#         return value
    
#     def create(self, validated_data):
#         pdf_file = validated_data['pdf']

#         reader = PdfReader(pdf_file)
#         page_count = len(reader.pages)

#         validated_data['pages'] = page_count
#         validated_data['uploaded_by'] = self.context['request'].user

#         return Book.objects.create(**validated_data)

    

# class BooklistSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Book
#         fields = ['title','author','uploaded_by']

    
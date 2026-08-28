from rest_framework import serializers
from .models import Book, ActivityLog
from pypdf import PdfReader
from rest_framework.decorators import action


class BookCreateSerialzier(serializers.ModelSerializer):

    

    class Meta:
        model = Book
        fields = ['id','title','author','description','pdf','category']

    
    def validate(self,attrs):
        if Book.objects.filter(
            title=attrs['title'],
            author=attrs['author'],
        ).exists():
            raise serializers.ValidationError(
                'A Book Already Exists on That Title and Author.'
            )
        return attrs
    
    def validate_pdf(self,value):

        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF file are allowed"
            )

        if value.content_type != "application/pdf":
            raise serializers.ValidationError(
                "Only valid PDF content type is allowed"
            )
        
        MAX_SIZE = 20 * 1024 * 1024 
        if value.size > MAX_SIZE:
            raise serializers.ValidationError(
                'PDF Not Allowed to Exceed 20 MB.'
            )
        
        try:
            reader = PdfReader(value)
        except Exception:
            raise serializers.ValidationError(
                'Invalid or PDF Corrupted.'
            )
        
        return value
    
    def create(self, validated_data):
        pdf_file = validated_data['pdf']

        reader = PdfReader(pdf_file)
        page_count = len(reader.pages)

        validated_data['pages'] = page_count

        return Book.objects.create(**validated_data)

class BookUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = [
            "id",'title','author','description','pdf','category'
        ]
    
    def validate(self, attrs):
        
        title = attrs.get("title", self.instance.title)
        author = attrs.get("author", self.instance.author)

        if Book.objects.filter(
            title=title,
            author=author,
        ).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(
                "A Book Already Exists on That Title And Author"
            )
        return attrs

    def validate_pdf(self, value):

        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are allowed"
            )

        if value.content_type != "application/pdf":
            raise serializers.ValidationError(
                "Only valid PDF content type is allowed"
            )

        MAX_SIZE = 20 * 1024 * 1024

        if value.size > MAX_SIZE:
            raise serializers.ValidationError(
                "PDF Not Allowed to Exceed 20 MB"
            )

        try:
            reader = PdfReader(value)
        except Exception:
            raise serializers.ValidationError(
                "Invalid or Corrupted PDF"
            )
        return value

    def update(self, instance, validated_data):

        if "pdf" in validated_data:
            reader = PdfReader(validated_data["pdf"])
            validated_data['pages'] = len(reader.pages)

        return super().update(instance, validated_data)

class BookListSerializer(serializers.ModelSerializer):
    
    category = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['id','title','author','category','uploaded_by']

    def __str__(self):
        return self.name

class BookDetailsSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta: 
        model = Book
        fields = ['id','title','author','pages','description','category','uploaded_by','uploaded_time','pdf',]


class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityLog
        fields = ['action','book','changes','created_at']

   
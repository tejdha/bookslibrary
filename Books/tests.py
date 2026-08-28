from django.test import SimpleTestCase
from django.core.cache import cache

# Create your tests here.

from .cache_utils import invalidate_books_cache, BOOKS_CACHE_VERSION_KEY

# UNIT TESTING
class CacheUtilsTest(SimpleTestCase):
    def test_invalidate_books_cache(self):
        # THIS IS ARRAGE WHAT WE WANT TO RUN
        cache.set(BOOKS_CACHE_VERSION_KEY,1)
        # THIS IS ACT, WE NEED TO RUN WHAT WE ARRAGED
        invalidate_books_cache()
        # THIS IS ASSERT,THIS IS WHERE WE VERIFY WHAT HEPPENED AND WHAT EXPECTED
        self.assertEqual(
            cache.get(BOOKS_CACHE_VERSION_KEY),2
        )

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class BookAPITest(APITestCase):
    def test_unauthenticated_user_can_access_my_books(self):
        # arrange
        user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client.force_authenticate(user=user)

        # act
        response = self.client.get("/books/my_books/")

        # assert
        self.assertEqual(response.status_code,200)


from Books.models import Book,Category
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from pathlib import Path
from django.conf import settings

from unittest.mock import patch
from django.core.cache import cache

class BookAPITest(APITestCase):
    def test_authenticated_user_can_create_book(self):
        # arrange
        user = User.objects.create_user(\
            username="createuser",
            password="testpass123"
            )

        self.client.force_authenticate(user=user)

        category = Category.objects.create(
            name="create category"
        )

        pdf_path = Path(settings.MEDIA_ROOT) / "books" / "Build_Dont_Talk_hin11h9.pdf"

        with open(pdf_path, "rb") as pdf_file:
            pdf = SimpleUploadedFile(
                "Build_Dont_Talk_hin11h9.pdf",
                pdf_file.read(),
                content_type="application/pdf"
            )


        data = {
            "title" : "Create Book",
            "author" :"Create Author",
            "description" : "Test Description",
            "pdf": pdf,
            "category" : category.id,

        }

        #act
        response = self.client.post(
            reverse('book-list'),
            data,
            format='multipart'
            )

        # url = reverse("book-detail", kwargs={"pk": book.id})
        # response = self.client.get(url)         

        #assert

        self.assertEqual(response.status_code, 201)
        # self.assertEqual(response.data["title"],"Test Book")
        book = Book.objects.get(id=response.data["id"])

        self.assertEqual(book.title, "Create Book")
        self.assertEqual(book.uploaded_by, user)

    def test_owner_can_update_book(self):
        # arrange
        user = User.objects.create_user(
            username="updateuser",
            password="testpass123"
        )

        self.client.force_authenticate(user=user)

        category = Category.objects.create(
            name="Update Category"
        )

        pdf = SimpleUploadedFile(
            "create_test.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )

        book = Book.objects.create(
            title="Old Title",
            author = "Test Author",
            description="Test description",
            pdf=pdf,
            category=category,
            uploaded_by=user,
            pages=1,
        )

        # act
        response = self.client.put(
            reverse("book-detail", kwargs={"pk":book.id}),
            {
                "title" : "New Title"
            },
            format='multipart'
        )
        print("STATUS:", response.status_code)
        print("DATA:", response.data)

        # assert
        self.assertEqual(response.status_code,200)

    def test_owner_can_delete_book(self):

        # arrange
        user = User.objects.create_user(
            username='deleteuser',
            password='testpass123'
        )

        self.client.force_authenticate(user=user)

        category = Category.objects.create(
            name='Delete Category'
        )

        pdf_path = (
            Path(settings.MEDIA_ROOT) / 'books' / 'Build_Dont_Talk_hin11h9.pdf'
        )

        with open(pdf_path,"rb") as pdf_file:
            pdf = SimpleUploadedFile(
                "Build_Dont_Talk_hin11h9.pdf",
                pdf_file.read(),
                content_type="application/pdf"
            )

        book = Book.objects.create(
            title="Delete Book",
            author="Delete Author",
            description="Test description",
            pdf=pdf,
            category=category,
            uploaded_by=user,
            pages=1,
        )

        # act
        response = self.client.delete(
            reverse('book-detail', kwargs={'pk':book.id})
        )

        # assert
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Book.objects.filter(id=book.id).exists()
        )


    def test_non_owner_cannot_update_book(self):
        # arrange
        # user a 
        owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123'
        )
        # user b
        other_user = User.objects.create_user(
            username='other_user',
            email='other@test.com',
            password='testpass123'
        )

        # category
        category = Category.objects.create(
            name='Authorization Category'
        )

        pdf_path = Path(settings.MEDIA_ROOT)/ 'books' / 'Build_Dont_Talk_hin11h9.pdf'

        with open(pdf_path, 'rb') as pdf_file:
            pdf = SimpleUploadedFile(
                "Build_Dont_Talk_hin11h9.pdf",
                pdf_file.read(),
                content_type='application/pdf'
            )

        # existing book owned by user a
        book = Book.objects.create(
            title="Original Title",
            author="Test Author",
            description="Test Description",
            category=category,
            uploaded_by=owner,
            pages=1,
            pdf=pdf,
        )

        self.client.force_authenticate(user=other_user)

        # act
        response = self.client.put(
            reverse('book-detail',kwargs={'pk':book.id}),
            {
                "title" : "Hacked title"
            },
            format='multipart'
        )

        # assert
        self.assertEqual(response.status_code,403)
        book.refresh_from_db()
        self.assertEqual(book.title, "Original Title")

    def test_invalid_pdf_upload(self):
        # arrange
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.client.force_authenticate(user=user)

        category = Category.objects.create(
            name='invalid pdf category'
        )

        pdf = SimpleUploadedFile(
            'invalid.pdf',
            b'this is not a real pdf',
            content_type='application/pdf'
        )

        data = {
            "title" :'invalidpdf',
            "author":'testauthro',
            "description":'testdescription',
            "category":category.id,
            "uploaded_by":user,
            "pages":1,
            "pdf":pdf,
        }

        # act

        response = self.client.post(
            reverse('book-list'),
            data,
            format='multipart'
        )

        # assert

        # self.assertEqual(response.status_code,200)
        self.assertEqual(response.status_code,400)


    def test_invalidae_books_cache(self):
        # arrange
        with patch("Books.cache_utils.cache") as mock_cache:
            mock_cache.get.return_value = 5

        # act
            invalidate_books_cache()

        # assert
            mock_cache.set.assert_called_once_with(
                BOOKS_CACHE_VERSION_KEY,
                6,
                timeout=None
            )
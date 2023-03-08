from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from django.db import IntegrityError

from api.serializers import (
    UserSerializer,
    TokenSerializer,
    SignUpSerializer,
    GenreSerializer,
    TitleSerializer,
    CategorySerializer,
    TitleCreateSerializer,
    ReviewSerializer,
    CommentSerializer
)
from reviews.models import User, Title, Category, Genre, Review
from api.permissions import (
    AdminPermission,
    ModeratorPermission,
    OnlyReadAndNotUser,
    IsAuthorOrAdminOrModerator
)
from api.filters import TitleFilter
from api.utils import send_code_email


class UserViewSet(viewsets.ModelViewSet):
    """Список юзеров доступный только admin"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminPermission,)
    lookup_field = 'username'

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Настройка эндпоинта api/v1/users/me/

        Получение и изменение данных пользователя, если он прошел аунтификацию.
        """
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(APIView):
    """Классс проверки токена авторизации"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            user = get_object_or_404(User, username=username)
            confirmation_code = serializer.data['confirmation_code']
            if not default_token_generator.check_token(
                    user,
                    confirmation_code):
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpViewSet(APIView):
    """Класс авторизации"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user, _ = User.objects.get_or_create(
                    **serializer.validated_data)
            except IntegrityError:
                raise serializers.ValidationError()
            send_code_email(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс произведения."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (ModeratorPermission, OnlyReadAndNotUser,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleCreateSerializer
        return TitleSerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Класс жанр."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ModeratorPermission, OnlyReadAndNotUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug', url_name='category_slug'
    )
    def get_genre(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Класс категория.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ModeratorPermission, OnlyReadAndNotUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug', url_name='category_slug'
    )
    def get_category(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
        )
        serializer.save(
            author=self.request.user, review=review
        )

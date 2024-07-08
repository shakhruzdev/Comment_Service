from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import ValidationError

from .models import Comment
from .serializers import CommentSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests





class CommentViewSet(ViewSet):

    def check_token(self, token):
        response = requests.post('http://134.122.76.27:8114/api/v1/check/', data={'token': token})
        if response.status_code != 200:
            raise ValidationError({'error': 'Invalid token'})

    @swagger_auto_schema(
        operation_description='Create a comment',
        operation_summary='Create a comment',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='message'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='token'),
            },
            required=['post_id', 'message', 'token']
        ),
        responses={
            404: 'Not Found',
            200: CommentSerializer()
        },
        tags=['post']
    )
    def create(self, request):
        self.check_token(request.data.get('token'))
        access_token = request.headers.get('Authorization')
        response = requests.get('http://134.122.76.27:8118/api/v1/auth/me/', headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        request.data['author_id'] = user.id
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['author_id'] = user.id
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Get all comment",
        operation_summary="Get all comment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='token'),
            },
            required=['token']
        ),
        responses={
            200: CommentSerializer(many=True)
        },
        tags=['post']
    )
    def get_all(self, request):
        self.check_token(request.GET.get('token'))
        access_token = request.headers.get('Authorization')
        response = requests.get('http://134.122.76.27:8118/api/v1/auth/me/', headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        if comments is None:
            return Response({'error': 'Comments not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'comments': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get comment by id",
        operation_summary="Get comment by id",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH, description='Comment ID', type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter(
                'token', openapi.IN_PATH, description='token', type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            404: 'Not Found',
            200: CommentSerializer()
        },
        tags=['post']
    )
    def get_by_id(self, request, *args, **kwargs):
        self.check_token(request.GET.get('token'))
        access_token = request.headers.get('Authorization')
        response = requests.get('http://134.122.76.27:8118/api/v1/auth/me/', headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        comment = Comment.objects.filter(id=kwargs['id']).first()
        if comment is None:
            return Response(data={'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=CommentSerializer(comment).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete comment by id",
        operation_summary="Delete comment by id",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH, description='Comment ID', type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                'token', openapi.IN_PATH, description='token', type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={
            404: 'Not Found',
            200: 'Successfully Deleted'
        },
        tags=['post']
    )
    def destroy(self, request, *args, **kwargs):
        self.check_token(request.data.get('token'))
        access_token = request.headers.get('Authorization')
        response = requests.get('http://134.122.76.27:8118/api/v1/auth/me/', headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        comment = Comment.objects.filter(id=kwargs['id']).first()
        if comment is None:
            return Response(data={'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        if comment.author_id != response.json()['id']:
            return Response({'error': 'You have not permission to update this comment'},
                            status=status.HTTP_400_BAD_REQUEST)

        comment.delete()

        return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description='Get posts comments',
        operation_summary='Get posts comments',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='token'),
            },
            required=['post_id', 'token']
        ),
        responses={
            404: 'Not Found',
            200: CommentSerializer()
        },
        tags=['post']
    )
    def post_comments(self, request, *args, **kwargs):
        print(request.data.get('token'))
        self.check_token(request.data.get('token'))

        post_id = request.data.get('post_id')
        access_token = request.headers.get('Authorization')
        response = requests.get('http://134.122.76.27:8118/api/v1/auth/me/', headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response({'comments': serializer.data}, status=status.HTTP_200_OK)

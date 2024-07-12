from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from .models import Comment
from .serializers import CommentSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests


class CommentViewSet(ViewSet):

    def get_token(self):
        response = requests.post('http://134.122.76.27:8114/api/v1/login/', json={
            "service_id": 1,
            "service_name": "Comment",
            "secret_key": "abd5a92b-57f4-45f4-95f5-bbde628a2131"
        })
        return response

    def get_post_id(self, pk):
        response = requests.get(f'http://134.122.76.27:8111/api/v1/post/{pk}/', json={
            "token": str(self.get_token().json().get('token')),
        })
        return response

    @swagger_auto_schema(
        operation_description='Create a comment',
        operation_summary='Create a comment',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='post_id'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='message')
            },
            required=['post_id', 'message']
        ),
        responses={
            404: 'Not Found',
            200: CommentSerializer()
        },
        tags=['post']
    )
    def create(self, request):
        access_token = request.headers.get('Authorization')
        response = requests.post('http://134.122.76.27:8118/api/v1/auth/me/',
                                 json={'token': self.get_token().json().get('token')},
                                 headers={'Authorization': access_token})

        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        request.data['author_id'] = response.json()['id']
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['author_id'] = response.json()['id']
            response2 = self.get_post_id(request.data.get('post_id'))
            if response2 is None:
                return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer.save()
            requests.post('http://134.122.76.27:8112/api/v1/notification/',
                          json={"user_id": response.json()['id'], "notification_type": 2,
                                "token": str(self.get_token().json().get('token')),
                                "message": serializer.validated_data['message']})

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Get all comment",
        operation_summary="Get all comment",
        responses={
            200: CommentSerializer(many=True)
        },
        tags=['post']
    )
    def get_all(self, request):
        access_token = request.headers.get('Authorization')
        response = requests.post('http://134.122.76.27:8118/api/v1/auth/me/',
                                 data={'token': self.get_token().json().get('token')},
                                 headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        comments = Comment.objects.filter(author_id=response.json()['id'])
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
        ],
        responses={
            404: 'Not Found',
            200: CommentSerializer()
        },
        tags=['post']
    )
    def get_by_id(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        response = requests.post('http://134.122.76.27:8118/api/v1/auth/me/',
                                 data={'token': self.get_token().json().get('token')},
                                 headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        comment = Comment.objects.filter(id=kwargs['pk']).first()
        if comment is None:
            return Response(data={'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data=CommentSerializer(comment).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Delete comment by id",
        operation_summary="Delete comment by id",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_QUERY, description='Comment ID', type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            404: 'Not Found',
            200: 'Successfully Deleted'
        },
        tags=['post']
    )
    def destroy(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        response = requests.post('http://134.122.76.27:8118/api/v1/auth/me/',
                                 data={'token': self.get_token().json().get('token')},
                                 headers={'Authorization': access_token})
        if response.status_code != 200:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        comment = Comment.objects.filter(id=kwargs['pk']).first()
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
        manual_parameters=[
            openapi.Parameter(
                'post_id', openapi.IN_QUERY, description='POST ID', type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            404: 'Not Found',
            200: CommentSerializer()
        },
        tags=['post']
    )
    def post_comments(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')
        token = request.data.get('token')
        response = requests.post('http://134.122.76.27:8114/api/v1/check/', data={
            "token": token
        })
        if response.status_code != 200:
            return Response(response.json(), response.status_code)

        response2 = self.get_post_id(request.data.get('post_id'))
        if response2 is None:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post_id=int(post_id))
        serializer = CommentSerializer(comments, many=True)
        return Response({'comments': serializer.data}, status=status.HTTP_200_OK)

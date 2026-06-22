from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Category, Skill
from .serializers import CategorySerializer, SkillSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=SkillSerializer(many=True))
def skill_list_view(request):
    skills = Skill.objects.all()
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@extend_schema(responses=CategorySerializer(many=True))
def category_list_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

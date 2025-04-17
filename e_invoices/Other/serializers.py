from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'tax_id']

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # 顯示 username
    company = CompanySerializer()  # 使用內嵌序列化
    viewable_companies = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), many=True  # 允許選擇多個公司
    )

    class Meta:
        model = UserProfile
        fields = ['user', 'company', 'viewable_companies']

from rest_framework import serializers
from .models import User, BorrowHistory, Book

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def create(self, validated_data):
        user = User(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class BookSerializer(serializers.ModelSerializer):
    user = UserLoginSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id','user','name','description','price','is_borrow','from_date','to_date',]

# Borrow History Serializer
class BorrowHistorySerializer(serializers.ModelSerializer):
    user = UserLoginSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = BorrowHistory
        fields = ['id','user','book','borrowed_on','returned_on','status',]
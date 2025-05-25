import json
from django.http import JsonResponse
from .models import User, Book
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from datetime import datetime
from rest_framework import status

def get_refresh_token(user):
    token = RefreshToken.for_user(user)
    
    return {'acsess': str(token.access_token), 'refresh': str(token)}

class UserRegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"error": False,"statusCode": 201, "message": "Registration successful"}, status=status.HTTP_201_CREATED)
        
        return JsonResponse({"error": True,"statusCode": 422,"message": "Validation failed","errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    token = get_refresh_token(user)
                    return JsonResponse({"error": False,"statusCode": 200,"message": "Login successful","data": {"id": user.id,"email": user.email},"token": token}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({"error": True,"statusCode": 401,"message": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return JsonResponse({"error": True,"statusCode": 404,"message": "Email not registered"}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({"error": True,"statusCode": 422,"message": "Validation failed","errors": serializer.errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginView

#For others
class BookListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.filter(is_borrow=False)
    serializer_class = BookSerializer 

class BookToBorrow(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        error = {}
        if not request.data:
            return JsonResponse({'error': True, "statusCode": 422, "message": "Data is required"}, status=422)
        if not request.data.get('name'):
            error['name'] = "This fields is required."
        if not request.data.get('from_date'):
            error['from_date'] = "This fields is required."
        if not request.data.get('to_date'):
            error['to_date'] = "This fields is required."
        try:
            from_date = datetime.strptime(request.data.get('from_date'), "%Y-%m-%d").date()
            to_date = datetime.strptime(request.data.get('to_date'), "%Y-%m-%d").date()
            if from_date > to_date:
                error['date_range'] = "from_date cannot be greater than to_date."
        except ValueError:
            error['date_format'] = "Dates must be in the format YYYY-MM-DD."
        if bool(error):
            return JsonResponse({'error': True, "statusCode": 422, "message": "Something went wrong", 'errors': error}, status=422)
                
        try:
            book = Book.objects.filter(name=request.data.get('name'), is_borrow=False).first()
            if not book:
                return JsonResponse({'error': True, "statusCode": 422, "errors": "Book is already borrowed"}, status=422)
            book.user = request.user
            book.from_date = request.data.get('from_date')
            book.to_date = request.data.get('to_date')
            book.is_borrow=True
            book.save()
            return JsonResponse({"error": False, "statusCode": 200, "message": f"request is submitted wait for accept"})
        except Exception as e:
            return JsonResponse({"error": True, "statusCode": 500, "message": "Something Went Wrong"}, status=500)

# for librarians and others both        
class BookBorrowHistory(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowHistorySerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return BorrowHistory.objects.filter(status="Approved")
        else:
            return BorrowHistory.objects.filter(user=self.request.user, status="Approved")

# for librarians

class BookBorrowRequest(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        if user.is_staff==True:
            return Book.objects.filter(is_borrow=True)
        
    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.request.user.id)
            
            if not user.is_staff:
                return JsonResponse({'error': True, 'statusCode': 403, 'message': 'Unauthorized'}, status=403)
            
            book = Book.objects.get(name=self.request.data.get('name'), is_borrow=True)
            
            history = BorrowHistory.objects.create(user_id=book.user_id, book=book)

            if self.request.data.get("action") == "approve":
                history.status = "Approved"
                book.save()
                history.save()
                return JsonResponse({'error': False, 'statusCode': 200, 'message': 'Request Accepted'}, status=200)
            elif self.request.data.get("action") == "reject":
                history.status = "Rejected"
                book.is_borrow = False
                book.save()
                history.save()
                return JsonResponse({'error': False, 'statusCode': 200, 'message': 'Request Rejected'}, status=200)        
        except Book.DoesNotExist:
            return JsonResponse({'error': True, 'statusCode': 404, 'message': 'Book not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': True, 'statusCode': 500, 'message': f"An error occurred: {str(e)}"}, status=500)

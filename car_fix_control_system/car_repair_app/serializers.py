from .models import Client,Car,Repair, RepairComment,WorkLog,RepairActivityLog, Client,Worker,Manager, RepairImage
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        
        user = User.objects.create_user(username=validated_data['email'],**validated_data)
        return user
    
    def update(self, instance, validated_data):
        
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)  
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

class CarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Car
        fields = '__all__'

class RepairSerializer(serializers.ModelSerializer):

    # nadpisanie metody po to, by klient nie widział pola workers
    def get_fields(self):
        fields = super().get_fields()
        request = self.context['request']
        
        if request.user.groups.first().name != "client":
            return fields

        fields.pop('workers')
        return fields

    class Meta:
        model = Repair
        fields = '__all__'
        read_only_fields = ['end_date','start_date','registration_date']


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = RepairComment
        fields = '__all__'
        read_only_fields = ['creation_date']

class WorkLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkLog
        fields = '__all__'

class RepairActivityLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = RepairActivityLog
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)
    
    class Meta:
        model = Client
        fields = "__all__"

    # tworzenie obiektu poprzez deserializując request
    def create(self, validated_data):

        # deserializacja i stworzenie zagnieżdżonego w ClientSerializer usera:
        user_data = validated_data.pop('user',None)  
        user = UserSerializer.create(UserSerializer(), validated_data=user_data) 
        # stworzenie clienta:
        client = Client.objects.create(user=user, **validated_data)  
        return client
    
    # update obiektu poprzez deserializując request
    def update(self, instance, validated_data):

        user_data = validated_data.pop('user')
        # deserializacja i update obiektu usera, który jest zagnieżdżony w danych klienta:
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data,partial=True)
            if user_serializer.is_valid():
                user_serializer.save()


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    

class WorkerSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)
    
    class Meta:
        model = Worker
        fields = "__all__"

    # tworzenie obiektu deserializując request
    def create(self, validated_data):

        # deserializacja i stworzenie zagnieżdżonego w WorkerSerializer usera:
        user_data = validated_data.pop('user',None)  
        user = UserSerializer.create(UserSerializer(), validated_data=user_data) 
        # stworzenie clienta:
        worker = Worker.objects.create(user=user, **validated_data)  
        return worker
    
    # update obiektu deserializując request
    def update(self, instance, validated_data):

        user_data = validated_data.pop('user')
        # deserializacja i update obiektu usera, który jest zagnieżdżony w danych workera:
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data,partial=True)
            if user_serializer.is_valid():
                user_serializer.save()


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class ManagerSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)
    
    class Meta:
        model = Manager
        fields = "__all__"

    # tworzenie obiektu deserializując request
    def create(self, validated_data):

        # deserializacja i stworzenie zagnieżdżonego w ManagerSerializer usera:
        user_data = validated_data.pop('user',None)  
        user = UserSerializer.create(UserSerializer(), validated_data=user_data) 
        # stworzenie Managera:
        worker = Manager.objects.create(user=user, **validated_data)  
        return worker
    
    # update obiektu deserializując request
    def update(self, instance, validated_data):

        user_data = validated_data.pop('user')
        # deserializacja i update obiektu usera, który jest zagnieżdżony w danych managera:
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data,partial=True)
            if user_serializer.is_valid():
                user_serializer.save()


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        

class RepairImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = RepairImage
        fields = '__all__'
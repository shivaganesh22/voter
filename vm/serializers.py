from rest_framework import serializers
from .models import CSVFile

class CSVFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVFile
        fields = '__all__'
class CollectionSerializer(serializers.Serializer):
    check1=serializers.BooleanField()
    check2=serializers.BooleanField()
    check3=serializers.BooleanField()
    check4=serializers.BooleanField()
    check5=serializers.BooleanField()
    check6=serializers.BooleanField()
class PreprocessingSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    check1=serializers.BooleanField()
    check2=serializers.BooleanField()
    check3=serializers.BooleanField()
    check4=serializers.BooleanField()
    check5=serializers.BooleanField()
class ExplorationSerializer(serializers.Serializer):
    csv=serializers.JSONField()
    check1=serializers.BooleanField()
    check2=serializers.BooleanField()
    check3=serializers.BooleanField()
    check4=serializers.BooleanField()
    check5=serializers.BooleanField()
class DataPreprocessingSerializer(serializers.Serializer):
    csv=serializers.JSONField()
    check1=serializers.BooleanField()
    check2=serializers.BooleanField()
    check3=serializers.BooleanField()
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CSVFile
from .serializers import CSVFileSerializer

class FileUpload(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Extract check1 and check2 from the request data
        check1 = request.data.get('check1')
        check2 = request.data.get('check2')
        check2 = request.data.get('check3')
        check2 = request.data.get('check4')
        check2 = request.data.get('check5')
        check2 = request.data.get('check6')

        # Log or process check1 and check2 as needed

        # Validate and save the CSV file data
        file_serializer = CSVFileSerializer(data=request.data)
        if file_serializer.is_valid():
            csv_file_instance = file_serializer.save()
            # Return the ID of the newly created object
            return Response({'id': csv_file_instance.id,"status":"saved","Check1":check1,"check2":check2})
        else:
            return Response({"status":"not saved","Check1":check1,"check2":check2})

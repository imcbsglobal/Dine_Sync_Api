from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AccUsers, TbItemMaster
from .serializers import AccUsersSerializer, TbItemMasterSerializer
import logging

logger = logging.getLogger(__name__)

class AccUsersAPIView(APIView):
    
    def get(self, request):
        """Get all acc_users records"""
        try:
            users = AccUsers.objects.all()
            serializer = AccUsersSerializer(users, many=True)
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Sync data - Create or Update acc_users records"""
        try:
            data = request.data
            
            # Handle single record
            if isinstance(data, dict):
                data = [data]
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for record in data:
                try:
                    user_id = record.get('id')
                    if not user_id:
                        errors.append({'record': record, 'error': 'ID is required'})
                        continue
                    
                    # Try to get existing user
                    try:
                        user = AccUsers.objects.get(id=user_id)
                        # Update existing user
                        serializer = AccUsersSerializer(user, data=record, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            updated_count += 1
                        else:
                            errors.append({'record': record, 'error': serializer.errors})
                    except AccUsers.DoesNotExist:
                        # Create new user
                        serializer = AccUsersSerializer(data=record)
                        if serializer.is_valid():
                            serializer.save()
                            created_count += 1
                        else:
                            errors.append({'record': record, 'error': serializer.errors})
                            
                except Exception as e:
                    errors.append({'record': record, 'error': str(e)})
            
            response_data = {
                'status': 'success',
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            }
            
            if errors:
                response_data['status'] = 'partial_success'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing data: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class TbItemMasterAPIView(APIView):

    def get(self, request):
        """Get all tb_item_master records"""
        try:
            items = TbItemMaster.objects.all()
            serializer = TbItemMasterSerializer(items, many=True)
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching items: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Sync data - Create or Update tb_item_master records"""
        try:
            data = request.data
            if isinstance(data, dict):
                data = [data]

            created = updated = 0
            errors = []

            for rec in data:
                item_code = rec.get('item_code')
                if not item_code:
                    errors.append({'record': rec, 'error': 'item_code is required'})
                    continue

                try:
                    item = TbItemMaster.objects.get(item_code=item_code)
                    ser = TbItemMasterSerializer(item, data=rec, partial=True)
                    if ser.is_valid():
                        ser.save()
                        updated += 1
                    else:
                        errors.append({'record': rec, 'error': ser.errors})
                except TbItemMaster.DoesNotExist:
                    ser = TbItemMasterSerializer(data=rec)
                    if ser.is_valid():
                        ser.save()
                        created += 1
                    else:
                        errors.append({'record': rec, 'error': ser.errors})

            resp = {'status': 'success', 'created': created, 'updated': updated, 'errors': errors}
            if errors:
                resp['status'] = 'partial_success'
            return Response(resp, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error syncing items: {str(e)}")
            return Response({'status': 'error', 'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        






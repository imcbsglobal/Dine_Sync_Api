from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AccUsers, TbItemMaster
from .serializers import AccUsersSerializer, TbItemMasterSerializer
from .serializers import DineBillSerializer,DineBill,DineKotSalesDetail,DineKotSalesDetailSerializer,DineBillMonthSerializer,DineBillMonth
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
        





# NEW: DineBill API View
class DineBillAPIView(APIView):
    def post(self, request):
        """
        Sync dine_bill data - clear existing and create new records
        """
        try:
            data = request.data
            
            # Clear existing data
            DineBill.objects.all().delete()
            
            # Create new records
            for item in data:
                serializer = DineBillSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(
                        {'error': f'Invalid data: {serializer.errors}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response({
                'message': f'Successfully synced {len(data)} dine_bill records'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """
        Get all dine_bill data
        """
        bills = DineBill.objects.all()
        serializer = DineBillSerializer(bills, many=True)
        return Response(serializer.data)
    
# NEW: DineBillMonth API View (ALL data)
class DineBillMonthAPIView(APIView):
    def post(self, request):
        """
        Sync dine_bill_month data - clear existing and create new records (ALL data)
        """
        try:
            data = request.data
            
            # Clear existing data
            DineBillMonth.objects.all().delete()
            
            # Create new records
            created_count = 0
            errors = []
            
            for item in data:
                serializer = DineBillMonthSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    created_count += 1
                else:
                    errors.append({'record': item, 'error': serializer.errors})
            
            if errors:
                return Response({
                    'status': 'partial_success',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill_month records (ALL data)',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing dine_bill_month: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """
        Get all dine_bill_month data (ALL data)
        """
        try:
            bills = DineBillMonth.objects.all()
            serializer = DineBillMonthSerializer(bills, many=True)
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching dine_bill_month: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DineKotSalesDetailAPIView(APIView):
    def post(self, request):
        """
        Sync dine_kot_sales_detail data - clear existing and create new records
        """
        try:
            data = request.data
            
            # Clear existing data
            DineKotSalesDetail.objects.all().delete()
            
            # Create new records
            created_count = 0
            errors = []
            
            for item in data:
                serializer = DineKotSalesDetailSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    created_count += 1
                else:
                    errors.append({'record': item, 'error': serializer.errors})
            
            if errors:
                return Response({
                    'status': 'partial_success',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} kot_sales_detail records',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing kot sales detail: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """
        Get all dine_kot_sales_detail data
        """
        try:
            kot_details = DineKotSalesDetail.objects.all()
            serializer = DineKotSalesDetailSerializer(kot_details, many=True)
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching kot sales detail: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






# Add this to your views.py file

from .models import CancelledBills
from .serializers import CancelledBillsSerializer

class CancelledBillsAPIView(APIView):
    def post(self, request):
        """
        Sync cancelled_bills data - clear existing and create new records
        """
        try:
            data = request.data
            
            # Clear existing data
            CancelledBills.objects.all().delete()
            
            # Create new records
            created_count = 0
            errors = []
            
            for item in data:
                serializer = CancelledBillsSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    created_count += 1
                else:
                    errors.append({'record': item, 'error': serializer.errors})
            
            if errors:
                return Response({
                    'status': 'partial_success',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} cancelled_bills records',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing cancelled bills: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """
        Get all cancelled_bills data
        """
        try:
            cancelled_bills = CancelledBills.objects.all()
            serializer = CancelledBillsSerializer(cancelled_bills, many=True)
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching cancelled bills: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
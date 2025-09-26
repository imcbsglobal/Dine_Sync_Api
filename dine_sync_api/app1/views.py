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
        """Sync data - CLEAR ALL and CREATE NEW acc_users records"""
        try:
            data = request.data
            
            # Handle single record
            if isinstance(data, dict):
                data = [data]
            
            # CLEAR ALL EXISTING DATA FIRST
            AccUsers.objects.all().delete()
            logger.info("Cleared all existing acc_users records")
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            for record in data:
                try:
                    user_id = record.get('id')
                    if not user_id:
                        errors.append({'record': record, 'error': 'ID is required'})
                        continue
                    
                    # Create new user (no update logic needed since we cleared all)
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
                'message': f'Successfully synced {created_count} acc_users records (cleared all old data)',
                'created': created_count,
                'errors': errors
            }
            
            if errors:
                response_data['status'] = 'partial_success'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing acc_users data: {str(e)}")
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
        """Sync data - CLEAR ALL and CREATE NEW tb_item_master records"""
        try:
            data = request.data
            if isinstance(data, dict):
                data = [data]

            # CLEAR ALL EXISTING DATA FIRST
            TbItemMaster.objects.all().delete()
            logger.info("Cleared all existing tb_item_master records")

            created_count = 0
            errors = []

            # CREATE ALL NEW RECORDS
            for rec in data:
                item_code = rec.get('item_code')
                if not item_code:
                    errors.append({'record': rec, 'error': 'item_code is required'})
                    continue

                try:
                    # Create new item (no update logic needed since we cleared all)
                    ser = TbItemMasterSerializer(data=rec)
                    if ser.is_valid():
                        ser.save()
                        created_count += 1
                    else:
                        errors.append({'record': rec, 'error': ser.errors})
                except Exception as e:
                    errors.append({'record': rec, 'error': str(e)})

            response_data = {
                'status': 'success',
                'message': f'Successfully synced {created_count} tb_item_master records (cleared all old data)',
                'created': created_count,
                'errors': errors
            }
            
            if errors:
                response_data['status'] = 'partial_success'
                
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error syncing tb_item_master: {str(e)}")
            return Response({'status': 'error', 'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DineBill API View (already correctly implemented - clear and replace)
class DineBillAPIView(APIView):
    def post(self, request):
        """
        Sync dine_bill data - CLEAR ALL and CREATE NEW records
        """
        try:
            data = request.data
            
            # CLEAR ALL EXISTING DATA FIRST
            DineBill.objects.all().delete()
            logger.info("Cleared all existing dine_bill records")
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            for item in data:
                serializer = DineBillSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    created_count += 1
                else:
                    errors.append({'record': item, 'error': serializer.errors})
            
            if errors:
                return Response({
                    'status': 'partial_success',
                    'message': f'Synced {created_count} dine_bill records with some errors (cleared all old data)',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill records (cleared all old data)',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing dine_bill: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all dine_bill data"""
        try:
            bills = DineBill.objects.all()
            serializer = DineBillSerializer(bills, many=True)
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching dine_bill: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# DineBillMonth API View (already correctly implemented - clear and replace)
class DineBillMonthAPIView(APIView):
    def post(self, request):
        """
        Sync dine_bill_month data - CLEAR ALL and CREATE NEW records (ALL data)
        """
        try:
            data = request.data
            
            # CLEAR ALL EXISTING DATA FIRST
            DineBillMonth.objects.all().delete()
            logger.info("Cleared all existing dine_bill_month records")
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
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
                    'message': f'Synced {created_count} dine_bill_month records with some errors (cleared all old data)',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill_month records (cleared all old data)',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing dine_bill_month: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all dine_bill_month data"""
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
        Sync dine_kot_sales_detail data - CLEAR ALL and CREATE NEW records
        """
        try:
            data = request.data
            
            # CLEAR ALL EXISTING DATA FIRST
            DineKotSalesDetail.objects.all().delete()
            logger.info("Cleared all existing dine_kot_sales_detail records")
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
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
                    'message': f'Synced {created_count} kot_sales_detail records with some errors (cleared all old data)',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} kot_sales_detail records (cleared all old data)',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing kot sales detail: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all dine_kot_sales_detail data"""
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


from .models import CancelledBills
from .serializers import CancelledBillsSerializer

class CancelledBillsAPIView(APIView):
    def post(self, request):
        """
        Sync cancelled_bills data - CLEAR ALL and CREATE NEW records
        """
        try:
            data = request.data
            
            # CLEAR ALL EXISTING DATA FIRST
            CancelledBills.objects.all().delete()
            logger.info("Cleared all existing cancelled_bills records")
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
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
                    'message': f'Synced {created_count} cancelled_bills records with some errors (cleared all old data)',
                    'created': created_count,
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} cancelled_bills records (cleared all old data)',
                'created': created_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing cancelled bills: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all cancelled_bills data"""
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
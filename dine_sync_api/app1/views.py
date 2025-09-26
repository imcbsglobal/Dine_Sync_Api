from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection, transaction
from .models import AccUsers, TbItemMaster, DineBill, DineBillMonth, DineKotSalesDetail, CancelledBills
from .serializers import (
    AccUsersSerializer, TbItemMasterSerializer, DineBillSerializer,
    DineBillMonthSerializer, DineKotSalesDetailSerializer, CancelledBillsSerializer
)
import logging

logger = logging.getLogger(__name__)

def truncate_table(table_name):
    """
    Safely truncate a specific table using raw SQL
    """
    try:
        with connection.cursor() as cursor:
            # Disable foreign key checks temporarily
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # Truncate the table (this resets auto-increment and is faster than DELETE)
            cursor.execute(f"TRUNCATE TABLE `{table_name}`;")
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            
        logger.info(f"Successfully truncated table: {table_name}")
        return True
    except Exception as e:
        logger.error(f"Error truncating table {table_name}: {str(e)}")
        return False

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
        """Sync data - TRUNCATE and CREATE NEW acc_users records"""
        try:
            data = request.data
            
            # Handle single record
            if isinstance(data, dict):
                data = [data]
            
            # TRUNCATE TABLE FIRST
            if not truncate_table('acc_users'):
                return Response({
                    'status': 'error',
                    'message': 'Failed to truncate acc_users table'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            with transaction.atomic():
                for record in data:
                    try:
                        user_id = record.get('id')
                        if not user_id:
                            errors.append({'record': record, 'error': 'ID is required'})
                            continue
                        
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
                'message': f'Successfully synced {created_count} acc_users records (TRUNCATED table first)',
                'created': created_count,
                'total_received': len(data),
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
        """Sync data - TRUNCATE and CREATE NEW tb_item_master records"""
        try:
            data = request.data
            if isinstance(data, dict):
                data = [data]

            # TRUNCATE TABLE FIRST
            if not truncate_table('tb_item_master'):
                return Response({
                    'status': 'error',
                    'message': 'Failed to truncate tb_item_master table'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            created_count = 0
            errors = []

            # CREATE ALL NEW RECORDS
            with transaction.atomic():
                for rec in data:
                    item_code = rec.get('item_code')
                    if not item_code:
                        errors.append({'record': rec, 'error': 'item_code is required'})
                        continue

                    try:
                        # Create new item
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
                'message': f'Successfully synced {created_count} tb_item_master records (TRUNCATED table first)',
                'created': created_count,
                'total_received': len(data),
                'errors': errors
            }
            
            if errors:
                response_data['status'] = 'partial_success'
                
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error syncing tb_item_master: {str(e)}")
            return Response({
                'status': 'error', 
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DineBillAPIView(APIView):
    def post(self, request):
        """
        Sync dine_bill data - TRUNCATE and CREATE NEW records
        """
        try:
            data = request.data
            
            # TRUNCATE TABLE FIRST
            if not truncate_table('dine_bill'):
                return Response({
                    'status': 'error',
                    'message': 'Failed to truncate dine_bill table'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            with transaction.atomic():
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
                    'message': f'Synced {created_count} dine_bill records with some errors (TRUNCATED table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill records (TRUNCATED table first)',
                'created': created_count,
                'total_received': len(data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing dine_bill: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    

class DineBillMonthAPIView(APIView):
    def post(self, request):
        """
        Sync dine_bill_month data - TRUNCATE and CREATE NEW records (ALL data)
        """
        try:
            data = request.data
            
            # TRUNCATE TABLE FIRST
            if not truncate_table('dine_bill_month'):
                return Response({
                    'status': 'error',
                    'message': 'Failed to truncate dine_bill_month table'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            with transaction.atomic():
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
                    'message': f'Synced {created_count} dine_bill_month records with some errors (TRUNCATED table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill_month records (TRUNCATED table first)',
                'created': created_count,
                'total_received': len(data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing dine_bill_month: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        Sync dine_kot_sales_detail data - TRUNCATE and CREATE NEW records
        """
        try:
            data = request.data
            
            # TRUNCATE TABLE FIRST
            if not truncate_table('dine_kot_sales_detail'):
                return Response({
                    'status': 'error',
                    'message': 'Failed to truncate dine_kot_sales_detail table'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            with transaction.atomic():
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
                    'message': f'Synced {created_count} kot_sales_detail records with some errors (TRUNCATED table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} kot_sales_detail records (TRUNCATED table first)',
                'created': created_count,
                'total_received': len(data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing kot sales detail: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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


class CancelledBillsAPIView(APIView):
    def post(self, request):
        """
        Sync cancelled_bills data - TRUNCATE and CREATE NEW records
        """
        try:
            data = request.data
            
            # TRUNCATE TABLE FIRST
            if not truncate_table('cancelled_bills'):
                return Response({
                    'status': 'error',
                    'message': 'Failed to truncate cancelled_bills table'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_count = 0
            errors = []
            
            # CREATE ALL NEW RECORDS
            with transaction.atomic():
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
                    'message': f'Synced {created_count} cancelled_bills records with some errors (TRUNCATED table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} cancelled_bills records (TRUNCATED table first)',
                'created': created_count,
                'total_received': len(data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error syncing cancelled bills: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
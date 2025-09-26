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
    Safely truncate a specific table - tries multiple approaches for different databases
    """
    try:
        with connection.cursor() as cursor:
            # Method 1: Try simple TRUNCATE first (works for most databases)
            try:
                cursor.execute(f"TRUNCATE TABLE [{table_name}]")
                logger.info(f"Successfully truncated table: {table_name}")
                return True
            except Exception as e1:
                logger.warning(f"TRUNCATE failed for {table_name}: {str(e1)}, trying DELETE...")
                
                # Method 2: Use DELETE as fallback
                try:
                    cursor.execute(f"DELETE FROM [{table_name}]")
                    logger.info(f"Successfully deleted all records from table: {table_name}")
                    
                    # Try to reset identity/auto-increment (SQL Server)
                    try:
                        cursor.execute(f"DBCC CHECKIDENT('{table_name}', RESEED, 0)")
                        logger.info(f"Reset identity for table: {table_name}")
                    except:
                        pass  # Identity reset not critical
                    
                    return True
                except Exception as e2:
                    logger.error(f"DELETE also failed for {table_name}: {str(e2)}")
                    return False
                    
    except Exception as e:
        logger.error(f"General error truncating table {table_name}: {str(e)}")
        return False


def clear_table_orm(model_class):
    """
    Alternative: Use Django ORM to delete all records (safer but slower)
    """
    try:
        count = model_class.objects.all().delete()[0]
        logger.info(f"Deleted {count} records from {model_class._meta.db_table} using ORM")
        return True
    except Exception as e:
        logger.error(f"Error deleting from {model_class._meta.db_table}: {str(e)}")
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
        """Sync data - CLEAR and CREATE NEW acc_users records"""
        try:
            data = request.data
            
            # Handle single record
            if isinstance(data, dict):
                data = [data]
            
            # Method 1: Try SQL TRUNCATE first
            truncate_success = truncate_table('acc_users')
            
            # Method 2: If TRUNCATE fails, use Django ORM to clear table
            if not truncate_success:
                logger.warning("TRUNCATE failed, using Django ORM to clear acc_users table")
                if not clear_table_orm(AccUsers):
                    return Response({
                        'status': 'error',
                        'message': 'Failed to clear acc_users table'
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
                'message': f'Successfully synced {created_count} acc_users records (cleared table first)',
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
        """Sync data - CLEAR and CREATE NEW tb_item_master records"""
        try:
            data = request.data
            if isinstance(data, dict):
                data = [data]

            # Method 1: Try SQL TRUNCATE first
            truncate_success = truncate_table('tb_item_master')
            
            # Method 2: If TRUNCATE fails, use Django ORM to clear table
            if not truncate_success:
                logger.warning("TRUNCATE failed, using Django ORM to clear tb_item_master table")
                if not clear_table_orm(TbItemMaster):
                    return Response({
                        'status': 'error',
                        'message': 'Failed to clear tb_item_master table'
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
                'message': f'Successfully synced {created_count} tb_item_master records (cleared table first)',
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
        Sync dine_bill data - CLEAR and CREATE NEW records
        """
        try:
            data = request.data
            
            # Method 1: Try SQL TRUNCATE first
            truncate_success = truncate_table('dine_bill')
            
            # Method 2: If TRUNCATE fails, use Django ORM to clear table
            if not truncate_success:
                logger.warning("TRUNCATE failed, using Django ORM to clear dine_bill table")
                if not clear_table_orm(DineBill):
                    return Response({
                        'status': 'error',
                        'message': 'Failed to clear dine_bill table'
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
                    'message': f'Synced {created_count} dine_bill records with some errors (cleared table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill records (cleared table first)',
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
        Sync dine_bill_month data - CLEAR and CREATE NEW records (ALL data)
        """
        try:
            data = request.data
            
            # Method 1: Try SQL TRUNCATE first
            truncate_success = truncate_table('dine_bill_month')
            
            # Method 2: If TRUNCATE fails, use Django ORM to clear table
            if not truncate_success:
                logger.warning("TRUNCATE failed, using Django ORM to clear dine_bill_month table")
                if not clear_table_orm(DineBillMonth):
                    return Response({
                        'status': 'error',
                        'message': 'Failed to clear dine_bill_month table'
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
                    'message': f'Synced {created_count} dine_bill_month records with some errors (cleared table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} dine_bill_month records (cleared table first)',
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
        Sync dine_kot_sales_detail data - CLEAR and CREATE NEW records
        """
        try:
            data = request.data
            
            # Method 1: Try SQL TRUNCATE first
            truncate_success = truncate_table('dine_kot_sales_detail')
            
            # Method 2: If TRUNCATE fails, use Django ORM to clear table
            if not truncate_success:
                logger.warning("TRUNCATE failed, using Django ORM to clear dine_kot_sales_detail table")
                if not clear_table_orm(DineKotSalesDetail):
                    return Response({
                        'status': 'error',
                        'message': 'Failed to clear dine_kot_sales_detail table'
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
                    'message': f'Synced {created_count} kot_sales_detail records with some errors (cleared table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} kot_sales_detail records (cleared table first)',
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
        Sync cancelled_bills data - CLEAR and CREATE NEW records
        """
        try:
            data = request.data
            
            # Method 1: Try SQL TRUNCATE first
            truncate_success = truncate_table('cancelled_bills')
            
            # Method 2: If TRUNCATE fails, use Django ORM to clear table
            if not truncate_success:
                logger.warning("TRUNCATE failed, using Django ORM to clear cancelled_bills table")
                if not clear_table_orm(CancelledBills):
                    return Response({
                        'status': 'error',
                        'message': 'Failed to clear cancelled_bills table'
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
                    'message': f'Synced {created_count} cancelled_bills records with some errors (cleared table first)',
                    'created': created_count,
                    'total_received': len(data),
                    'errors': errors
                }, status=status.HTTP_200_OK)
            
            return Response({
                'status': 'success',
                'message': f'Successfully synced {created_count} cancelled_bills records (cleared table first)',
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
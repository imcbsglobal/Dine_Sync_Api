
from django.db import models

class AccUsers(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    pass_field = models.CharField(max_length=100, db_column='pass')  # 'pass' is a reserved word in Python
    
    class Meta:
        db_table = 'acc_users'
        
    def __str__(self):
        return self.id


class TbItemMaster(models.Model):
    id = models.AutoField(primary_key=True)               # new PK
    item_code = models.CharField(max_length=15, unique=True)
    item_name = models.CharField(max_length=60, blank=True, null=True)
    rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate1 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate2 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate3 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate4 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate5 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate6 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    rate7 = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    kitchen = models.CharField(max_length=30, blank=True, null=True)
    category = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'tb_item_master'

    def __str__(self):
        return self.item_code        








class DineBill(models.Model):
    billno = models.DecimalField(max_digits=10, decimal_places=0, primary_key=True)
    time_field = models.DateTimeField(blank=True, null=True, db_column='time')  # 'time' is reserved
    user_field = models.CharField(max_length=15, blank=True, null=True, db_column='user')  # 'user' is reserved
    amount = models.DecimalField(max_digits=13, decimal_places=5, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True, db_column='date')  # 'date' is reserved - ADDED

    class Meta:
        db_table = 'dine_bill'
        
    def __str__(self):
        return str(self.billno)
    
class DineBillMonth(models.Model):
    billno = models.DecimalField(max_digits=10, decimal_places=0, primary_key=True)
    time_field = models.DateTimeField(blank=True, null=True, db_column='time')  # 'time' is reserved
    user_field = models.CharField(max_length=15, blank=True, null=True, db_column='user')  # 'user' is reserved
    amount = models.DecimalField(max_digits=13, decimal_places=5, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True, db_column='date')  # 'date' is reserved

    class Meta:
        db_table = 'dine_bill_month'
        
    def __str__(self):
        return f"Monthly Bill {self.billno}"




class DineKotSalesDetail(models.Model):
    slno = models.DecimalField(max_digits=10, decimal_places=0, primary_key=True)
    billno = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    item = models.CharField(max_length=15, blank=True, null=True)
    qty = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    rate = models.DecimalField(max_digits=14, decimal_places=5, blank=True, null=True)

    class Meta:
        db_table = 'dine_kot_sales_detail'
        
    def __str__(self):
        return f"KOT {self.slno} - Bill {self.billno}"
    




# takes from dine_bill db

class CancelledBills(models.Model): 
    billno = models.DecimalField(max_digits=10, decimal_places=0, primary_key=True)
    date_field = models.DateField(blank=True, null=True, db_column='date')  # 'date' is reserved
    creditcard = models.CharField(max_length=30, blank=True, null=True)
    colnstatus = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        db_table = 'cancelled_bills'
        
    def __str__(self):
        return f"Cancelled Bill {self.billno}"
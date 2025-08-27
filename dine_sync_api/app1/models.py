
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
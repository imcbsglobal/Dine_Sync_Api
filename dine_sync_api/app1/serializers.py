from rest_framework import serializers
from .models import AccUsers, TbItemMaster, DineBill

class AccUsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(source='pass_field', max_length=100)
    
    class Meta:
        model = AccUsers
        fields = ['id', 'password']
        
    def create(self, validated_data):
        return AccUsers.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.pass_field = validated_data.get('pass_field', instance.pass_field)
        instance.save()
        return instance
    

class TbItemMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TbItemMaster
        fields = [
            'id', 'item_code', 'item_name', 'rate', 'rate1', 'rate2',
            'rate3', 'rate4', 'rate5', 'rate6', 'rate7', 'kitchen', 'category'
        ]


# NEW: DineBill serializer
class DineBillSerializer(serializers.ModelSerializer):
    billno = serializers.DecimalField(max_digits=10, decimal_places=0)
    time = serializers.DateTimeField(source='time_field', required=False, allow_null=True)
    user = serializers.CharField(source='user_field', max_length=15, required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = DineBill
        fields = ['billno', 'time', 'user', 'amount']
        
    def validate_billno(self, value):
        """Ensure billno is properly converted to decimal"""
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            raise serializers.ValidationError("Invalid billno format")
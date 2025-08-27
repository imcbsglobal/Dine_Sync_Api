from rest_framework import serializers
from .models import AccUsers, TbItemMaster

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
    

# NEW: Serializer for TbItemMaster
class TbItemMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TbItemMaster
        fields = [
            'id', 'item_code', 'item_name', 'rate', 'rate1', 'rate2',
            'rate3', 'rate4', 'rate5', 'rate6', 'rate7', 'kitchen', 'category'
        ]

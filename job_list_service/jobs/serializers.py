from rest_framework import serializers
from .models import JobApplication


from rest_framework import serializers
from .models import JobApplication

class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'id',            
            'candidate_id',
            'company_name',
            'job_title',
            'platform',
            'salary_range',
            'status',
            'applied_date',
            'notes',
            'job_url',
            'location',
            'is_active',
            'created_at',
            'updated_at',
            'priority',
        ]

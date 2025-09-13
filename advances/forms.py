from django import forms
from .models import AdvanceRequest, AdvanceType

class AdvanceRequestForm(forms.ModelForm):
    class Meta:
        model = AdvanceRequest
        fields = ['advance_type', 'amount', 'notes']

    def __init__(self, *args, **kwargs):
        available_types = kwargs.pop('available_types', None)
        super().__init__(*args, **kwargs)
        if available_types:
            self.fields['advance_type'].choices = [(t, dict(AdvanceType.choices)[t]) for t in available_types]

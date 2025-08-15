from django import forms
from .models import Review
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class ReviewForm(forms.ModelForm):
    """
    Form for users to submit reviews. Used in ProductDetailView if user has purchased.
    Crispy forms for Tailwind styling.
    Validation: Rating 1-5, comment optional.
    """
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit Review', css_class='btn btn-primary'))

from django import forms

from .models import Review


class VisitorReviewForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "review-input",
            "placeholder": "Enter your name",
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "review-input",
            "placeholder": "Enter your email address",
        })
    )

    rating = forms.TypedChoiceField(
        choices=Review._meta.get_field("rating").choices,
        coerce=int,
        empty_value=None,
        widget=forms.RadioSelect,
        error_messages={
            "required": "Please select a star rating."
        }
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "review-input",
            "placeholder": "Share your experience (optional)",
            "rows": 4,
        })
    )

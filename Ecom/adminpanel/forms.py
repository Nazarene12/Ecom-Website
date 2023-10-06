from django import forms
from .models import Product, Color, Brand, Category ,Size

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'name', 'required': 'required'}),

        }


class ProductForm(forms.ModelForm):
    color = forms.ModelChoiceField(
        queryset=Color.objects.all(),
        required=False,
        empty_label="Select a color"
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label="Select a brand"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select a category"
    )

    # Add a new field for selecting multiple sizes
    size = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,  # Use checkboxes for multiple selection
    )

    normal_image = forms.ImageField(required=False)
    front_image = forms.ImageField(required=False)
    back_image = forms.ImageField(required=False)
    side_image = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

from typing import Any
from django import forms
from .models import Product, Color, Brand, Category ,Size,Connector
from .mixins import get_count
from django.core.exceptions import ValidationError


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'name', 'required': 'required'}),

        }
class SizeCountFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        if all(not any(form.cleaned_data.values()) for form in self.forms):
            raise ValidationError('At least one size should be added.')
        sizes = []
        for form in self.forms:
            size = form.cleaned_data.get('size')
            
            if size and size in sizes:
                raise ValidationError('you have entered the same sizes which not allowed.')
            sizes.append(size)

class VarientCountColorFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        if all(not any(form.cleaned_data.values()) for form in self.forms):
            raise ValidationError('At least one form in the formset must be filled out.')
        colors = []
        for form in self.forms:
            color = form.cleaned_data.get('color')
            if color and color in colors:
                raise ValidationError('you have entered the same colors which is not allowed.')
            colors.append(color)

class SizeCountForm(forms.Form):
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-select form-control'}
        ),
        help_text="required *",
        empty_label="select a size"
    )
    
    count = forms.IntegerField(
        min_value=0,
        initial=0,
        label='Count' ,
        help_text="required *",
        widget=forms.NumberInput(
            attrs={'class': 'form-control customclass','placeholder':'number'}
        ),
        
    )

    def clean(self):
        cleaned_data = super().clean()
        count = cleaned_data.get('count')
        if count and  count <= 0:
            self.add_error('count', 'it can not bee zero or negative number')
        return cleaned_data
    
def SizeCountFormSetFactory(instance = None ,prefix=0):
    size_count = Size.objects.count()  # Count the number of sizes in the database
    size_count_factory = forms.formset_factory(SizeCountForm,formset=SizeCountFormSet, extra=size_count)
    if instance:
        return size_count_factory(instance, prefix=f'varientsize{prefix}')

    return size_count_factory( prefix=f'varientsize{prefix}')


def VarientCountFormSetFactory(instance , files , extra = 1):
    varient_count_factory= forms.formset_factory(VarientForm,formset=VarientCountColorFormSet,extra=extra)
    if instance:
        return varient_count_factory(instance ,files, prefix='varient' )
    return varient_count_factory( prefix='varient' )


class ProductForm(forms.ModelForm):
    color = forms.ModelChoiceField(
        queryset=Color.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-select form-control'}
        ),
        required=True, 
        help_text="required *",
        empty_label="Select a color"
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-select form-control'}
        ),
        required=True, 
        help_text="required *",
        empty_label="Select a brand"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-select form-control'}
        ),
        required=True, 
        help_text="required *",
        empty_label="Select a category"
    )


    normal_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': 'required'})
    )
    front_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': 'required'})
    )
    back_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': 'required'})
    )
    side_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': 'required'})
    )

    # size_count_formset = SizeCountFormSetFactory()

    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'name', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control customclass','placeholder':'discription' , 'required': 'required'}),
            'price' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'number' , 'required': 'required' }),

        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Product.objects.filter(name=name).exists():
            print("hello")
            raise forms.ValidationError('this product name is already available')

        return name


class UpdateProductVarient(forms.ModelForm):


    class Meta:
        model = Connector
        fields = ['product','color' , 'size' , 'count' , 'first_preference' ]

        widgets = {
            'product':forms.HiddenInput(),
            'count' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'number' , 'required': 'required' }),
            'color': forms.Select(attrs={'class': 'form-select form-control', 'required': 'required'}),
            'size': forms.Select(attrs={'class': 'form-select form-control', 'required': 'required'}),
        }

    def clean(self):
        
        cleaned_data = super().clean()
        count = cleaned_data.get('count')
        if not count or  count <= 0:
            self.add_error('count', 'it can not bee zero or negative number or empty')

        instance_product = self.instance

        if instance_product.color != cleaned_data['color'] and instance_product.size == cleaned_data['size']:

            if Connector.objects.filter(product = instance_product.product , size = instance_product.size , color = cleaned_data['color']).exists():
                self.add_error(None , 'there is already a varient like this , changed(color)')
        elif instance_product.color == cleaned_data['color'] and instance_product.size != cleaned_data['size']:

            if Connector.objects.filter(product = instance_product.product , size = cleaned_data['size'] , color = instance_product.color).exists():
                self.add_error(None , 'there is already a varient like this , changed(size)')

        elif instance_product.color != cleaned_data['color'] and instance_product.size != cleaned_data['size']:

            if Connector.objects.filter(product = instance_product.product , size = cleaned_data['size'] , color = cleaned_data['color']).exists():
                self.add_error(None , 'there is already a varient like this , changed(color , size)')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.first_preference:
            previous_variant = Connector.objects.filter(product=instance.product, first_preference=True).exclude(id=instance.id).first()
            if previous_variant:
                previous_variant.first_preference = False
                previous_variant.save()
        if commit:
            instance.save()
        return instance
    



class VarientForm(forms.Form):
    
    color = forms.ModelChoiceField(
        queryset=Color.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-select form-control', 'required': True}
        ),
        required=True, 
        help_text="required *",
        empty_label="Select a color",
        
    )
    normal_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )
    front_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )
    back_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )
    side_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )

    size_count_formset = None

class UpdatedProductAddForm(forms.ModelForm):

    
    class Meta:
        model = Product
        fields = ['name', 'description', 'price' , 'brand' , 'category']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'name', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control customclass','placeholder':'discription' , 'required': 'required'}),
            'price' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'number' , 'required': 'required' }),
            'brand': forms.Select(attrs={'class': 'form-select form-control', 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-select form-control', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super(UpdatedProductAddForm, self).__init__(*args, **kwargs)
        
        # Set custom placeholder text for brand and category fields
        self.fields['brand'].empty_label = 'Select a Brand'
        self.fields['category'].empty_label = 'Select a Category'

class  AddAditionVarientColorForm(forms.ModelForm):

    normal_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )
    front_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )
    back_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )
    side_image = forms.ImageField(
        required=True ,
        help_text="required *",
        widget=forms.FileInput(attrs={'required': True})
    )

    size_count_formset = None

    class Meta:
        model = Connector
        fields = ['color' ,'product']

        widgets = {
            'color': forms.Select(attrs={'class': 'form-select form-control', 'required': 'required'}),
            'product':forms.HiddenInput(),
        }

    def clean(self):
        clean_data = super().clean()

        color = clean_data['color']
        product = clean_data['product']

        if Connector.objects.filter(product=product,color=color).exists():
            self.add_error('color' , 'there is already a varient for this product in this color ')
        
        return clean_data

    

    

class AddAditionVarientForm(forms.ModelForm):

    connector = forms.CharField(
        widget=forms.HiddenInput(
            attrs={'id':'add_similar_varient'}
        ),
        required=True, 
        label=''
     
    )

    class Meta:
        model = Connector
        fields = ['size' , 'count' ]

        widgets = {
            'count' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'number' , 'required': 'required' }),
            'size': forms.Select(attrs={'class': 'form-select form-control', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super(AddAditionVarientForm, self).__init__(*args, **kwargs)
        
        # Set custom placeholder text for brand and category fields
        self.fields['size'].empty_label = 'Select a size'


    def clean(self):

        clean_data = super().clean()

        varient = Connector.objects.get(id = clean_data['connector'])

        if not clean_data['count'] or clean_data['count'] <= 0 :

            self.add_error('count',"count can not be zero or negative")

        if Connector.objects.filter(product=varient.product , color = varient.color , size = clean_data['size']).exists():
            self.add_error('size' , 'there is already a varient with this color size')

    def save(self, commit=True):
        instance = super().save(commit=False)
        clean_data = self.cleaned_data
        varient = Connector.objects.get(id = clean_data['connector'])
        instance.product = varient.product
        instance.image = varient.image
        instance.color = varient.color
        if commit:
            instance.save()
        return instance
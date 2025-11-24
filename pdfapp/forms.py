from django import forms

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(label='Upload PDF for Watermark')

class WatermarkForm(forms.Form):
    WATERMARK_CHOICES = [
        ('Bhudevnetworkvivah.com', 'Bhudevnetworkvivah.com'),
        ('NRI', 'NRI'),
        ('Divorce', 'Divorce'),
        ('Saurashtra', 'Saurashtra'),
        ('Doctor', 'Doctor'),
        ('Masters', 'Masters'),
        ('CACS', 'CACS'),
        ('Maharashtra', 'Maharashtra'),
        ('GovJob', 'GovJob'),
        ('40plus', '40plus'),
        ('1012', '1012'),
        ('SG', 'SG'),
        ('NG', 'NG'),
        ('Canada', 'Canada'),
        ('USA', 'USA'),
        ('Aus-NZ', 'Aus-NZ'),
        ('Europe', 'Europe'),
        ('Mumbai', 'Mumbai'),
        ('Amdavad', 'Amdavad'),
        ('Vadodara', 'Vadodara'),
        ('Surat', 'Surat'),
        ('Rajkot', 'Rajkot'),
        ('Pune', 'Pune'),
        ('Gandhinagar', 'Gandhinagar'),
        ('Anand', 'Anand'),
        ('Mangalfera', 'Mangalfera'),
        ('jamnagar', 'jamnagar'),
        ('bhavnagar', 'bhavnagar'),
    ]
    watermark = forms.ChoiceField(choices=WATERMARK_CHOICES, label='Select Watermark')

class MergePDFForm(forms.Form):
    pdf_file_2 = forms.FileField(label='Upload PDF to Merge')

class CustomFileNameForm(forms.Form):
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Enter City Name"}),
    )
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Enter Name & Surname"}),
    )
    date = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "dd-mm-yyyy"}),
    )
    education = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Enter Education"}),
    )
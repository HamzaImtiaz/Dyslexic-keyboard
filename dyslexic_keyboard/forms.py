from django import forms
 
# creating a form
class NameForm(forms.Form):
    your_name = forms.CharField( label='',max_length=100)

    
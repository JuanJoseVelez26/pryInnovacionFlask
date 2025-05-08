from django import forms

class RegisterForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)
    nombre = forms.CharField(max_length=100)
    fecha_nacimiento = forms.DateField(widget=forms.SelectDateWidget())
    direccion = forms.CharField(max_length=255)
    descripcion = forms.CharField(widget=forms.Textarea)
    area_expertise = forms.CharField(max_length=100, required=False, label="Área de expertise")
    informacion_adicional = forms.CharField(widget=forms.Textarea, required=False, label="Información adicional")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Validación de contraseñas
        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
    



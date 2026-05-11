"""Formularios del modulo mesas."""

from django import forms

from bongusto.modules.mesas.models import Mesa


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ["numero_mesa", "nombre", "capacidad", "activa"]

    def clean_numero_mesa(self):
        numero = self.cleaned_data.get("numero_mesa")
        if numero is None or int(numero) <= 0:
            raise forms.ValidationError("El numero de mesa debe ser mayor a cero.")
        return numero

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get("capacidad")
        if capacidad is None or int(capacidad) <= 0:
            raise forms.ValidationError("La capacidad debe ser mayor a cero.")
        return capacidad


__all__ = ["MesaForm"]

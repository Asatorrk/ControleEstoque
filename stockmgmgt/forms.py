from django import forms
from .models import Stock

class StockCreateForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['category', 'item_name', 'quantity','expiration_date',]
		labels = {
            'category': 'Categoria',  # Alterando o rótulo do campo 'category' para 'Categoria'
            'item_name': 'Nome do item',
            'quantity': 'Quantidade',
            'expiration_date': 'Data de Validade',
        }

def clean_expiration_date(self):
        expiration_date = self.cleaned_data.get('expiration_date')
        # Aqui você pode adicionar validações personalizadas, se necessário
        return expiration_date


def clean_category(self):
		category = self.cleaned_data.get('category')
		if not category:
			raise forms.ValidationError('Este campo é obrigatório')
		return category

		
def clean_item_name(self):
		item_name = self.cleaned_data.get('item_name')
		if not item_name:
			raise forms.ValidationError('Este campo é obrigatório')
		return item_name	


class StockSearchForm(forms.ModelForm):
	Exportar_para_EXCEL = forms.BooleanField(required=False)
	class Meta:
		model = Stock
		fields = ['item_name']
		labels = {'item_name': 'Pesquisar',
        }


class StockUpdateForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['category','item_name','quantity']
		labels = {
            'category': 'Categoria',  # Alterando o rótulo do campo 'category' para 'Categoria'
            'item_name': 'Nome do item',
            'quantity': 'Quantidade',
        }

class IssueForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['issue_quantity']
		labels = {
            'issue_quantity': 'Retirar quantia'     
        }

class ReceiveForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['receive_quantity']
		labels = {
            'receive_quantity': 'Adicionar quantidade',
        }

class ReorderLevelForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['reorder_level']
		labels = {
            'reorder_level': 'Reordenar quantidade mínima',
        }

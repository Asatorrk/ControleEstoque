from django import forms
from .models import Stock

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['category', 'item_name', 'quantity', 'expiration_date', 'barcode']
        labels = {
            'category': 'Categoria',
            'item_name': 'Nome do item',
            'quantity': 'Quantidade',
            'expiration_date': 'Data de Validade',
            'barcode': 'Código de Barras',
        }

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        if Stock.objects.filter(barcode=barcode).exists():
            raise forms.ValidationError('Um item com este código de barras já existe.')  # Mensagem de erro personalizada
        return barcode

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
		fields = ['category','item_name','quantity','barcode']
		labels = {
            'category': 'Categoria',  # Alterando o rótulo do campo 'category' para 'Categoria'
            'item_name': 'Nome do item',
            'quantity': 'Quantidade',
            'barcode': 'Código de Barras',
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

class BarcodeForm(forms.Form):
    barcode = forms.CharField(max_length=50, required=True, label='Código de Barras')


class StockSearchForm(forms.Form):
    # Campo para pesquisa de itens
    search = forms.CharField(max_length=50, required=False, label="Pesquisar")


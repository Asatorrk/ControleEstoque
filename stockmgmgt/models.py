from django.db import models

category_choice = (
		('Bolo', 'Bolo'),
		('Bolo no pote', 'Bolo no pote'),
	)
#class Category(models.Model):
#	name =models.CharField(max_length=50, blank=True, null=True)
#	def __str__(self):
#		return self.name



class Stock(models.Model):
	category = models.CharField(max_length=50, blank=False, null=True)
	item_name = models.CharField(max_length=50, blank=False, null=True)
	quantity = models.IntegerField(default='0', blank=False, null=True)
	receive_quantity = models.IntegerField(default='0', blank=True, null=True)
	receive_by = models.CharField(max_length=50, blank=True, null=True)
	issue_quantity = models.IntegerField(default='0', blank=True, null=True)
	issue_by = models.CharField(max_length=50, blank=True, null=True)
	issue_to = models.CharField(max_length=50, blank=True, null=True)
	phone_number = models.CharField(max_length=50, blank=True, null=True)
	created_by = models.CharField(max_length=50, blank=True, null=True)
	reorder_level = models.IntegerField(default='0', blank=True, null=True)
	last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
	expiration_date = models.DateField(blank=False, null=True)  # Adicionando o campo da data de validade
	#timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	#date = models.DateTimeField(auto_now_add=False, auto_now=False)
	barcode = models.CharField(max_length=50, unique=True, blank=False, null=True)

	def __str__(self):
		return self.item_name + ' ' + str(self.quantity)

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    cep = models.CharField(max_length=9)
    endereco = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return self.nome
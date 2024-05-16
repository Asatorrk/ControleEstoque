from django.shortcuts import render, redirect
from django.http import HttpResponse
import csv
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required




# Create your views here.

def home(request):
	title = 'Welcome: This is the home Page'
	form = 'Welcome: This is the Home Page'
	context = {
		"title": title,
		"test": form,
	}
	return redirect('/list_items')
	# return render(request, "home.html", context)


@login_required
def list_items(request):
	header = 'Lista de Itens'
	form = StockSearchForm(request.POST or None)
	queryset = Stock.objects.all()
	context = {
		"header": header,
		"queryset": queryset,
		"form":form,
	}
	if request.method == 'POST':
		queryset = Stock.objects.filter(#category__icontains=form['category'].value(),
									item_name__icontains=form['item_name'].value()
									)
		if form['Exportar_para_EXCEL'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="Lista do estoque.csv"'
			writer = csv.writer(response)
			writer.writerow(['CATEGORIA','NOME ITEM','QUANTIDADE'])
			instance = queryset
			for stock in instance:
				writer.writerow([stock.category, stock.item_name, stock.quantity])
			return response


		context = {
		"form":form,
		"header":header,
		"queryset":queryset,
	}

	return render(request, "list_items.html", context)	


@login_required
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Salvo com Sucesso')
		return redirect('/list_items')
	context = {
		"form": form,
		"title": "Adicionar Itens",
	}
	return render(request, "add_items.html", context)


def update_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = StockUpdateForm(instance=queryset)
	if request.method =='POST':
		form = StockUpdateForm(request.POST, instance=queryset)
		if form.is_valid():
			form.save()
			messages.success(request, 'Salvo com Sucesso')
			return redirect('/list_items')

	context = {
		'form': form
	} 
	return render(request, 'add_items.html', context)


def delete_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	if request.method =='POST':
		queryset.delete()
		messages.success(request, 'Excluído com Sucesso')
		return redirect('/list_items')
	return render(request, 'delete_items.html')

def stock_detail(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"queryset": queryset,
	}
	return render(request, "stock_detail.html", context)


def issue_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
			instance = form.save(commit=False)
			instance.quantity -= instance.issue_quantity
			#instance.issue_by = str(request.user)
			messages.success(request, "Retirado com sucesso. " + str(instance.quantity) + " " + str(instance.item_name) + "s restante no estoque")
			instance.save()

			return redirect('/stock_detail/'+str(instance.id))

			# return httpResponseRedirect(instance.get_absolute_url())

	context = {
			"title": 'Retirar ' + str(queryset.item_name),
			"queryset": queryset,
			"form": form,
			"username": 'Issue By: ' + str(request.user),

	}
	return render(request, "add_items.html", context)

def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
				instance = form.save(commit=False)
				instance.quantity += instance.receive_quantity
				instance.save()
				messages.success(request, "Recebido com sucesso. " + str(instance.quantity) + " " + str(instance.item_name)+"s agora no estoque")

				return redirect('/stock_detail/'+str(instance.id))
				#return HttpResponseRedirect(instance.get_absolute_url())

	context = {
						"title": 'Reaceive ' + str(queryset.item_name),
						"instance": queryset,
						"form":form,
						"username": 'Receive By: ' + str(request.user),

					}
	return render(request, "add_items.html", context)

def reorder_level(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReorderLevelForm(request.POST or None, instance= queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Nivel de estoque " +str(instance.item_name) + " foi atualizado para " + str(instance.reorder_level))

		return redirect("/list_items")
	context = {
			"instance": queryset,
			"form": form,
		}
	return render(request, "add_items.html", context)
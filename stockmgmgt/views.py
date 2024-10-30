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

@login_required
def list_items(request):
    header = 'Lista de Itens'
    form = StockSearchForm(request.POST or None)
    queryset = Stock.objects.all()
    selected_items = []  # Lista para armazenar itens selecionados via código de barras
    total_quantity = 0  # Para somar a quantidade dos itens selecionados

    if request.method == 'POST':
        if 'barcode_item' in request.POST:
            barcode = request.POST.get('barcode')
            try:
                item = Stock.objects.get(barcode=barcode)  # Busca o item pelo código de barras
                selected_items.append(item)  # Adiciona o item à lista de itens selecionados
                total_quantity += item.quantity  # Atualiza a quantidade total
                messages.success(request, f'Item {item.item_name} adicionado à lista.')
            except Stock.DoesNotExist:
                messages.error(request, 'Item não encontrado com esse código de barras.')

        # Processa a baixa dos itens selecionados
        if 'selected_items' in request.POST:
            selected_barcodes = request.POST.getlist('selected_items[]')
            for barcode in selected_barcodes:
                try:
                    item = Stock.objects.get(barcode=barcode)
                    item.quantity -= 1  # Exemplo: diminuindo a quantidade em 1
                    item.save()
                except Stock.DoesNotExist:
                    continue  # Ignorar se o item não existir

            return HttpResponse(status=204)  # Retornar sucesso sem conteúdo

    context = {
        "form": form,
        "header": header,
        "queryset": queryset,
        "selected_items": selected_items,  # Passa a lista de itens selecionados
        "total_quantity": total_quantity,  # Passa a quantidade total dos itens selecionados
    }

    return render(request, "list_items.html", context)

@login_required
def add_items(request):
    form = StockCreateForm(request.POST or None)
    if request.method == 'POST':
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
    if request.method == 'POST':
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
    if request.method == 'POST':
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
        # instance.issue_by = str(request.user)
        messages.success(request, "Retirado com sucesso. " + str(instance.quantity) + " " + str(instance.item_name) + "s restante no estoque")
        instance.save()

        return redirect('/stock_detail/' + str(instance.id))

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
        messages.success(request, "Recebido com sucesso. " + str(instance.quantity) + " " + str(instance.item_name) + "s agora no estoque")

        return redirect('/stock_detail/' + str(instance.id))

    context = {
        "title": 'Receive ' + str(queryset.item_name),
        "instance": queryset,
        "form": form,
        "username": 'Receive By: ' + str(request.user),
    }
    return render(request, "add_items.html", context)

def reorder_level(request, pk):
    queryset = Stock.objects.get(id=pk)
    form = ReorderLevelForm(request.POST or None, instance=queryset)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Nível de estoque " + str(instance.item_name) + " foi atualizado para " + str(instance.reorder_level))

        return redirect("/list_items")
    context = {
        "instance": queryset,
        "form": form,
    }
    return render(request, "add_items.html", context)

@login_required
def barcode_items(request):
    header = 'Retirar Itens por Código de Barras'
    form = BarcodeForm(request.POST or None)

    # Inicializa a lista de itens na sessão como uma lista se não existir
    if 'items_list' not in request.session or not isinstance(request.session['items_list'], list):
        request.session['items_list'] = []

    items_list = request.session['items_list']

    if request.method == 'POST':
        if form.is_valid():
            barcode = form.cleaned_data.get('barcode')
            try:
                item = Stock.objects.get(barcode=barcode)
                
                # Adiciona o item à lista na sessão
                items_list.append({'barcode': item.barcode, 'item_name': item.item_name})
                request.session['items_list'] = items_list
                
                messages.success(request, f'Item {item.item_name} adicionado à lista.')
            except Stock.DoesNotExist:
                messages.error(request, 'Item não encontrado com esse código de barras.')

        # Lógica para finalizar a retirada dos itens
        if 'finalize_items' in request.POST:
            # Dicionário para contar a quantidade de itens a retirar
            item_counts = {}
            for item in items_list:
                barcode = item['barcode']
                item_counts[barcode] = item_counts.get(barcode, 0) + 1  # Conta a quantidade de cada item

            # Verifica se a quantidade a ser retirada é maior que a quantidade disponível
            for barcode, quantity in item_counts.items():
                try:
                    item = Stock.objects.get(barcode=barcode)
                    if item.quantity < quantity:
                        messages.error(request, f'Quantidade insuficiente para {item.item_name}. Disponível: {item.quantity}.<br>Refaça a operação!')
                        # Limpa a lista de itens e redireciona para a página de listagem de itens
                        request.session['items_list'] = []
                        return redirect('/list_items')
                except Stock.DoesNotExist:
                    messages.error(request, f'Item não encontrado com o código de barras: {barcode}')
                    # Limpa a lista de itens e redireciona para a página de listagem de itens
                    request.session['items_list'] = []
                    return redirect('/list_items')

            # Remove os itens do estoque de acordo com as contagens
            for barcode, quantity in item_counts.items():
                try:
                    item = Stock.objects.get(barcode=barcode)
                    item.quantity -= quantity
                    item.save()
                    messages.success(request, f'{quantity} unidades de {item.item_name} retiradas do estoque.')
                except Stock.DoesNotExist:
                    messages.error(request, f'Item não encontrado com o código de barras: {barcode}')

            # Limpa a lista de itens após a finalização
            request.session['items_list'] = []
            messages.success(request, 'Operação finalizada com sucesso.')

            # Redireciona para a página de listagem de itens
            return redirect('/list_items')

    context = {
        'header': header,
        'form': form,
        'items_list': items_list,  # Passa a lista de itens adicionados
    }
    return render(request, 'barcode_items.html', context)























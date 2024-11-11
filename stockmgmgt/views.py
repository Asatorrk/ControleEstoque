from django.shortcuts import render, redirect
from django.http import HttpResponse
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
    form = StockSearchForm(request.GET or None)  # Alterando para usar GET
    queryset = Stock.objects.all()  # Inicia com todos os itens
    selected_items = []
    total_quantity = 20

    # Limpa a lista de itens na sessão quando acessar a página de listagem de itens
    if 'items_list' in request.session:
        del request.session['items_list']

    # Processamento do formulário de pesquisa
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        if search_query:
            queryset = queryset.filter(item_name__icontains=search_query)  # Filtra pelo nome do item

    context = {
        "form": form,
        "header": header,
        "queryset": queryset,  # Passando os itens filtrados
        "selected_items": selected_items,
        "total_quantity": total_quantity,
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
        
        # Verifica se a quantidade a ser retirada é maior do que a quantidade disponível
        if instance.issue_quantity > instance.quantity:
            messages.error(request, "Quantidade insuficiente em estoque. Não foi possível realizar a retirada.")
            return redirect('/stock_detail/' + str(instance.id))
        
        # Realiza a retirada, pois a quantidade é válida
        instance.quantity -= instance.issue_quantity
        instance.save()
        messages.success(request, f"{instance.issue_quantity} unidades de {instance.item_name} retiradas com sucesso. Quantidade restante: {instance.quantity}")
        
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

    if 'items_list' not in request.session or not isinstance(request.session['items_list'], list):
        request.session['items_list'] = []

    items_list = request.session['items_list']

    if request.method == 'POST':
        # Adiciona um item pela leitura do código de barras
        if form.is_valid():
            barcode = form.cleaned_data.get('barcode')
            try:
                item = Stock.objects.get(barcode=barcode)
                items_list.append({'barcode': item.barcode, 'item_name': item.item_name})
                request.session['items_list'] = items_list
                messages.success(request, f'Item {item.item_name} adicionado à lista.')
            except Stock.DoesNotExist:
                messages.error(request, 'Item não encontrado com esse código de barras.')

        # Remove uma unidade do item específico ao clicar no botão de exclusão
        if 'remove_item' in request.POST:
            barcode_to_remove = request.POST.get('remove_item')
            # Encontra e remove a primeira ocorrência do item com o código de barras
            for i, item in enumerate(items_list):
                if item['barcode'] == barcode_to_remove:
                    del items_list[i]
                    break
            request.session['items_list'] = items_list
            messages.success(request, 'Item removido da lista.')

        # Finalizar a operação
        if 'finalize_items' in request.POST:
            # Mantém o mesmo processamento de finalização da operação
            item_counts = {}
            for item in items_list:
                barcode = item['barcode']
                item_counts[barcode] = item_counts.get(barcode, 0) + 1

            for barcode, quantity in item_counts.items():
                try:
                    item = Stock.objects.get(barcode=barcode)
                    if item.quantity < quantity:
                        messages.error(request, f'Quantidade insuficiente para {item.item_name}. Disponível: {item.quantity}.<br>Refaça a operação!')
                        request.session['items_list'] = []
                        return redirect('/list_items')
                except Stock.DoesNotExist:
                    messages.error(request, f'Item não encontrado com o código de barras: {barcode}')
                    request.session['items_list'] = []
                    return redirect('/list_items')

            for barcode, quantity in item_counts.items():
                try:
                    item = Stock.objects.get(barcode=barcode)
                    item.quantity -= quantity
                    item.save()
                    messages.success(request, f'{quantity} unidades de {item.item_name} retiradas do estoque.')
                except Stock.DoesNotExist:
                    messages.error(request, f'Item não encontrado com o código de barras: {barcode}')

            request.session['items_list'] = []
            messages.success(request, 'Operação finalizada com sucesso.')
            return redirect('/list_items')

    context = {
        'header': header,
        'form': form,
        'items_list': items_list,
    }
    return render(request, 'barcode_items.html', context)



@login_required
def remove_item_from_list(request, barcode):
    if request.method == 'POST':
        # Obtém a lista de itens da sessão
        items_list = request.session.get('items_list', [])

        # Remove o item específico da lista
        items_list = [item for item in items_list if item['barcode'] != barcode]

        # Atualiza a sessão com a lista alterada
        request.session['items_list'] = items_list

        # Exibe mensagem de sucesso
        messages.success(request, 'Item removido da lista com sucesso.')

    # Redireciona de volta para a página de controle de código de barras
    return redirect('barcode_items')

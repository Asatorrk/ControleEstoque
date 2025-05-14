from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
import matplotlib
matplotlib.use('Agg')  # Força o Matplotlib a usar um backend não interativo
import matplotlib.pyplot as plt
from .models import Stock
from django.db import connection
import io
import base64
import pandas as pd
from django.http import HttpResponse, JsonResponse
import requests
import json
from datetime import datetime



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
    selected_items = []
    total_quantity = 20

    # Limpa a lista de itens na sessão quando acessar a página de listagem de itens
    if 'items_list' in request.session:
        del request.session['items_list']

    if request.method == 'POST':
        if 'barcode_item' in request.POST:
            barcode = request.POST.get('barcode')
            try:
                item = Stock.objects.get(barcode=barcode)
                selected_items.append(item)
                total_quantity += item.quantity
                messages.success(request, f'Item {item.item_name} adicionado à lista.')
            except Stock.DoesNotExist:
                messages.error(request, 'Item não encontrado com esse código de barras.')

        if 'selected_items' in request.POST:
            selected_barcodes = request.POST.getlist('selected_items[]')
            for barcode in selected_barcodes:
                try:
                    item = Stock.objects.get(barcode=barcode)
                    item.quantity -= 1
                    item.save()
                except Stock.DoesNotExist:
                    continue

            return HttpResponse(status=204)

    context = {
        "form": form,
        "header": header,
        "queryset": queryset,
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
        instance.quantity -= instance.issue_quantity
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


def relatorio_itens_retirados(request):
    # Obter parâmetros de filtro
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    top_n = request.GET.get('top_n', '10')  # Garante que recebe uma string

    # Converte `top_n` para inteiro
    try:
        top_n = int(top_n)
    except ValueError:
        top_n = 10  # Se for inválido, usa o valor padrão

    # Construir filtros dinâmicos
    params = []
    filters = []

    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            filters.append("DATE(last_updated) >= %s")
            params.append(data_inicio)
        except ValueError:
            data_inicio = None  # Ignora se for inválido

    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            filters.append("DATE(last_updated) <= %s")
            params.append(data_fim)
        except ValueError:
            data_fim = None  # Ignora se for inválido

    # Construir query SQL
    query = """
    SELECT item_name, SUM(issue_quantity) AS total_retirado, MAX(last_updated) AS last_updated
    FROM stockmgmgt_stock
    WHERE issue_quantity > 0
    """

    if filters:
        query += " AND " + " AND ".join(filters)

    query += " GROUP BY item_name ORDER BY total_retirado DESC LIMIT %s;"
    params.append(top_n)

    # Executar a query e buscar os dados
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    # Criar dataframe do Pandas
    df = pd.DataFrame(rows, columns=['item_name', 'total_retirado', 'last_updated']) if rows else pd.DataFrame()

    # Criar gráfico se houver dados
    img = None
    if not df.empty:
        plt.figure(figsize=(10, 5))
        plt.bar(df['item_name'], df['total_retirado'], color='blue')
        plt.xlabel('Item')
        plt.ylabel('Quantidade Retirada')
        plt.title('Itens mais retirados')
        plt.xticks(rotation=45)
        plt.grid()

        # Converter gráfico para imagem base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        string = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        img = f'data:image/png;base64,{string}'

    return render(request, 'relatorio.html', {
        'df': df.to_dict(orient='records'),
        'img': img,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'top_n': top_n
    })


def buscar_endereco_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@login_required
def cadastrar_pessoa(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        cep = request.POST.get("cep")
        numero = request.POST.get("numero")
        complemento = request.POST.get("complemento")

        endereco_info = buscar_endereco_cep(cep)

        if endereco_info and "erro" not in endereco_info:
            endereco = endereco_info.get("logradouro", "")
            bairro = endereco_info.get("bairro", "")
            cidade = endereco_info.get("localidade", "")
            estado = endereco_info.get("uf", "")
        else:
            messages.error(request, "CEP inválido ou não encontrado.")
            return redirect("/cadastrar_pessoa")

        Cliente.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            cep=cep,
            endereco=endereco,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado
        )

        messages.success(request, "Pessoa cadastrada com sucesso!")
        return redirect("/listar_pessoas")

    return render(request, "cadastro_pessoa.html")

@login_required
def listar_pessoas(request):
    pessoas = Cliente.objects.all()
    return render(request, "listar_pessoas.html", {"pessoas": pessoas})



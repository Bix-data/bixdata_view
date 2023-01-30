from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
import requests
import json
import datetime


def get_render_index(request):
    response = requests.get(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_tables_menu")
    menu_list = json.loads(response.text)

    print(menu_list.items())
    print(type(menu_list))
    for workspace_key, workspace_value in menu_list.items():
        print(type(workspace_value))
        for table in workspace_value:
            print(type(table))
            print(table.get('description'))

    context = {
        'menu_list': menu_list,
        'date': datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'),

    }

    return render(request, 'index.html', context)


def get_render_loading(request):
    return render(request, 'other/loading.html')

#request: {tableid}
def get_render_content_records(request):
    context = dict()
    records_table = 'records table';
    context['records_table'] = records_table
    tableid=request.POST.get('table')
    context['table']= tableid.upper()
    context['tableid']= tableid
    context['views']=dict()
    return render(request, 'content/records.html')

def get_render_content_charts(request):
    return render(request, 'content/charts.html')




def get_block_records_table(request):
    table = request.POST.get('table')
    searchTerm = request.POST.get('searchTerm')
    viewid= request.POST.get('viewid')
    post = {
        'table': table,
        'searchTerm': searchTerm,
        'viewid':viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': table,
    }

    for records_index, record in enumerate(records):
        for record_index, value in enumerate(record):
            if record_index == 4:
                # record[index]=split(value)
                value = value.split('|:|')
                record[record_index] = value[0]
            else:
                record[record_index] = value
        records[records_index] = record

    records_table = render_to_string('block/records/records_table.html', context, request=request)
    return records_table


def get_block_records_gantt(request):
    table = request.POST.get('table')
    searchTerm = request.POST.get('searchTerm')
    viewid= request.POST.get('viewid')
    post = {
        'table': table,
        'searchTerm': searchTerm,
        'viewid':viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': table,
    }

    for records_index, record in enumerate(records):
        for record_index, value in enumerate(record):
            if record_index == 4:
                # record[index]=split(value)
                value = value.split('|:|')
                record[record_index] = value[0]
            else:
                record[record_index] = value
        records[records_index] = record

    records_table = render_to_string(
        'block/records_table.html', context, request=request)
    return records_table

def get_block_records_kanban(request):
    table = request.POST.get('table')
    searchTerm = request.POST.get('searchTerm')
    viewid= request.POST.get('viewid')
    post = {
        'table': table,
        'searchTerm': searchTerm,
        'viewid':viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': table,
    }

    for records_index, record in enumerate(records):
        for record_index, value in enumerate(record):
            if record_index == 4:
                # record[index]=split(value)
                value = value.split('|:|')
                record[record_index] = value[0]
            else:
                record[record_index] = value
        records[records_index] = record

    records_table = render_to_string(
        'block/records_table.html', context, request=request)
    return records_table

def get_block_records_calendar(request):
    table = request.POST.get('table')
    searchTerm = request.POST.get('searchTerm')
    viewid= request.POST.get('viewid')
    post = {
        'table': table,
        'searchTerm': searchTerm,
        'viewid':viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': table,
    }

    for records_index, record in enumerate(records):
        for record_index, value in enumerate(record):
            if record_index == 4:
                # record[index]=split(value)
                value = value.split('|:|')
                record[record_index] = value[0]
            else:
                record[record_index] = value
        records[records_index] = record

    records_table = render_to_string(
        'block/records_table.html', context, request=request)
    return records_table


def get_block_record(request):
    table = request.POST.get('table')
    searchTerm = request.POST.get('searchTerm')
    viewid= request.POST.get('viewid')
    post = {
        'table': table,
        'searchTerm': searchTerm,
        'viewid':viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': table,
    }

    for records_index, record in enumerate(records):
        for record_index, value in enumerate(record):
            if record_index == 4:
                # record[index]=split(value)
                value = value.split('|:|')
                record[record_index] = value[0]
            else:
                record[record_index] = value
        records[records_index] = record

    records_table = render_to_string(
        'block/records_table.html', context, request=request)
    return records_table


def get_block_record_card(request):
    context = dict()
    context['recordcard_preview'] = get_block_record_badge(request)
    context['record_linked_labels']= get_block_record_linkedlabels(request)
    returned = render_to_string('block/record/record_card.html', context, request=request)
    return HttpResponse(returned)

def get_block_record_badge(request):
    context = dict()
    tableid = request.POST.get('tableid')
    recordid = request.POST.get('recordid')
    post = {
        'tableid': tableid,
        'recordid': recordid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_fissi", data=post)
    print(response)
    response_dict = json.loads(response.text)
    context['fields'] = response_dict
    records_table = render_to_string('block/record/record_badge.html', context, request=request)
    return records_table


def get_block_record_linkedlabels(request):
    
    context = dict()
    post = {
        'tableid': 'company',
        'recordid': '1234',
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_record_labels", data=post)
    response_dict = json.loads(response.text)
    context['labels'] = response_dict
    record_linked_labels = render_to_string('block/record/record_linked.html', context, request=request)
    return record_linked_labels
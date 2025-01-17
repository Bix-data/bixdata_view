from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
import requests
import json
import datetime
from django.contrib.auth.decorators import login_required
import time
from .forms import LoginForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth.models import Group, Permission, User, Group
from django_user_agents.utils import get_user_agent
from bixdata_app.models import MyModel


def user_agent(request, page, mobilepage, context={}):
    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(request, mobilepage, context)
    else:
        return render(request, page, context)

# from .models import Login
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_test_query(request, name=None):
    with connection.cursor() as cursor1:
        cursor1.execute(
            "SELECT query_conditions FROM sys_view WHERE id = 9"
        )
        query = cursor1.fetchone()[0]

        with connection.cursor() as cursor2:
            cursor2.execute(query)
            rows = cursor2.fetchall()

            users = [row[0] for row in rows]
            effective_margins = [row[1] for row in rows]
            expected_margins = [row[2] for row in rows]

            data = {
                'users': users,
                'effective_margins': effective_margins,
                'expected_margins': expected_margins
            }

            # Get the custom permission
            permission = Permission.objects.get(codename='can_do_something')

            # Assign the permission to a group
            # group = Group.objects.get(name='My group')
            # group.permissions.add(permission)

            # Assign the permission to a user
            user = User.objects.get(username='test')
            user.user_permissions.add(permission)

            # Check if a user has a permission
            if user.has_perm('can_do_something'):
                print('has permission')
            else:
                print('no permission')

    return render(request, 'other/test_query.html', {'data': data})


def get_full_data(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        print(name)
        with connection.cursor() as cursor1:
            cursor1.execute(
                "SELECT query_conditions FROM sys_view WHERE id = 10"
            )
            query = cursor1.fetchone()[0]
            # query = query.replace('namee', name)
            with connection.cursor() as cursor2:
                cursor2.execute(
                    # "select dealname, expectedmargin, effectivemargin from user_deal where dealuser = %s", [name]
                    query
                )
                rows = cursor2.fetchall()
                dealname = [row[0] for row in rows]
                expectedmargin = [row[1] for row in rows]
                effectivemargin = [row[2] for row in rows]

                dealname = str(dealname)
                dealname = dealname.split(',')

                expectedmargin = str(expectedmargin)
                expectedmargin = expectedmargin.split(',')

                effectivemargin = str(effectivemargin)
                effectivemargin = effectivemargin.split(',')

                data2 = {
                    'dealname': dealname,
                    'expectedmargin': expectedmargin,
                    'effectivemargin': effectivemargin,
                    'name': name
                }
                # print(data)

    return JsonResponse(data2)


def get_test_query2(request):
    with connection.cursor() as cursor1:
        cursor1.execute(
            "SELECT query_conditions FROM sys_view WHERE id = 11"
        )
        query = cursor1.fetchone()[0]
        with connection.cursor() as cursor2:
            cursor2.execute(
                query
            )
            rows = cursor2.fetchall()
            effective_margins = [row[0] for row in rows]
            months = [row[1] for row in rows]

            months = months[1::]
            effective_margins = effective_margins[1::]

            for i in range(len(effective_margins)):
                if effective_margins[i] == None:
                    effective_margins[i] = 0

            data = {
                'effective_margins': effective_margins,
                'months': months
            }

    return render(request, 'other/test_query2.html', {'data': data}, print(data))


def get_full_data2(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        with connection.cursor() as cursor1:
            cursor1.execute(
                "SELECT query_conditions FROM sys_view WHERE id = 12"
            )
            query = cursor1.fetchone()[0]
            with connection.cursor() as cursor2:
                cursor2.execute(
                    # "SELECT dealname, effectivemargin FROM user_deal WHERE closedate LIKE %s", [f"{date}-%"]
                    query
                )

                rows = cursor2.fetchall()
                dealname = [row[0] for row in rows]
                effectivemargin = [row[1] for row in rows]

                dealname = str(dealname)
                dealname = dealname.split(',')

                effectivemargin = str(effectivemargin)
                effectivemargin = effectivemargin.split(',')

                data2 = {
                    'dealname': dealname,
                    'effectivemargin': effectivemargin,
                    'date': date
                }

                # print(data)

    return JsonResponse(data2)


@login_required(login_url='/login/')
def get_render_index(request):
    response = requests.get(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_tables_menu")
    menu_list = json.loads(response.text)

    username = request.user

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
        'username': username,
    }

    return user_agent(request, 'index.html', 'index2.html', context)
    #return render(request, 'index.html', context)


def get_render_loading(request):
    return render(request, 'other/loading.html')


# request: {tableid}
@login_required(login_url='/login/')
def get_content_records(request):
    context = dict()
    records_table = get_block_records_table(request);
    context['records_table'] = records_table
    tableid = request.POST.get('tableid')
    context['table'] = tableid.upper()
    context['tableid'] = tableid
    context['views'] = dict()
    return user_agent(request, 'content/records.html', 'content/records_mobile.html', context)
    #return render(request, 'content/records.html', context)


@login_required(login_url='/login/')
def get_render_content_chart(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT dealuser, SUM(effectivemargin), sum(expectedmargin) FROM user_deal WHERE dealuser is not null GROUP BY dealuser")
        rows = cursor.fetchall()
        users = [row[0] for row in rows]
        effective_margins = [row[1] for row in rows]
        expected_margins = [row[2] for row in rows]

        data = {
            'users': users,
            'effective_margins': effective_margins,
            'expected_margins': expected_margins,
        }

    return render(request, 'records/records_chart.html', {'data': data})


@login_required(login_url='/login/')
def get_block_records_chart(request):
    context = dict()
    tableid = request.POST.get('tableid')
    post = {
        'table': 'deal',
        'searchTerm': '',
    }
    response = requests.post("http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records_chart", data=post)
    response_dict = json.loads(response.text)
    label = response_dict['label'];

    label = '# of test'
    labels = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
    labels = json.dumps(labels)
    data = [12, 19, 3, 5, 2, 3]
    data = json.dumps(data)

    context = {
        'label': label,
        'labels': labels,
        'data': data,
    }
    records_table = render_to_string('block/records/records_chart.html', context, request=request)
    return HttpResponse(records_table)


@login_required(login_url='/login/')
def get_test(request):
    return render(request, 'content/test.html')


@login_required(login_url='/login/')
def get_block_reload(request):
    return render(request)


@login_required(login_url='/login/')
def get_render_content_dashboard(request):
    return user_agent(request, 'content/dashboard.html', 'content/dashboard_mobile.html', None)
    #return render(request, 'content/dashboard.html')


@login_required(login_url='/login/')
def get_record_card_copy(request):
    return render(request)


@login_required(login_url='/login/')
def get_record_card_delete(request):
    return render(request)


@login_required(login_url='/login/')
def get_record_card_permissions(request):
    return render(request)


@login_required(login_url='/login/')
def get_record_card_pin(request):
    return render(request)


# https://openclassrooms.com/en/courses/7107341-intermediate-django/7263317-create-a-login-page-with-a-function-based-view


def get_render_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')

            else:
                messages.error(request, 'Invalid username or password')

            """if username == 'admin' and password == 'admin':

                return redirect('index')
            else:
                form.add_error(None, "Invalid username or password")"""

            # request.session['message'] = 'Invalid username or password'



    else:
        form = LoginForm()
    #return user_agent(request, 'other/login.html', 'other/test_query.html', {'form': form})
    return render(request, 'other/login.html', {'form': form}, )


@user_passes_test(lambda u: u.is_superuser)
def get_render_gestione_utenti(request):
    return render(request, 'other/gestione_utenti.html')


@login_required(login_url='/login/')
def get_render_logout(request):
    logout(request)
    return render(request, 'other/login.html')


@login_required(login_url='/login/')
def get_block_records_table(request):
    tableid = request.POST.get('tableid')
    searchTerm = request.POST.get('searchTerm')
    viewid = request.POST.get('viewid')
    post = {
        'tableid': tableid,
        'searchTerm': searchTerm,
        'viewid': viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': tableid,
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


@login_required(login_url='/login/')
def get_block_records_gantt(request):
    context = dict()
    tableid = request.POST.get('tableid')
    post = {
        'table': 'task',
        'searchTerm': '',
    }

    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records_gantt", data=post)
    response_dict = json.loads(response.text)

    records = response_dict['records']
    # print(records)
    records_gantt = []
    for record in records:
        new_record = dict()
        new_record['id'] = record[1]
        new_record['name'] = record[2]
        new_record['start'] = record[3]
        new_record['end'] = record[4]
        new_record['progress'] = 100

        records_gantt.append(new_record)
    records_json = json.dumps(records_gantt)

    context = {
        'records': records,
        'records_json': records_json,
    }
    records_table = render_to_string('block/records/records_gantt.html', context, request=request)
    return HttpResponse(records_table)


@login_required(login_url='/login/')
def get_block_records_kanban(request):
    context = dict()
    tableid = request.POST.get('tableid')
    post = {
        'table': 'deal',
        'searchTerm': '',
    }

    # response = requests.post("http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records_kanban", data=post)
    # response_dict = json.loads(response.text)

    # records = response_dict['records']
    # print(records)
    groups = []
    # for record in records:
    #   new_record = dict()
    #  new_record['id'] = record[1]
    # new_record['name'] = record[2]
    # new_record['start'] = record[3]
    # new_record['end'] = record[4]
    # new_record['progress'] = 100
    #    records_kanban.append(new_record)

    group = dict()
    group['description'] = 'TODO test'
    group_records = []
    record = dict()
    record['recordid'] = '123456789'
    record['title'] = 'title'
    record['tag'] = 'tag'
    record['date'] = 'date'
    record['user'] = 'user'
    record['field1'] = 'field1'
    record['field2'] = 'field2'
    record['field3'] = 'field3'
    record['field4'] = 'field4'
    group_records.append(record)
    group['records'] = group_records
    groups.append(group);

    group = dict()
    group['description'] = 'IN PROGRESS'
    group_records = []
    record = dict()
    record['recordid'] = '2222344453'
    record['title'] = 'title2'
    record['tag'] = 'tag2'
    record['date'] = 'date2'
    record['user'] = 'user2'
    record['field1'] = 'field12'
    record['field2'] = 'field22'
    record['field3'] = 'field32'
    record['field4'] = 'field42'
    group_records.append(record);
    group['records'] = group_records
    groups.append(group);

    context = {
        'groups': groups,
    }
    records_table = render_to_string('block/records/records_kanban.html', context, request=request)
    return HttpResponse(records_table)


@login_required(login_url='/login/')
def get_block_records_calendar(request):
    tableid = request.POST.get('tableid')
    searchTerm = request.POST.get('searchTerm')
    viewid = request.POST.get('viewid')
    post = {
        'tableid': tableid,
        'searchTerm': searchTerm,
        'viewid': viewid,
    }
    response = requests.post(
        "http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_records", data=post)
    response_dict = json.loads(response.text)
    columns = response_dict['columns']
    records = response_dict['records']
    context = {
        'records': records,
        'columns': columns,
        'tableid': tableid,
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

    records_table = render_to_string('block/records/records_calendar.html', context, request=request)
    return HttpResponse(records_table)


@login_required(login_url='/login/')
def get_block_record(request):
    table = request.POST.get('table')
    searchTerm = request.POST.get('searchTerm')
    viewid = request.POST.get('viewid')
    post = {
        'table': table,
        'searchTerm': searchTerm,
        'viewid': viewid,
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


@login_required(login_url='/login/')
def get_block_record_card(request):
    context = dict()
    context['block_record_badge'] = get_block_record_badge(request)
    context['block_record_linked'] = get_block_record_linked_pytest(request)
    #context['block_record_linked'] = get_block_record_linked(request)
    context['block_record_fields'] = get_block_record_fields(request)
    returned = render_to_string('block/record/record_card.html', context, request=request)
    return HttpResponse(returned)


@login_required(login_url='/login/')
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
    response_dict = json.loads(response.text)
    context['fields'] = response_dict
    records_table = render_to_string('block/record/record_badge.html', context, request=request)
    return records_table


@login_required(login_url='/login/')
def get_block_record_fields(request):
    context = dict()
    http_response = request.POST.get('http_response')
    tableid = request.POST.get('tableid')
    recordid = request.POST.get('recordid')
    post = {
        'tableid': tableid,
        'recordid': recordid,
    }
    response = requests.post("http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_record_fields", data=post)
    response_dict = json.loads(response.text)
    context['record_fields'] = response_dict
    context['function'] = 'edit'
    context['tableid'] = tableid
    context['recordid'] = recordid
    block_record_fields = render_to_string('block/record/record_fields.html', context, request=request)
    if (http_response):
        return HttpResponse(block_record_fields)
    else:
        return block_record_fields


@login_required(login_url='/login/')
def get_block_record_linked(request):
    context = dict()
    tableid = request.POST.get('tableid')
    recordid = request.POST.get('recordid')
    post = {
        'tableid': tableid,
        'recordid': recordid,
    }
    response = requests.post("http://10.0.0.133:8822/bixdata/index.php/rest_controller/get_record_labels", data=post)
    response_dict = json.loads(response.text)
    context['labels'] = response_dict
    record_linked_labels = render_to_string('block/record/record_linked.html', context, request=request)
    return record_linked_labels


@login_required(login_url='/login/')
def get_block_record_linked_pytest(request):
    tableid = request.POST.get('tableid')
    print(tableid)

    with connection.cursor() as cursor:
        cursor.execute("SELECT tablelinkid FROM sys_table_link WHERE tableid = 'company'")
        rows = dictfetchall(cursor)
        context = dict()
        context['labels'] = rows

    record_linked_labels = render_to_string('block/record/record_linked.html', {'context': context}, request=request)
    return record_linked_labels


@login_required(login_url='/login/')
def get_linked(request):
    name = ''
    if request.method == 'POST':
        name = request.POST.get('name')
    return JsonResponse(name)


@login_required(login_url='/login/')
def save_record_fields(request):
    tableid = ''
    recordid = ''
    fields = ''

    tableid = request.POST.get('tableid')
    recordid = request.POST.get('recordid')
    fields = request.POST.get('fields')
    post = {
        'tableid': tableid,
        'recordid': recordid,
        'fields': fields
    }

    response = requests.post("http://10.0.0.133:8822/bixdata/index.php/rest_controller/set_record", data=post)
    return render(request, 'block/record/record_fields.html')

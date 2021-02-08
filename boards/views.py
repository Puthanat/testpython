from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404,HttpResponse,JsonResponse
from .forms import NewTopicForm
from .models import Board, Topic, Post
import xlwt

from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum

def home(request):
    mgs = {
                    'massage' : ' '
                }
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        comment = request.POST.get('comment')
        add = Board(
            name = firstname,
            description = comment
        )
        add.save()
        mgs = {
                    'massage' : 'Sussecs'
                }
        
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards, 'mgs':mgs})

def about(request):
    # do something...
    return render(request, 'about.html')

def Profile(request):
    boards = Board.objects.all().order_by('id')
    return render(request, 'Profile.html',{'boards': boards})

def about_company(request):
    # do something else...
    # return some data along with the view...
    return render(request, 'about_company.html', {'company_name': 'Simple Complex'})

def board_topics(request, pk):
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404
    return render(request, 'topics.html', {'board': board})
    
def topics(request,board_id):
    boards = Board.objects.get(pk=board_id)
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        comment = request.POST.get('comment')
        star = request.POST.get('star')
        boards.name = firstname
        boards.description = comment
        boards.num_stars = star
        boards.save()
        return redirect('Profile')
    return render(request, 'topics.html',{'boards': boards})

def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['รหัสพนักงาน', 'ชื่อ-นามสกุล', 'ความคิดเห็น',]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    boards = Board.objects.all().order_by('id').values_list('id', 'name','description')
    for row in boards:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="users.pdf"'

    response['Content-Transfer-Encoding']='binary'

    html_string=render_to_string('pdf-output.html',{'total':0})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()


        output=open(output.name,'rb')
        response.write(output.read())
    
    return response

def population_chart(request):
    labels = []
    data = []

    queryset = Board.objects.order_by('-num_stars')
    for Boards in queryset:
        labels.append(Boards.name)
        data.append(Boards.num_stars)
    
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })
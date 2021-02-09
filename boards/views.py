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
import datetime
import requests, xmltodict

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

def login(request):
    aerror = {
                'x' : ' '
                }
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if username == '464628' or username == '501103':
                check_ID = idm_login(username,password)
                reposeMge = check_ID  
                if reposeMge == 'true':
                        nameget = idm(username)
                        Fullname = nameget['TitleFullName']+nameget['FirstName']+' '+nameget['LastName']
                        Position = nameget['Position']+nameget['LevelCode']+nameget['DepartmentShort']
                        StaffDate = nameget['StaffDate'].split('/')
                        Workage = int(StaffDate[2])-543
                        today = datetime.datetime.today()
                        yearBE = today.year
                        Someyear = yearBE-Workage  
                        print(Fullname,Position,Someyear)
                        return redirect('home')
        else:
            aerror = {
                    'x':'Invalid Credentials. Please try again.'
                    }
    return render(request,'login.html',{'aerror': aerror})        

def idm_login(username, password):
    # Emp_passc = str(Emp_pass)
    print('--------------------')
    
    url="https://idm.pea.co.th/webservices/idmservices.asmx?WSDL"
    headers = {'content-type': 'text/xml'}
    xmltext ='''<?xml version="1.0" encoding="utf-8"?>
                 <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <IsValidUsernameAndPassword_SI xmlns="http://idm.pea.co.th/">
                        <WSAuthenKey>{0}</WSAuthenKey>
                        <Username>{1}</Username>
                        <Password>{2}</Password>
                        </IsValidUsernameAndPassword_SI>
                    </soap:Body>
                </soap:Envelope>'''
    wskey = '07d75910-3365-42c9-9365-9433b51177c6'
    body = xmltext.format(wskey,username,password)
    response = requests.post(url,data=body,headers=headers)
    print(response.status_code)
    o = xmltodict.parse(response.text)
    jsonconvert=dict(o)
    # print(o)
    authen_response = jsonconvert["soap:Envelope"]["soap:Body"]["IsValidUsernameAndPassword_SIResponse"]["IsValidUsernameAndPassword_SIResult"]["ResultObject"]
    return authen_response

def idm(username):
    url="https://idm.pea.co.th/webservices/EmployeeServices.asmx?WSDL"
    headers = {'content-type': 'text/xml'}
    xmltext ='''<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                <soap:Body>
                    <GetEmployeeInfoByEmployeeId_SI xmlns="http://idm.pea.co.th/">
                        <WSAuthenKey>{0}</WSAuthenKey>
                        <EmployeeId>{1}</EmployeeId>
                        </GetEmployeeInfoByEmployeeId_SI>
                </soap:Body>
                </soap:Envelope>'''
    wsauth = 'e7040c1f-cace-430b-9bc0-f477c44016c3'
    body = xmltext.format(wsauth,username)
    response = requests.post(url,data=body,headers=headers)
    o = xmltodict.parse(response.text)

    # print(o)
    jsonconvert=o["soap:Envelope"]['soap:Body']['GetEmployeeInfoByEmployeeId_SIResponse']['GetEmployeeInfoByEmployeeId_SIResult']['ResultObject']
    employeedata = dict(jsonconvert)
    # print(employeedata['FirstName'])
    return employeedata
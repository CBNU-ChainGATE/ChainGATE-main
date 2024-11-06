from django.db import connection
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import requests
from django.http import JsonResponse
from datetime import datetime

@csrf_protect
def login_view(request):
    if request.method == "POST":
        login_id = request.POST['loginId']
        login_pw = request.POST['loginPw']
        

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username FROM user WHERE username = %s AND password = %s", 
                [login_id, login_pw]
            )
            user = cursor.fetchone()
        
        if user:
            request.session['username'] = user[0] 
            return redirect('management:search_visitor') 
        else:
            return render(request, 'management/login.html', {
                'error_message': 'ID 또는 비밀번호가 잘못되었습니다.'
            })
    else:
        return render(request, 'management/login.html')

def search_user(request):
    name = request.GET.get('name', '')
    department = request.GET.get('department', '')
    user_id = request.GET.get('user_id', None)

    users = []
    details = []

    with connection.cursor() as cursor:
        if name or department:
            cursor.execute("""
                SELECT User_id, Name, Affiliation, Position 
                FROM user 
                WHERE Name LIKE %s AND Affiliation LIKE %s
            """, [f"%{name}%", f"%{department}%"])
        else:
            cursor.execute("SELECT User_id, Name, Affiliation, Position FROM user")
        
        users = cursor.fetchall()

        if user_id:
            cursor.execute("""
                SELECT User_id, Name, Affiliation, Position, Dob, Phone, Email, photo
                FROM user
                WHERE User_id = %s
            """, [user_id])
            details = cursor.fetchone()

    return render(request, 'management/SearchUser.html', {
        'users': users,
        'details': details
    })

def search_visitor(request):
    name = request.GET.get('name', '')
    department = request.GET.get('department', '')
    visitor_id = request.GET.get('visitor_id', None)

    visitors = []
    details = []
    
    with connection.cursor() as cursor:
        if name or department:
            cursor.execute("""
                SELECT Visitor_id, Name, Affiliation, Position, Emp_no 
                FROM visitor 
                WHERE Name LIKE %s AND Affiliation LIKE %s
            """, [f"%{name}%", f"%{department}%"])
        else:
            cursor.execute("SELECT Visitor_id, Name, Affiliation, Position, Emp_no FROM visitor")
        
        visitors = cursor.fetchall()

        if visitor_id:
            cursor.execute("""
                SELECT Visitor_id, Name, Affiliation, Position, Dob, Phone, Email, Emp_no, photo
                FROM visitor
                WHERE Visitor_id = %s
            """, [visitor_id])
            details = cursor.fetchone()

    print(visitors) 
    return render(request, 'management/SearchVisitor.html', {
        'visitors': visitors,
        'details': details
    })

def create_visitor(request):
    return render(request, 'management/CreateVisitor.html')

def update_visitor(request):
    visitor_id = request.GET.get('visitor_id', None)
    visitor_details = None

    if visitor_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT visitor_id, Name, Affiliation, Position, Dob, Phone, Email, emp_no, photo
                FROM visitor 
                WHERE visitor_id = %s
            """, [visitor_id])
            visitor_details = cursor.fetchone()

    return render(request, 'management/UpdateVisitor.html', {
        'visitor_details': visitor_details 
    })

def save_visitor(request):
    if request.method == 'POST':
        visitor_id = request.POST.get('visitor_id')
        name = request.POST.get('name')
        department = request.POST.get('department')
        position = request.POST.get('position')
        dob = request.POST.get('dob')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        emp_no = request.POST.get('emp_no')

        photo_url = None

        if request.FILES.get('photo'):
            photo = request.FILES['photo']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photo'))
            filename = fs.save(photo.name, photo)
            photo_url = f"photo/{filename}"

        cursor = connection.cursor()

        if photo_url:
            cursor.execute("""
                UPDATE visitor
                SET Name = %s, Affiliation = %s, Position = %s, Dob = %s,
                    Phone = %s, Email = %s, Emp_no = %s, Photo = %s
                WHERE visitor_id = %s
            """, [name, department, position, dob, phone, email, emp_no, photo_url, visitor_id])
        else:
            cursor.execute("""
                UPDATE visitor
                SET Name = %s, Affiliation = %s, Position = %s, Dob = %s,
                    Phone = %s, Email = %s, Emp_no = %s
                WHERE visitor_id = %s
            """, [name, department, position, dob, phone, email, emp_no, visitor_id])

        return redirect('management:search_visitor')
    


def create_user(request):
    return render(request, 'management/createUser.html')

def update_user(request): 
    user_id = request.GET.get('user_id', None)
    user_details = None

    if user_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT User_id, Name, Affiliation, Position, Dob, Phone, Email, Username, Password, Photo
                FROM user 
                WHERE User_id = %s
            """, [user_id])
            user_details = cursor.fetchone()

    return render(request, 'management/UpdateUser.html', {
        'user_details': user_details 
    })

def save_user(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        name = request.POST.get('name')
        department = request.POST.get('department')
        position = request.POST.get('position')
        dob = request.POST.get('dob')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('id')
        password = request.POST.get('pw')

        photo_url = None
        
        if request.FILES.get('photo'):
            photo = request.FILES['photo']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photo'))
            filename = fs.save(photo.name, photo)
            photo_url = f"photo/{filename}" 

        cursor = connection.cursor()
        if photo_url:
            cursor.execute("""
                UPDATE user
                SET Name = %s, Affiliation = %s, Position = %s, Dob = %s, Phone = %s, Email = %s, Username = %s, Password = %s, Photo = %s
                WHERE User_id = %s
            """, (name, department, position, dob, phone, email, username, password, photo_url, user_id))
        else:
            cursor.execute("""
                UPDATE user
                SET Name = %s, Affiliation = %s, Position = %s, Dob = %s, Phone = %s, Email = %s, Username = %s, Password = %s
                WHERE User_id = %s
            """, (name, department, position, dob, phone, email, username, password, user_id))

        return redirect('management:search_user')
    
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM user WHERE User_id = %s", [user_id])

        return redirect('management:search_user')
    
def insert_user(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        position = request.POST.get('position')
        dob = request.POST.get('dob')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('id')
        password = request.POST.get('pw')

        photo_url = ""

        if request.FILES.get('photo'):
            photo = request.FILES['photo']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photo'))
            filename = fs.save(photo.name, photo)
            photo_url = f"photo/{filename}" 

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user (Name, Affiliation, Position, Dob, Phone, Email, Username, Password, Photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, department, position, dob, phone, email, username, password, photo_url))

        return redirect('management:search_user')

def insert_visitor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        position = request.POST.get('position')
        dob = request.POST.get('dob')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        emp_no = request.POST.get('emp_no')

        photo_url = ""

        if request.FILES.get('photo'):
            photo = request.FILES['photo']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photo'))
            filename = fs.save(photo.name, photo)
            photo_url = f"photo/{filename}" 

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO visitor (Name, Affiliation, Position, Dob, Phone, Email, Emp_no, Photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [name, department, position, dob, phone, email, emp_no, photo_url])

        return redirect('management:search_visitor')
    
def entrance_log(request):
    records = []
    details = None
    error_message = ""

    # 검색 필드 값 가져오기
    date = request.POST.get('date') or request.GET.get('date') or ""
    name = request.POST.get('name') or request.GET.get('name') or ""
    department = request.POST.get('department') or request.GET.get('department') or ""

    # POST 요청이 있을 경우 (검색 기능)
    if request.method == 'POST':
        data = {
            "date": date,
            "employee_id": "",
            "name": name,
            "department": department
        }

        try:
            response = requests.post('http://27.35.94.180:1551/api/blockchain/search', json=data)
            response_data = response.json()

            if response.status_code == 200 and 'results' in response_data:
                records = response_data['results']
                # 검색 결과와 검색 필드 값을 세션에 저장
                request.session['search_records'] = records
                request.session['search_date'] = date
                request.session['search_name'] = name
                request.session['search_department'] = department
            else:
                print(f"Error fetching data: {response_data}")
        except Exception as e:
            print(f"API request error: {e}")

    # GET 요청 시 세션에서 검색 결과와 필드를 가져옴
    else:
        records = request.session.get('search_records', [])
        date = request.session.get('search_date', "")
        name = request.session.get('search_name', "")
        department = request.session.get('search_department', "")

    # employee_id에 대한 상세 정보 조회
    employee_id = request.GET.get('employee_id')
    if employee_id:
        with connection.cursor() as cursor:
            cursor.execute(""" 
                SELECT Visitor_id, Name, Affiliation, Position, Dob, Phone, Email, Emp_no, photo
                FROM visitor
                WHERE Emp_no = %s
            """, [employee_id])
            details = cursor.fetchone()

            # 상세 정보가 없을 경우 오류 메시지 설정
            if details is None:
                error_message = "삭제된 출입자입니다."

    return render(request, 'management/EntranceLog.html', {
        'records': records,
        'details': details,
        'error_message': error_message,  # 오류 메시지 전달
        'date': date,
        'name': name,
        'department': department
    })


@csrf_exempt
def enroll_fingerprint(request):
    if request.method == "POST":
        emp_no = request.POST.get('emp_no')
        data = {'employee_id': emp_no}

        try:
            #response = requests.post('http://192.168.0.19:5001/finger/enroll', json=data) #donggu home
            #response = requests.post('http://172.20.10.2:5001/finger/enroll', json=data) #donggu
            response = requests.post('http://172.30.76.106:5001/finger/enroll', json=data) #CBNU-WIFI
            result = response.json()

            if result.get('success'):
                return JsonResponse({'message': '지문 등록이 성공적으로 완료되었습니다.'})
            else:
                return JsonResponse({'message': '지문 등록에 실패하였습니다.'})

        except requests.exceptions.RequestException as e:
            return JsonResponse({'message': f'지문 등록 중 오류가 발생하였습니다: {str(e)}'})

    return JsonResponse({'message': '잘못된 요청입니다.'})

@csrf_exempt
def delete_visitor(request):
    if request.method == 'POST':
        visitor_id = request.POST.get('visitor_id')
        emp_no = request.POST.get('emp_no')

        # 지문 삭제 요청을 먼저 시도
        data = {'employee_id': emp_no}
        try:
            response = requests.post('http://172.30.76.106:5001/finger/delete', json=data)
            result = response.json()

            if result.get('success'):
                # 지문 삭제 성공 시, 출입자 정보 삭제
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM visitor WHERE Visitor_id = %s", [visitor_id])

                return JsonResponse({'message': '출입자와 지문 정보가 성공적으로 삭제되었습니다.'})
            else:
                # 지문 삭제 실패 시
                return JsonResponse({'message': '지문 삭제에 실패하여 출입자 삭제가 취소되었습니다.'}, status=400)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'message': f'지문 삭제 중 오류가 발생하였습니다: {str(e)}'}, status=500)

    return JsonResponse({'message': '잘못된 요청입니다.'}, status=400)

@csrf_exempt
def approve_entry(request):
    if request.method == "GET":
        try:
            #fingerprint_response = requests.get('http://172.20.10.2:5001/finger/search')
            #fingerprint_response = requests.get('http://192.168.0.19:5001/finger/search',)
            fingerprint_response = requests.get('http://172.30.76.106:5001/finger/search') #CBNU-WIFI
            fingerprint_data = fingerprint_response.json()
            print(fingerprint_data)
            if fingerprint_data.get('success'):
                emp_no = fingerprint_data.get('employee_id')

                cursor = connection.cursor()
                cursor.execute("""
                    SELECT Name, Position, Affiliation
                    FROM visitor
                    WHERE Emp_no = %s
                """, [emp_no])
                visitor = cursor.fetchone()

                if visitor:
                    name, position, department = visitor
                    now = datetime.now()
                    date = now.strftime('%Y-%m-%d')
                    time = now.strftime('%H:%M:%S')

                    transaction_data = {
                        "date": date,
                        "time": time,
                        "employee_id": emp_no,
                        "name": name,
                        "position": position,
                        "department": department
                    }

                    transaction_response = requests.post('http://27.35.94.180:1551/api/blockchain/new', json=transaction_data)
                    transaction_result = transaction_response.json()

                    if transaction_response.status_code == 201:
                        return JsonResponse({'message': '출입 승인이 완료되었습니다.'})
                    else:
                        return JsonResponse({'message': f'출입 승인 중 오류가 발생하였습니다: {transaction_result}'})

                else:
                    return JsonResponse({'message': '해당 사번의 사용자를 찾을 수 없습니다.'})

            else:
                return JsonResponse({'message': '지문이 등록되어 있지 않습니다.'})

        except requests.exceptions.RequestException as e:
            return JsonResponse({'message': f'지문 확인 중 오류가 발생하였습니다: {str(e)}'})

    return JsonResponse({'message': '잘못된 요청입니다.'})
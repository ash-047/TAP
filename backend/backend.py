from functools import wraps 
from flask import Flask, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
from datetime import datetime
import ollama
import json
from fpdf import FPDF
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
cors = CORS(app)

pswd = os.getenv('PASSWORD')

# Role-based access control decorator
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                return redirect(url_for('login'))
            
            if session['role'] not in allowed_roles:
                return jsonify({'message': 'Unauthorized access'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    
    conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
    )

    cursor = conn.cursor()
    
    loginQuery = """CALL ValidateSignIn(%s, %s, @isValid);"""
    cursor.execute(loginQuery, (username, password))
    cursor.execute("SELECT @isValid;")
    user = cursor.fetchone()
    
    if user[0] == 0:
        cursor.close()
        return jsonify({'message': 'Invalid credentials'}), 401
    
    session['user_id'] = username
    if username.startswith(('PES1UG', 'PES2UG')):
        session['role'] = 'student'
        redirect_url = '/student-dashboard'
    elif username[0] in ('1', '2'):
        session['role'] = 'ta'
        redirect_url = '/ta-dashboard'
    elif username.startswith(('PES1TT', 'PES2TT')):
        session['role'] = 'admin'
        redirect_url = '/admin-dashboard'
    else:
        cursor.close()
        return jsonify({'message': 'Invalid user type'}), 400
    
    session['user_id'] = username
    cursor.close()
    
    return jsonify({
        'role': session['role'],
        'redirect': redirect_url,
        'username': username
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/student-dashboard', methods=['GET'])
@role_required(['student'])
def student_dashboard():
    conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student WHERE SRN = %s", (session['user_id'],))
    student_data = cursor.fetchone()
    cursor.close()
    
    return jsonify({
        'message': 'Welcome to the Student dashboard',
        'student_data': student_data
    })

@app.route('/ta-dashboard', methods=['GET'])
@role_required(['ta'])
def ta_dashboard():
    conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TA WHERE TA_ID = %s", (session['user_id'],))
    ta_data = cursor.fetchone()
    cursor.close()
    
    return jsonify({
        'message': 'Welcome to the TA dashboard',
        'ta_data': ta_data
    })

@app.route('/admin-dashboard', methods=['GET'])
@role_required(['admin'])
def admin_dashboard():
    conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Teacher WHERE Teacher_ID = %s", (session['user_id'],))
    admin_data = cursor.fetchone()
    cursor.close()
    
    return jsonify({
        'message': 'Welcome to the Admin dashboard',
        'admin_data': admin_data
    })


@app.route('/check_notifications')
@role_required(['student', 'ta'])
def check_notifications():
    conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Notifications WHERE user_id = %s AND read = 0", (session['user_id'],))
    notifications = cursor.fetchall()
    cursor.close()
    
    return jsonify({
        'notifications': notifications
    })

@app.route('/write_worklog', methods=['POST'])
@role_required(['ta'])
def write_worklog():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id', 'course_id', 'start_timestamp', 'work_description', 'end_timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']
        course_id = data['course_id']
        start_timestamp = data['start_timestamp']
        work_description = data['work_description']
        end_timestamp = data['end_timestamp']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """ CALL AddWorkLog(%s, %s, %s, %s, %s);"""
            cursor.execute(worklogQuery, (ta_id, course_id, start_timestamp, work_description, end_timestamp))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_worklog', methods=['POST'])
@role_required(['ta'])
def update_worklog():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id', 'course_id', 'start_timestamp', 'work_description', 'end_timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']
        course_id = data['course_id']
        start_timestamp = data['start_timestamp']
        work_description = data['work_description']
        end_timestamp = data['end_timestamp']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """CALL EditWorkLog(%s, %s, %s, %s, %s);"""
            cursor.execute(worklogQuery, (ta_id, course_id, start_timestamp, work_description, end_timestamp))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/ta_bank_details', methods=['POST'])
@role_required(['ta'])
def ta_bank_details():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id', 'bank_name', 'account_no', 'ISFC_Code']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']
        bank_name = data['bank_name']
        account_no = data['account_no']
        ISFC_Code = data['ISFC_Code']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """
                INERT INTO TA_Bank_Details (TA_ID, Bank_Name, Account_Number, ISFC_Code)
                VALUES (%s, %s, %s, %s);"""
            cursor.execute(worklogQuery, (ta_id, bank_name, account_no, ISFC_Code))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_ta_bank_details', methods=['POST'])
@role_required(['ta'])
def update_ta_bank_details():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id', 'bank_name', 'account_no', 'ISFC_Code']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']
        bank_name = data['bank_name']
        account_no = data['account_no']
        ISFC_Code = data['ISFC_Code']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """
                UPDATE TA_Bank_Details
                SET Bank_Name = %s, Account_Number = %s, ISFC_Code = %s
                WHERE TA_ID = %s;"""
            cursor.execute(worklogQuery, (bank_name, account_no, ISFC_Code, ta_id))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/display_ta_bank_details', methods=['GET'])
def display_ta_bank_details():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """
                SELECT Bank_Name, Account_Number, ISFC_Code
                FROM TA_Bank_Details
                WHERE TA_ID = %s;"""
            cursor.execute(worklogQuery, (ta_id))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/display_worklog', methods=['GET'])
def display_worklog():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id', 'course_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']
        course_id = data['course_id']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """
                SELECT Start_Timestamp, Work_Description, End_Timestamp
                FROM Worklog
                WHERE TA_ID = %s AND Course_ID = %s;"""
            cursor.execute(worklogQuery, (ta_id, course_id))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def workDescriptionsSummarizer(work_descriptions):
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': f'Please summarize all the work done by a certain Teaching Assistant given the work done by the day everytime he is on the clock: {work_descriptions}. Please ensure that the summary is provided in a json format: "Summary: [point1, point2, ..]"',
        },
    ])
    return response['message']['content']

def worklogAndTADetails(ta_id, course_id, output_file):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=pswd,
            database='TAPortal'
        )
        
        cursor = conn.cursor()
        
        worklogQuery = """CALL GenerateWorkReport(%s, %s);"""
        cursor.execute(worklogQuery, (ta_id, course_id))
        worklogResults = cursor.fetchall()

        cursor.nextset()
        bankDetails = cursor.fetchall()

        cursor.close()
        conn.close()
        
        totalTime = 0
        work_descriptions = []
        for start, description, end in worklogResults:
            startTime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            endTime = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            totalTime += (endTime - startTime).total_seconds()
            work_descriptions.append(description)
        
        workSummary = workDescriptionsSummarizer(work_descriptions)
        workSummary = json.loads(workSummary.split("```")[1])["Summary"]
        workSummary = "\n".join(f"- {summary}" for summary in workSummary)
        
        txt_path = f"{output_file}.txt"
        pdf_path = f"{output_file}.pdf"
        
        with open(txt_path, 'w') as file:
            if worklogResults:
                file.write("Worklog Details:\n")
                file.write(f"\nTotal Time Worked: {totalTime / 3600:.2f} hours\n")
                file.write(f"\nSummary of Work Descriptions:\n{workSummary}\n")
            else:
                file.write("No worklog details found for the given TA_ID and Course_ID.\n")
            
            if bankDetails:
                file.write("\nTA Bank Details:\n")
                file.write(f"Bank Name: {bankDetails[0]}\n")
                file.write(f"Account Number: {bankDetails[1]}\n")
                file.write(f"ISFC Code: {bankDetails[2]}\n")
            else:
                file.write("No TA bank details found for the given TA_ID.\n")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        
        with open(txt_path, "r") as f:
            for x in f:
                pdf.cell(200, 10, txt=x.strip(), ln=1, align='C')
        
        pdf.output(pdf_path)
        return txt_path, pdf_path
        
    except mysql.connector.Error as err:
        raise Exception(f"Database error: {err}")
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")

@app.route('/generate_report', methods=['POST'])
@role_required(['admin'])
def generate_report():
    try:
        data = request.get_json()
        
        required_fields = ['ta_id', 'course_id', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        ta_id = data['ta_id']
        course_id = data['course_id']
        output_file = f"report_{ta_id}_{course_id}"
        
        txt_path, pdf_path = worklogAndTADetails(ta_id, course_id, output_file)
        
        # Return the PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"report_{ta_id}_{course_id}.pdf"
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up temporary files
        try:
            os.remove(txt_path)
            os.remove(pdf_path)
        except:
            pass

def send_notification(srn, notification):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=pswd,
            database='TAPortal'
        )
        
        cursor = conn.cursor()
        notificationQuery = """
            INSERT INTO Notifications (SRN, Notification)
            VALUES (%s, %s)"""
        cursor.execute(notificationQuery (srn, notification))
        
        cursor.close()
        conn.commit()
        conn.close()

    except mysql.connector.Error as err:
        raise Exception(f"Database error: {err}")
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")


@app.route('/approval', methods=['POST'])
@role_required(['admin'])
def approval():
    try:
        data = request.get_json()
        required_fields = ['srn', 'course_id', 'teacher_id']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        srn = data['srn']
        course_id = data['course_id']
        teacher_id = data['teacher_id']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()

            approvalQuery = """CALL ApproveTA(srn, teacher_id, course_id, @p_TA_ID);"""
            cursor.execute(approvalQuery, (srn, teacher_id, course_id))
            cursor.execute("SELECT @p_TA_ID;")
            ta_id = cursor.fetchone()
            ta_id = ta_id[0]

            notification = f"Your request for being a TA has been approved. Please go to the administrator to receive your TA credentials."
            send_notification(srn, notification)
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assign', methods=['POST'])
@role_required(['admin'])
def assign():
    try:
        data = request.get_json()
        required_fields = ['class_id', 'ta_id']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        class_id = data['class_id']
        ta_id = data['ta_id']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            assignedQuery = """CALL AssignTAToClass(%s, %s);"""
            cursor.execute(assignedQuery, (ta_id, class_id))

            cursor.close()
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}") 

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sign_up', methods=['POST'])
@role_required(['admin'])
def sign_up():
    try:
        data = request.get_json()
        required_fields = ['Username', 'Password']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        username = data['Username']
        password = data['Password']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            signUpQuery = """
                INSERT INTO sign_in (Username, Password)
                VALUES (%s, %s, %s);"""
            cursor.execute(signUpQuery, (username, password))

            cursor.close()
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}") 

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_sign_up', methods=['POST'])
@role_required(['admin'])
def delete_sign_up():
    try:
        data = request.get_json()
        required_fields = ['Username']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        username = data['Username']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            deleteSignUpQuery = """
                DELETE FROM sign_in WHERE Username = %s;"""
            cursor.execute(deleteSignUpQuery, (username))

            cursor.close()
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}") 

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_assign', methods=['POST'])
@role_required(['admin'])
def delete_assign():
    try:
        data = request.get_json()
        required_fields = ['class_id', 'ta_id']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        class_id = data['class_id']
        ta_id = data['ta_id']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            deleteAssignedQuery = """
                DELETE FROM TA WHERE Class_ID = %s AND TA_ID = %s;"""
            cursor.execute(deleteAssignedQuery, (class_id, ta_id))

            cursor.close()
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}") 

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_ta', methods=['POST'])
@role_required(['admin'])
def delete_ta():
    try:
        data = request.get_json()
        required_fields = ['ta_id', 'srn']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        ta_id = data['ta_id']
        srn = data['srn']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            deleteTaQuery = """
                DELETE FROM TA WHERE TA_ID = %s AND SRN = %s;"""
            cursor.execute(deleteTaQuery, (ta_id, srn))

            cursor.close()
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}") 

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/display_approval', methods=['GET'])
@role_required(['admin'])
def display_approval():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=pswd,
            database='TAPortal'
        )
        
        cursor = conn.cursor()
        
        requestQuery = """
            SELECT * FROM Approval;"""
        cursor.execute(requestQuery)
        cursor.close()
        conn.commit()
        conn.close()
        
    except mysql.connector.Error as err:
        raise Exception(f"Database error: {err}")
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")



@app.route('/student_request', methods=['POST'])
@role_required(['student'])
def student_request():
    try:
        data = request.get_json()
        required_fields = ['srn', 'course_id', 'teacher_id']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
            
        srn = data['srn']
        course_id = data['course_id']
        teacher_id = data['teacher_id']

        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=pswd,
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            requestQuery = """
                INSERT INTO Request (SRN, Course_Id, Teacher_ID)
                VALUES (%s, %s, %s);"""
            cursor.execute(requestQuery, (srn, course_id, teacher_id))

            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug = True, port = 8000)
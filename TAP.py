import streamlit as st
import mysql.connector
from datetime import datetime
import json
import tempfile
import os
from fpdf import FPDF
import ollama
from streamlit_option_menu import option_menu
from dotenv import load_dotenv

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None

load_dotenv()
pswd = os.getenv('MYSQL_PASSWORD')

def get_database_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password=pswd,
        database='TAPortal'
    )

def workDescriptionsSummarizer(work_descriptions):
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': f'Please summarize all the work done by a certain Teaching Assistant given the work they have done when on the clock: {work_descriptions}. Please ensure that the summary is provided in a json format: "Summary: [point1, point2, ..]").',
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
        bankDetails = bankDetails[0]

        cursor.close()
        conn.close()
        
        totalTime = 0
        work_descriptions = []
        
        for start, description, end in worklogResults:
            startTime = start if isinstance(start, datetime) else datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            endTime = end if isinstance(end, datetime) else datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            duration = (endTime - startTime).total_seconds()
            
            totalTime += duration
            work_descriptions.append(description)
        
        workSummary = workDescriptionsSummarizer(work_descriptions)

        try:
            parts = workSummary.split("```")
            if len(parts) > 1:
                workSummary = json.loads(parts[1])["Summary"]
            else:
                workSummary = json.loads(workSummary)["Summary"]
        except (IndexError, json.JSONDecodeError) as e:
            workSummary = json.loads(workSummary)["Summary"]

        workSummary = "\n".join(f"- {summary}" for summary in workSummary)

        txt_path = f"{output_file}.txt"
        pdf_path = f"{output_file}.pdf"
        
        with open(txt_path, 'w') as file:
            if worklogResults:
                file.write("Worklog Details:\n")
                file.write(f"\nTotal Time Worked: {totalTime / 3600:.2f} hours\n")
                file.write(f"\nSummary of Work Done:\n{workSummary}\n")
            else:
                file.write("No worklog details found for the given TA_ID and Course_ID.\n")
            
            if bankDetails:
                file.write("\nBank Details:\n")
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
        return pdf_path
        
    except mysql.connector.Error as err:
        raise Exception(f"Database error: {err}")
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")

def generate_report(ta_id, course_id):
    with tempfile.TemporaryDirectory() as temp_dir:
        print(temp_dir)
        output_file = os.path.join(temp_dir, f"report_{ta_id}_{course_id}")
        pdf_path = worklogAndTADetails(ta_id, course_id, output_file)
        
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        return pdf_bytes

def send_approval_notification(srn, course_id):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        notification_msg = f"""Your TA request for course {course_id} has been approved! 
        Please visit the admin to receive your TA_ID and the login details to the portal."""
        insert_notification = """
            INSERT INTO Notifications (SRN, Message)
            VALUES (%s, %s);"""
        cursor.execute(insert_notification, (srn, notification_msg))
        
        conn.commit()
        cursor.close()
    except Exception as e:
        st.error(f"Error sending notification: {str(e)}")

def approve_student(srn, course_id, teacher_id):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        approve_query = """CALL ApproveStudent(%s, %s, %s, @new_TA_ID);"""
        cursor.execute(approve_query, (srn, teacher_id, course_id))
        cursor.execute("SELECT @new_TA_ID;")
        new_ta_id = cursor.fetchone()[0]
        
        st.success(f"TA approved successfully! New TA ID: {new_ta_id}")
        send_approval_notification(srn, course_id)

        signUpCheck = """
            IF NOT EXISTS(
            SELECT 1 
            FROM sign_in 
            WHERE Username = %s)"""
        cursor.execute(signUpCheck, (new_ta_id))
        result = cursor.fetchone()

        if result[0] == 1:
            signUpQuery = """
                INSERT INTO sign_in (Username, Password)
                VALUES (%s, %s);"""
            cursor.execute(signUpQuery, (new_ta_id, "pass"))
        conn.commit()
        cursor.close()
    except Exception as e:
        st.error(f"Error approving TA: {str(e)}")

def send_rejection_notification(srn, course_id):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        notification_msg = f"Your TA request for course {course_id} has sadly been declined!"
        insert_notification = """
            INSERT INTO Notifications (SRN, Message)
            VALUES (%s, %s);"""
        cursor.execute(insert_notification, (srn, notification_msg))
        
        conn.commit()
        cursor.close()
    except Exception as e:
        st.error(f"Error sending notification: {str(e)}")

def reject_student(srn, course_id):
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        reject_query = """CALL RejectStudent(%s, %s);"""
        cursor.execute(reject_query, (srn, course_id))
        
        conn.commit()
        cursor.close()
        st.success("TA request rejected successfully!")
        send_rejection_notification(srn, course_id)
    except Exception as e:
        st.error(f"Error rejecting TA request: {str(e)}")

def login(username, password):
    conn = get_database_connection()
    cursor = conn.cursor()
    
    login_query = """CALL ValidateSignIn(%s, %s, @isValid);"""
    cursor.execute(login_query, (username, password))
    cursor.execute("SELECT @isValid;")
    user = cursor.fetchone()
    
    if user[0] == 0:
        cursor.close()
        return False, None
    
    if username.startswith(('PES1UG', 'PES2UG')):
        role = 'student'
    elif username[0] in ('1', '2'):
        role = 'ta'
    elif username.startswith(('PES1TT', 'PES2TT')):
        role = 'admin'
    else:
        cursor.close()
        return False, None
    
    cursor.close()
    return True, role

def student_dashboard():
    st.title("Student Dashboard")
    
    menu = ["TA Request", "View Notifications"]
    choice = option_menu("Menu", menu, icons=['pencil-square', 'bell'], 
                        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if choice == "TA Request":
        st.subheader("Request to be a TA")
        with st.form("request_form"):
            course_id = st.text_input("Course ID")
            teacher_id = st.text_input("Teacher ID")
            submitted = st.form_submit_button("Submit Request")
            
            if submitted:
                if not course_id or not teacher_id:
                    st.error("Please fill in both the Course ID and Teacher ID fields")
                    return
                try:
                    conn = get_database_connection()
                    cursor = conn.cursor()
                    
                    request_query = """
                        INSERT INTO Request (SRN, Course_Id, Teacher_ID)
                        VALUES (%s, %s, %s);"""
                    cursor.execute(request_query, (st.session_state.user_id, course_id, teacher_id))
                    
                    conn.commit()
                    cursor.close()
                    st.success("Request submitted successfully!")
                except Exception as e:
                    st.error(f"Error submitting request: {str(e)}")

    elif choice == "View Notifications":
        st.subheader("Notifications")
        try:
            conn = get_database_connection()
            cursor = conn.cursor()

            notificationsQuery = "SELECT * FROM Notifications WHERE SRN = %s AND `Read` = 0;"
            cursor.execute(notificationsQuery, (st.session_state.user_id,))
            notifications = cursor.fetchall()
            cursor.close()
            
            for notification in notifications:
                col1, col2 = st.columns([10,1])
                with col1:
                    st.info(notification[1])
                with col2:
                    if st.button("✕", key=f"dismiss_{notification[0]}"):
                        cursor = conn.cursor()
                        update_query = "UPDATE Notifications SET `Read` = 1 WHERE SRN = %s;"
                        cursor.execute(update_query, (notification[0],))
                        conn.commit()
                        cursor.close()
                        st.rerun()
        except Exception as e:
            st.error(f"Error fetching notifications: {str(e)}")

def ta_dashboard():
    st.title("TA Dashboard")
    
    menu = ["Worklog", "View Worklogs", "Bank Details", "Assigned Classes"]
    choice = option_menu("Menu", menu, icons=['journal', 'bank', 'bell', 'check2-circle'], 
                        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if choice == "Worklog":
        st.subheader("Write Worklog")
        with st.form("worklog_form"):
            course_id = st.text_input("Course ID")
            start_date = st.date_input("Start Date")
            
            hours = [datetime.strptime(f"{i:02d}:00", "%H:%M").time() for i in range(24)]
            # start_time = st.time_input("Start Time")
            start_time = st.selectbox("Start Time", hours, format_func=lambda x: x.strftime("%H:%M"))
            
            end_date = st.date_input("End Date")
            # end_time = st.time_input("End Time")
            end_time = st.selectbox("End Time", hours, format_func=lambda x: x.strftime("%H:%M"))
            
            work_description = st.text_area("Work Description")

            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            submitted = st.form_submit_button("Submit Worklog")
            
            if submitted:
                if not course_id or not start_datetime or not work_description or not end_datetime:
                    st.error("Please fill in all the required fields (Course ID, Start Date, Start Time, End Date, End Time, and Work Description)")
                    return
                try:
                    conn = get_database_connection()
                    cursor = conn.cursor()
                    
                    worklog_query = """CALL AddWorkLog(%s, %s, %s, %s, %s);"""
                    cursor.execute(worklog_query, (st.session_state.user_id, course_id, 
                                                 start_datetime, work_description, end_datetime))
                    
                    conn.commit()
                    cursor.close()
                    st.success("Worklog submitted successfully!")
                except Exception as e:
                    st.error(f"Error submitting worklog: {str(e)}")

    elif choice == "View Worklogs":
        st.subheader("View Worklogs")
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            
            worklogQuery = """
                SELECT Course_ID, Start_Timestamp, Work_Description, End_Timestamp
                FROM Worklog
                WHERE TA_ID = %s
                ORDER BY Course_ID DESC, Start_Timestamp ASC;
            """
            cursor.execute(worklogQuery, (st.session_state.user_id,))
            worklog_results = cursor.fetchall()
            
            formatted_data = []
            for course, start, description, end in worklog_results:
                formatted_data.append({
                    "Course": course,
                    "Date": start.strftime("%Y-%m-%d"),
                    "Start Time": start.strftime("%H:%M"),
                    "End Time": end.strftime("%H:%M"),
                    "Description": description
                })
            
            st.dataframe(
                formatted_data,
                column_config={
                    "Course": st.column_config.TextColumn("Course"),
                    "Date": st.column_config.TextColumn("Date"),
                    "Start Time": st.column_config.TextColumn("Start Time"),
                    "End Time": st.column_config.TextColumn("End Time"),
                    "Description": st.column_config.TextColumn("Description", width="large")
                }
            )

            if not worklog_results:
                st.info("No worklog entries found for this TA and course.")
                return
            
            if 'show_worklog_update_form' not in st.session_state:
               st.session_state.show_worklog_update_form = False

            if st.button("Update Worklog Details"):
                st.session_state.show_worklog_update_form = not st.session_state.show_worklog_update_form

            if st.session_state.show_worklog_update_form:
                st.subheader("Update Worklog Details")
                with st.form("update_worklog_form", clear_on_submit=False):
                    course_id = st.text_input("Course ID")
                    start_date = st.date_input("Start Date")
                    
                    hours = [datetime.strptime(f"{i:02d}:00", "%H:%M").time() for i in range(24)]
                    start_time = st.selectbox("Start Time", hours, format_func=lambda x: x.strftime("%H:%M"))
                    
                    end_date = st.date_input("End Date")
                    end_time = st.selectbox("End Time", hours, format_func=lambda x: x.strftime("%H:%M"))
                    
                    work_description = st.text_area("Work Description")

                    start_datetime = datetime.combine(start_date, start_time)
                    end_datetime = datetime.combine(end_date, end_time)
                    submitted = st.form_submit_button("Update Details")

                    if submitted:
                        if not course_id or not start_datetime or not work_description or not end_datetime:
                            st.error("Please fill in all required fields (Course ID, Start Date, Start Time, End Date, End Time, and Work Description)")
                        else:
                            try:
                                conn = get_database_connection()
                                cursor = conn.cursor()
                                
                                update_query = """CALL EditWorkLog(%s, %s, %s, %s, %s);"""
                                cursor.execute(update_query, (st.session_state.user_id, course_id, 
                                                            start_datetime, work_description, end_datetime))
                                
                                conn.commit()
                                cursor.close()
                                st.success("Worklog updated successfully!")
                                st.session_state.show_worklog_update_form = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating worklog: {str(e)}")

        except Exception as e:
            st.error(f"Error retrieving worklog: {str(e)}")
    
    elif choice == "Bank Details":
        conn = get_database_connection()
        cursor = conn.cursor()

        check_query = """SELECT COUNT(*) FROM TA_Bank_Details WHERE TA_ID = %s;"""
        cursor.execute(check_query, (st.session_state.user_id,))
        result = cursor.fetchone()
        
        if result[0] == 1:
            st.subheader("Bank Details")
            viewBankDetailsQuery = """SELECT Bank_Name, Account_Number, IFSC_Code FROM TA_Bank_Details WHERE TA_ID = %s;"""
            cursor.execute(viewBankDetailsQuery, (st.session_state.user_id,))
            bank_details = cursor.fetchone()

            bank_data = [{
                "Bank Name": bank_details[0],
                "Account Number": bank_details[1],
                "IFSC Code": bank_details[2]
            }]
            
            st.dataframe(
                bank_data,
                column_config={
                    "Bank Name": st.column_config.TextColumn("Bank Name"),
                    "Account Number": st.column_config.TextColumn("Account Number"),
                    "IFSC Code": st.column_config.TextColumn("IFSC Code")
                },
                hide_index=True
            )

            if 'show_update_form' not in st.session_state:
                st.session_state.show_update_form = False

            if st.button("Update Bank Details"):
                st.session_state.show_update_form = not st.session_state.show_update_form

            if st.session_state.show_update_form:
                st.subheader("Update Bank Details")
                with st.form("bank_details_form", clear_on_submit=False):
                    bank_name = st.text_input("Bank Name")
                    account_no = st.text_input("Account Number")
                    ifsc_code = st.text_input("IFSC Code")
                    submitted = st.form_submit_button("Update Details")
                    
                    if submitted:
                        if not bank_name or not account_no or not ifsc_code:
                            st.error("Please fill in all required fields (Bank Name, Account Number, and IFSC Code)")
                        else:
                            try:
                                bankUpdateQuery = """CALL EditBankDetails(%s, %s, %s, %s);"""
                                cursor.execute(bankUpdateQuery, (st.session_state.user_id, bank_name, account_no, ifsc_code))
                                conn.commit()
                                st.success("Bank details updated successfully!")
                                st.session_state.show_update_form = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating bank details: {str(e)}")

    elif choice == "Assigned Classes":
        st.subheader("Assigned Classes")
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            
            assignedClassesQuery = """
                SELECT Class_ID
                FROM Assigned
                WHERE TA_ID = %s;
            """
            cursor.execute(assignedClassesQuery, (st.session_state.user_id,))
            assigned_classes = cursor.fetchall()
            
            if assigned_classes:
                assigned_data = [{"Class ID": cls[0]} for cls in assigned_classes]
                st.dataframe(
                    assigned_data,
                    column_config={
                        "Class ID": st.column_config.TextColumn("Class ID")
                    },
                    hide_index=True
                )
            else:
                st.info("No classes assigned.")
        except Exception as e:
            st.error(f"Error fetching assigned classes: {str(e)}")

def admin_dashboard():
    st.title("Admin Dashboard")
    
    menu = ["Approve TAs", "Assign TAs", "Generate Reports", "Manage TAs"]
    choice = option_menu("Menu", menu, icons=['check-circle', 'person-plus', 'file-text', 'people'], 
                        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if choice == "Approve TAs":
        st.subheader("TA Approval Requests")
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            
            viewTaRequestsQuery = """
                SELECT R.SRN, S.First_Name, S.Last_Name, S.YearOfJoining, R.Course_Id, R.Teacher_ID
                FROM Request R
                JOIN Student S ON R.SRN = S.SRN 
                WHERE R.Accept = 0 AND R.Reject = 0 AND R.Teacher_ID = %s;
            """
            cursor.execute(viewTaRequestsQuery, (st.session_state.user_id,))
            requests = cursor.fetchall()
            cursor.close()
            
            for req in requests:
                col1, col2, col3 = st.columns([3,1,1])
                with col1:
                    st.write(f"SRN: {req[0]}, Name: {req[1]}"+" "+f"{req[2]}, Batch: {req[3]}, Course: {req[4]}")
                with col2:
                    if st.button("Approve", key=f"approve_{req[0]}_{req[4]}_{req[5]}"):
                        approve_student(req[0], req[4], req[5])
                        st.rerun()
                with col3:
                    if st.button("Reject", key=f"reject_{req[0]}_{req[4]}"):
                        reject_student(req[0], req[4])
                        st.rerun()
        except Exception as e:
            st.error(f"Error fetching approval requests: {str(e)}")

    elif choice == "Generate Reports":
        st.subheader("Generate Report")
        generated_pdf = None
        with st.form("generate_report_form"):
            ta_id = st.text_input("TA ID")
            course_id = st.text_input("Course ID")
            submitted = st.form_submit_button("Generate Report")
            
            if submitted:
                if not ta_id or not course_id:
                    st.error("Please fill in both the TA ID and Course ID fields")
                else:
                    try:
                        with st.spinner('Generating report...'):
                            generated_pdf = generate_report(ta_id, course_id)
                            if generated_pdf:
                                st.success("Report generated successfully!")
                            else:
                                st.warning("No data found for the given TA and Course")
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
        
        if generated_pdf:
            st.download_button(
                label="Download Report",
                data=generated_pdf,
                file_name=f"report_{ta_id}_{course_id}.pdf",
                mime='application/pdf'
            )
    
    elif choice == "Assign TAs":
        st.subheader("Assign TAs")
        with st.form("assign_ta_form"):
            ta_id = st.text_input("TA ID")
            class_id = st.text_input("Class ID")
            submitted = st.form_submit_button("Assign TA")
            
            if submitted:
                if not class_id or not ta_id:
                    st.error("Please fill in both the TA ID and Class ID fields")
                    return
                try:
                    conn = get_database_connection()
                    cursor = conn.cursor()
                    
                    assign_query = """CALL AssignTAToClass(%s, %s);"""
                    cursor.execute(assign_query, (ta_id, class_id))
                    
                    conn.commit()
                    cursor.close()
                    st.success("TA assigned successfully!")
                except Exception as e:
                    st.error(f"Error assigning TA: {str(e)}")

        st.header("Delete TA Assignment")
        with st.form("delete_ta_form"):
            class_id = st.text_input("Class ID")
            ta_id = st.text_input("TA ID")
            submitted = st.form_submit_button("Delete TA Assignment")
            
            if submitted:
                if not class_id or not ta_id:
                    st.error("Please fill in both the Class ID and TA ID fields")
                    return
                try:
                    conn = get_database_connection()
                    cursor = conn.cursor()
                    
                    delete_query = "CALL UnassignTAFromClass(%s, %s);"
                    cursor.execute(delete_query, (ta_id, class_id))
                    
                    conn.commit()
                    cursor.close()
                    st.success("TA assignment deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting TA assignment: {str(e)}")

    elif choice == "Manage TAs":
        st.subheader("List of TAs")
        try:
            conn = get_database_connection()
            cursor = conn.cursor()
            taListQuery = """
                    SELECT TA.TA_ID, TA.SRN
                    FROM TA 
                    JOIN Approval ON TA.TA_ID = Approval.TA_ID 
                    WHERE Approval.Teacher_ID = %s"""
            cursor.execute(taListQuery, (st.session_state.user_id,))
            tas = cursor.fetchall()
            cursor.close()
            
            if tas:
                ta_data = [{"TA ID": ta[0], "SRN": ta[1]} for ta in tas]
                st.dataframe(
                    ta_data,
                    column_config={
                    "TA ID": st.column_config.TextColumn("TA ID"),
                    "SRN": st.column_config.TextColumn("SRN")
                    },
                    hide_index=True
                )
            else:
                st.info("No TAs found.")
        except Exception as e:
            st.error(f"Error fetching TA details: {str(e)}")

        st.subheader("Remove TAs")
        with st.form("remove_ta_form"):
            ta_id = st.text_input("TA ID")
            srn = st.text_input("SRN")
            submitted = st.form_submit_button("Remove TA")
            
            if submitted:
                if not ta_id or srn:
                    st.error("Please fill in both the TA ID and SRN fields")
                    return
                try:
                    conn = get_database_connection()
                    cursor = conn.cursor()
                    
                    remove_query = """CALL DeleteTA(%s, %s);"""
                    cursor.execute(remove_query, (ta_id, srn))
                    
                    conn.commit()
                    cursor.close()
                    st.success("TA removed successfully!")
                except Exception as e:
                    st.error(f"Error removing TA: {str(e)}")

def main():
    st.set_page_config(page_title="TA Portal", layout="wide")
    
    if st.session_state.user_id is None:
        st.title("TA Portal Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            success, role = login(username, password)
            if success:
                st.session_state.user_id = username
                st.session_state.role = role
            else:
                st.error("Invalid credentials")
    else:
        if st.button("Logout", key="logout"):
            st.session_state.user_id = None
            st.session_state.role = None
            st.rerun()
            
        if st.session_state.role == "student":
            student_dashboard()
        elif st.session_state.role == "ta":
            ta_dashboard()
        elif st.session_state.role == "admin":
            admin_dashboard()

if __name__ == "__main__":
    main()
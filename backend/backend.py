from flask import Flask, request, jsonify, send_file
import mysql.connector
from datetime import datetime
import ollama
import json
from fpdf import FPDF
import os

app = Flask(__name__)

@app.route('/write_worklog', methods=['GET'])
# @role_required(['ta'])
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
                password='root',
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """
                INSERT INTO Worklog (TA_ID, Course_ID, Start_Timestamp, Work_Description, End_Timestamp)
                VALUES (%s, %s, %s, %s, %s);"""
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
# @role_required(['ta'])
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
                password='root',
                database='TAPortal'
            )
            
            cursor = conn.cursor()
            
            worklogQuery = """
                UPDATE Worklog
                SET Start_Timestamp = %s, End_Timestamp = %s, Work_Description = %s
                WHERE TA_ID = %s AND Course_ID = %s;"""
            cursor.execute(worklogQuery, (start_timestamp, end_timestamp, work_description, ta_id, course_id))
            cursor.close()
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
            raise Exception(f"Database error: {err}")
        except Exception as e:
            raise Exception(f"Error processing request: {str(e)}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_ta_bank_details', methods=['GET'])
# @role_required(['ta'])
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
                password='root',
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
                password='root',
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
                password='root',
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
            password='root',
            database='TAPortal'
        )
        
        cursor = conn.cursor()
        
        worklogQuery = """
            SELECT Start_Timestamp, Work_Description, End_Timestamp
            FROM Worklog
            WHERE TA_ID = %s AND Course_ID = %s;"""
        cursor.execute(worklogQuery, (ta_id, course_id))
        worklogResults = cursor.fetchall()
        
        taQuery = """
            SELECT Bank_Name, Account_Number, ISFC_Code
            FROM TA_Bank_Details
            WHERE TA_ID = %s;"""
        cursor.execute(taQuery, (ta_id,))
        taResult = cursor.fetchone()
        
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
            
            if taResult:
                file.write("\nTA Bank Details:\n")
                file.write(f"Bank Name: {taResult[0]}\n")
                file.write(f"Account Number: {taResult[1]}\n")
                file.write(f"ISFC Code: {taResult[2]}\n")
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
# @role_required(['admin'])
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



if __name__ == "__main__":
    app.run(debug=True)
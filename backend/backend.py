import mysql.connector
from datetime import datetime
import ollama
import json
from fdpf import FPDF

def workDescriptionsSummarizer(work_descriptions):
    response = ollama.chat(model = 'llama3.2', messages = [
    {
        'role': 'user',
        'content': f'Please summarize all the work done by a certain Teaching Assistant given the work done by the day everytime he is on the clock: {work_descriptions}. Please ensure that the summary is provided in a json format: "Summary: [point1, point2, ..]"',
    },
    ])
    return response['message']['content']


def worklogAndTADetails(ta_id, course_id, password, output_file):
    conn = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = f'{password}',
        database = 'TAPortal'
    )
    cursor = conn.cursor()

    worklogQuery = f"""
    SELECT Start_Timestamp, Work_Description, End_Timestamp
    FROM Worklog
    WHERE TA_ID = {ta_id} AND Course_ID = {course_id}"""
    cursor.execute(worklogQuery)
    worklogResults = cursor.fetchall()

    taQuery = f"""
    SELECT Bank_Name, Account_Number, ISFC_Code
    FROM TA
    WHERE TA_ID = {ta_id} """
    cursor.execute(taQuery)
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

    with open(output_file+".txt", 'w') as file:
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
    pdf.set_font("Arial", size = 15)
    
    f = open(output_file+".txt", "r")
    for x in f:
        pdf.cell(200, 10, txt = x, ln = 1, align = 'C')

    pdf.output(output_file+".pdf")

if __name__ == "__main__":
    ta_id = input("Enter TA ID: ")
    course_id = input("Enter Course ID: ")
    password = input("Enter password: ")
    output_file = f"report_{ta_id}_{course_id}"
    worklogAndTADetails(ta_id, course_id, password, output_file)
import ollama
import json
from fpdf import FPDF

def workDescriptionsSummarizer(work_descriptions):
    response = ollama.chat(model = 'llama3.2', messages = [
    {
        'role': 'user',
        'content': f'Please summarize all the work done by a certain Teaching Assistant given the work done by the day everytime he is on the clock: {work_descriptions}. Please ensure that the summary is provided in a json format: "Summary: [point1, point2, ..]"',
    },
    ])
    return response['message']['content']


if __name__ == '__main__':
    # work_descriptions = ["Helped students with their assignments", "Graded assignments", "Created a ppt for the next lecture"]
    # workSummary = workDescriptionsSummarizer(work_descriptions)
    # workSummary = json.loads(workSummary.split("```")[1])["Summary"]
    # workSummary = "\n".join(f"- {summary}" for summary in workSummary)
    fileName = "report"
    workSummary = """
    - Provided academic support to students through assignment help
    - Evaluated student submissions and graded assignments accurately
    - Prepared engaging presentations for upcoming lectures using PowerPoint"""
    with open(fileName+".txt", 'w') as file:
        file.write(f"\nSummary of Work Descriptions:\n{workSummary}\n")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    
    f = open("report.txt", "r")
    for x in f:
        pdf.cell(200, 10, txt = x, ln = 1, align = 'C')

    pdf.output(fileName+".pdf")
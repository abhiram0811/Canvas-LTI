import requests
from django.http import JsonResponse

class CanvasAPI:
    def __init__(self, api_url, access_token, course_id):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.course_id = course_id

    def retrieve_user_data(self, user_roles):
        user_data_url = f"{self.api_url}courses/{self.course_id}/users"
        response = requests.get(user_data_url, headers=self.headers, params={"enrollment_type[]": user_roles})

        if response.status_code == 200:
            return response.json()
        return []

    def retrieve_assignment_data(self):
        assignment_data_url = f"{self.api_url}courses/{self.course_id}/assignments"
        response = requests.get(assignment_data_url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return []

    def retrieve_submission_status(self, assignment_id, user_id):
        submission_url = f"{self.api_url}courses/{self.course_id}/assignments/{assignment_id}/submissions/{user_id}"
        response_submission = requests.get(submission_url, headers=self.headers)

        if response_submission.status_code == 200:
            submission_data = response_submission.json()
            workflow_state = submission_data.get('workflow_state')

            if workflow_state == 'graded' or workflow_state == 'submitted':
                return 'Submitted'
            else:
                return 'Not Submitted'

        return 'Not Submitted'  # Assume 'Not Submitted' if there's an issue with the API

def index(request):
    api_url = "https://canvas.instructure.com/api/v1/"
    access_token = "7~HwSMoPKwaA6GIOVL5qShZGtrHZ1TYsw3dA5ltIrTEHzHRBeDKQYZKZXdqy1bKqLU"
    course_id = "8022424"
    user_roles = ["student"]

    canvas_api = CanvasAPI(api_url, access_token, course_id)
    users_data = canvas_api.retrieve_user_data(user_roles)
    assignments_data = canvas_api.retrieve_assignment_data()

    if not (users_data and assignments_data):
        return JsonResponse({"error": "Data not available"})

    result = []

    for user in users_data:
        user_id, user_name = user['id'], user['name']
        assignments = []

        for assignment in assignments_data:
            assignment_name = assignment['name']
            submission_status = canvas_api.retrieve_submission_status(assignment['id'], user_id)
            assignments.append({'Assignment Name': assignment_name, 'Submission Status': submission_status})

        result.append({'Student Name': user_name, 'Assignments': assignments})

    response_data = []
    for user in result:
        user_info = {"Student Name": user["Student Name"]}
        user_assignments = [{"Assignment Name": assignment.get("Assignment Name", "Name not available"),
                            "Submission Status": assignment.get("Submission Status", "Not Submitted")} for assignment in user.get("Assignments", [])]
        user_info["Assignments"] = user_assignments
        response_data.append(user_info)

    return JsonResponse({"Assignment Status": response_data})

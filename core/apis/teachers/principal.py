from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.teachers import Teacher
from .schema import TeacherSchema

# Create a Blueprint for the principal teachers resources
principal_teachers_resources = Blueprint('principal_teachers_resources', __name__)

# Define the endpoint to list teachers
@principal_teachers_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(p):
    """
    Returns list of teachers for the principal
    """
    # Fetch all teachers
    all_teachers = Teacher.get_all_teachers()
    # Serialize the teachers using the TeacherSchema
    all_teachers_dump = TeacherSchema().dump(all_teachers, many=True)
    # Return the serialized data as a response
    return APIResponse.respond(data=all_teachers_dump)

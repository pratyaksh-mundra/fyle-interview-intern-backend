from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment
from .schema import AssignmentSchema, AssignmentGradeSchema
from .. import decorators
from core.apis.decorators import accept_payload, authenticate_principal

# Create a Blueprint for the principal assignments resources
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

# Define the endpoint to list assignments
@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """
    Returns list of assignments for the principal
    """
    # Fetch all assignments
    principals_assignments = Assignment.list_assignments()
    # Serialize the assignments using the AssignmentSchema
    principals_assignments_dump = AssignmentSchema().dump(principals_assignments, many=True)
    # Return the serialized data as a response
    return APIResponse.respond(data=principals_assignments_dump)

# Define the endpoint to grade an assignment
@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """
    Grade an assignment
    """
    # Deserialize the incoming payload using the AssignmentGradeSchema
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    # Mark the assignment with the given grade
    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    # Commit the changes to the database
    db.session.commit()
    # Serialize the graded assignment using the AssignmentSchema
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    # Return the serialized data as a response
    return APIResponse.respond(data=graded_assignment_dump)

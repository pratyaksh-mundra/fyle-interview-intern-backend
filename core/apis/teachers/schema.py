from marshmallow import Schema, EXCLUDE, fields, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_enum import EnumField
from core.libs.helpers import GeneralObject
from core.models.teachers import Teacher

# Define a schema for serializing and deserializing Teacher objects
class TeacherSchema(SQLAlchemyAutoSchema):
    class Meta:
        # Specify the model to use for the schema
        model = Teacher
        # Exclude unknown fields from the input data
        unknown = EXCLUDE

    # Define fields to be included in the schema
    created_at = auto_field(dump_only=True)  # Field is read-only
    id = auto_field(required=False, allow_none=True)  # Field is optional and can be null
    updated_at = auto_field(dump_only=True)  # Field is read-only
    user_id = auto_field(dump_only=True)  # Field is read-only

    @post_load
    def initiate_class(self, data_dict, many, partial):
        """
        Instantiate a Teacher object after loading the data.
        """
        # pylint: disable=unused-argument,no-self-use
        return Teacher(**data_dict)  # Return a Teacher instance with the loaded data

from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
import jwt
from api.jwt_authorize import token_required
from model.user import Section

section_api = Blueprint('section_api', __name__,
                   url_prefix='/api')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(section_api)

class SectionAPI:        
         
    class _CRUD(Resource):  # Users API operation for Create, Read, Update, Delete 
        @token_required("Admin")
        def post(self): # Create method
            ''' Read data for json body '''
            body = request.get_json()
            
            ''' Avoid garbage in, error checking '''
            # validate section name
            name = body.get('name')
            if name is None or len(name) < 2:
                return {'message': f'Name is missing, or is less than 2 characters'}, 400
            # validate abbreviation 
            abbreviation = body.get('abbreviation')
            if abbreviation is None or len(abbreviation) < 2:
                return {'message': f'Section abbreviation is missing, or is less than 2 characters'}, 400
            
            ''' #1: Setup SECTION OBJECT '''
            so = Section(name=name, 
                      abbreviation=abbreviation)
            
            ''' #2: Add SECTION to DATABASE '''
            # create user in database
            section = so.create()
            # success returns json of section 
            if section:
                return jsonify(section.read())
            # failure returns error
            return {'message': f'Processed {name}, either a format error or User ID {abbreviation} is duplicate'}, 400

        def get(self):
            sections = Section.query.all() # extract all sections from the database
             
            # prepare a json list of user dictionaries
            json_ready = [section.read() for section in sections]  
            
            # return response, a json list of user dictionaries
            return jsonify(json_ready)
        
        @token_required("Admin")
        def delete(self): # Delete Method
            body = request.get_json()
            abbreviation = body.get('abbreviation')
            section = Section.query.filter_by(_abbreviation=abbreviation).first()
            if section is None:
                return {'message': f'Section {section} not found'}, 404
            json = section.read()
            section.delete() 
            # 204 is the status code for delete with no json response
            return f"Deleted user: {json}", 204 # use 200 to test with Postman
         
    # building RESTapi endpoint
    api.add_resource(_CRUD, '/section')

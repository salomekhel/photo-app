import mimetypes
from flask import Response, request
from flask_restful import Resource
from models import Bookmark, bookmark, db, Post
import json
from . import can_view_post
import flask_jwt_extended

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    @flask_jwt_extended.jwt_required()
    def get(self):
        # Your code here
        bookmarks = Bookmark.query.filter_by(user_id=self.current_user.id).order_by('id').all()
        bookmark_list_of_dictionaries = [
            bookmark.to_dict() for bookmark in bookmarks
        ]
        return Response(json.dumps(bookmark_list_of_dictionaries), mimetype="application/json", status=200)
    @flask_jwt_extended.jwt_required()
    def post(self):
        # Your code here
        body = request.get_json()
        if not body:
            return Response(json.dumps({'message': 'Post: bad data'}), mimetype="application/json", status=400)

        post_id = body.get('post_id')
        if not str(post_id).isdigit(): #checking that post_id is a number
            return Response(json.dumps({'message': 'Post: invalid post_id format'}), mimetype="application/json", status=400)
        
        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({'message': 'Post: unauthorized'}), mimetype="application/json", status=404)
        
        # post = Post.query.get(post_id) 
        # if not post or post_id not in Post.id:
        #     return Response(json.dumps({'message': 'Post: invalid post id 404'}), mimetype="application/json", status=404)

        # bookmark = Bookmark.query.filter_by(post_id=post_id).all()
        # if bookmark and bookmark.user_id == user_id:
        #     return Response(json.dumps({'message': 'Post: no duplicates'}), mimetypes="application/json", status=400)
        
        #create post:
        try:
            bookmark = Bookmark(self.current_user.id,post_id)
            db.session.add(bookmark)
            db.session.commit()
        except:
            return Response(json.dumps({'message': 'Post: no duplicates'}), mimetype="application/json", status=400)
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # Your code here
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'DELETE: invalid ID'}), mimetype="application/json", status=400)
        bookmark = Bookmark.query.get(id)
        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
       

        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Post {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<id>', 
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

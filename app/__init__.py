# -*- coding: utf-8 -*-
import logging

import coloredlogs
from flask import Flask
from flask_jsonrpc import JSONRPC, JSONRPCBlueprint
from flask_pymongo import PyMongo

from app.common import AuthorizationSite

coloredlogs.install(level='INFO')
logger = logging.getLogger(__name__)

mongo = PyMongo()

jsonrpc = JSONRPC(None, '/api')

blueprint = JSONRPCBlueprint('blueprint', __name__)
blueprint_admin = JSONRPCBlueprint('blueprint_admin', __name__,
                                   jsonrpc_site=AuthorizationSite)


def after_request(response):
    # 允许跨域请求
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,X-Password'
    response.headers['Access-Control-Max-Age'] = 3600
    return response


def create_app(config_obj):
    app = Flask(__name__)

    app.after_request(after_request)
    # 加载配置文件
    app.config.from_object(config_obj)
    # print(app.config)

    # MongoDB数据库初始化
    mongo.init_app(app)

    jsonrpc.init_app(app)

    from app.onedrive.api import onedrive_bp, onedrive_admin_bp, \
        onedrive_route_bp
    jsonrpc.register_blueprint(app, onedrive_bp, url_prefix='/od')
    jsonrpc.register_blueprint(app, onedrive_admin_bp, url_prefix='/admin/od')

    app.register_blueprint(onedrive_route_bp, url_prefix='/')

    # jsonrpc.register_blueprint(app, tmdb_bp, url_prefix='/tmdb')
    # jsonrpc.register_blueprint(app, tmdb_admin_bp, url_prefix='/admin/tmdb')
    from app import tmdb
    jsonrpc.register_blueprint(app, blueprint, url_prefix='/')
    jsonrpc.register_blueprint(app, blueprint_admin, url_prefix='/admin')

    return app

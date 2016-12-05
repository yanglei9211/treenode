#!/usr/bin/env python
# encoding: utf-8

from tornado.web import HTTPError
from pymongo import UpdateOne

from util.base_handler import BaseHandler
from util.escape import safe_objectid_from_str


class TreeHandler(BaseHandler):
    def get(self, type_id=None):
        if type_id:
            type_id = safe_objectid_from_str(type_id)
        self.render('tree.html',
                    cur_type=type_id)


class SearchNodeHandler(BaseHandler):
    def get(self, type_id=None):
        if type_id:
            type_id = safe_objectid_from_str(type_id)
            nodes = list(self.db.node.find({'type': type_id}, sort=[('index', 1), ('_id', 1)]))
            for r in nodes:
                r['id'] = r['_id']
                if not r['pId']:
                    r['open'] = True
                    r['is_root'] = True
            from debugtools.debug_func import show_pretty_dict
            show_pretty_dict(nodes)
            self.write({'nodes': nodes})


class TreeNodeHandler(BaseHandler):
    def post(self, _id):
        _id = safe_objectid_from_str(_id)
        action = self.get_argument('action')
        res_data = {}
        if action == 'add':
            name = self.get_argument('name')
            new_node = self.create(_id, name)
            res_data['node'] = new_node
        elif action == 'update':
            pass
        elif action == 'delete':
            pass
        elif action == 'update_index':
            p_id = safe_objectid_from_str(self.get_argument('parent'))
            node = self.db.node.find_one({'_id': _id})
            if not node:
                print 'id'
                raise HTTPError(404)
            parent = self.db.node.find_one({'_id': p_id})
            if not parent:
                print 'pid'
                raise HTTPError(404)

            ids = self.get_arguments('ids[]')
            if ids:
                ids = [safe_objectid_from_str(id_) for id_ in ids]
                self.db.node.update({'_id': _id}, {'$set': {'pId': p_id}})
                print ids
                requests = [
                    UpdateOne({'_id': id_}, {'$set': {'index': idx}}) for idx, id_ in enumerate(ids)
                ]
                self.db.node.bulk_write(requests)
            if p_id != node['pId']:
                ori_ids = [r['_id'] for r in self.db.node.find({'pId': node['pId']})]
                print ori_ids
                if ori_ids:
                    requests_ori_idx = [
                        UpdateOne({'_id': id_}, {'$set': {'index': idx}}) for idx, id_ in enumerate(ori_ids)
                    ]
                    self.db.node.bulk_write(requests_ori_idx)

        self.write(res_data)

    def create(self, pid, name):
        parent = self.db.node.find_one({'_id': pid})
        if not parent or parent['deleted']:
            raise HTTPError(404)
        idx = self.db.node.find({'pId': pid}).count();
        node = {
            'name': name,
            'type': parent['type'],
            'pId': pid,
            'desc': '',
            'deleted': False,
            'index': idx
        }
        node['_id'] = node['id'] = self.db.node.insert(node)
        return node

    def update(self, _id, name):
        node = self.db.node.find_one(_id)
        if not node:
            raise HTTPError(404)
        self.db.node.update({
            '_id': _id,
            'name': name,
        })

#!/usr/bin/env python
# encoding: utf-8


def get_routes():
    routes = [
        (r'/first', 'controller.first.FirstHandler'),
        (r'/tree', 'controller.ztree.TreeHandler'),
        (r'/tree/(\w+)', 'controller.ztree.TreeHandler'),
        (r'/tree/node/(\w+)', 'controller.ztree.TreeNodeHandler'),
        (r'/tree/search/(\w+)', 'controller.ztree.SearchNodeHandler')
    ]
    return routes

# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import logging
import pytest
from django.core.urlresolvers import reverse
from demo.utils import user_grant_permission

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("action", ['export_as_csv', 'export_as_xls', 'merge',
                                    'export_as_fixture', 'export_delete_tree',
                                    'graph_queryset', 'mass_update'])
@pytest.mark.django_db
def test_permission_needed(app, admin, demomodels, action):
    permission_mapping = {'export_as_csv': 'adminactions_export',
                          'export_as_fixture': 'adminactions_export',
                          'export_as_xls': 'adminactions_export',
                          'export_delete_tree': 'adminactions_export',
                          'mass_update': 'adminactions_massupdate',
                          'merge': 'adminactions_merge',
                          'graph_queryset': 'adminactions_chart',
                          }
    perm = "demo.{}_demomodel".format(permission_mapping[action])
    url = reverse('admin:demo_demomodel_changelist')
    pks = [demomodels[0].pk, demomodels[1].pk]
    with user_grant_permission(admin, ['demo.change_demomodel']):
        res = app.post(url, [('action', action),
                             ('_selected_action', pks)],
                       extra_environ={'wsgi.url_scheme': 'https'},
                       user=admin.username,
                       expect_errors=True)
        assert res.status_code == 302
        res = res.follow()
        assert 'Sorry you do not have rights to execute this action' in [str(m) for m in res.context['messages']]

        with user_grant_permission(admin, [perm]):
            res = app.post(url, [('action', action),
                                 ('_selected_action', pks)],
                           extra_environ={'wsgi.url_scheme': 'https'},
                           user=admin.username,
                           expect_errors=True)
            assert res.status_code == 200

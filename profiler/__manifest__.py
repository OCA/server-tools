{
    'name': "profiler",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'category': 'Tests',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ["document"],
    'data': [
        'security/ir.model.access.csv',
        'views/profiler_profile_view.xml',
    ],
    'post_load': 'post_load',
    'installable': True,
}

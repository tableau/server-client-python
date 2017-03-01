class AccessPermissions(object):
    class Mode(object):
        Allow = 'Allow'
        Deny = 'Deny'

    class _Base_Permssions(object):
        Read = 'Read'
        Write = 'Write'

    class Workbook(_Base_Permssions):
        AddComment = 'AddComment'
        ChangeHierarchy = 'ChangeHierarchy'
        ChangePermissions = 'ChangePermissions'
        Delete = 'Delete'
        ExportData = 'ExportData'
        ExportImage = 'ExportImage'
        ExportXml = 'ExportXml'
        Filter = 'Filter'
        ShareView = 'ShareView'
        ViewComments = 'ViewComments'
        ViewUnderlyingData = 'ViewUnderlyingData'
        WebAuthoring = 'WebAuthoring'


    class Datasource(_Base_Permssions):
        ChangePermissions = 'ChangePermissions'
        Connect = 'Connect'
        Delete = 'Delete'
        ExportXml = 'ExportXml'


    class Project(_Base_Permssions):
        ProjectLeader = 'ProjectLeader'

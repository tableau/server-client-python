from tableauserverclient import *

# TODO why aren't these available in the tsc namespace? Probably a bug.
from tableauserverclient.models import (
    DataAccelerationReportItem,
    Credentials,
    ServerInfoItem,
    Resource,
    TableauItem,
)


def get_unimplemented_models():
    return [
        # these items should have repr , please fix
        CollectionItem,
        DQWItem,
        ExtensionsServer,
        ExtensionsSiteSettings,
        FileuploadItem,
        FlowRunItem,
        LinkedTaskFlowRunItem,
        LinkedTaskItem,
        LinkedTaskStepItem,
        SafeExtension,
        # these should be implemented together for consistency
        CSVRequestOptions,
        ExcelRequestOptions,
        ImageRequestOptions,
        PDFRequestOptions,
        PPTXRequestOptions,
        RequestOptions,
        # these don't need it
        FavoriteItem,  # no repr because there is no state
        Resource,  # list of type names
        TableauItem,  # should be an interface
    ]

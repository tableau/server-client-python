import tableauserverclient as TSC
from tableauserverclient.models.reference_item import ResourceReference


def test_and() -> None:
    grantee = ResourceReference("a", "user")
    rule1 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )
    rule2 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )

    composite = rule1 & rule2

    assert composite.capabilities.get(TSC.Permission.Capability.ExportData) == TSC.Permission.Mode.Allow
    assert composite.capabilities.get(TSC.Permission.Capability.Delete) == TSC.Permission.Mode.Deny
    assert composite.capabilities.get(TSC.Permission.Capability.ViewComments) == None
    assert composite.capabilities.get(TSC.Permission.Capability.ExportXml) == TSC.Permission.Mode.Deny


def test_or() -> None:
    grantee = ResourceReference("a", "user")
    rule1 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )
    rule2 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )

    composite = rule1 | rule2

    assert composite.capabilities.get(TSC.Permission.Capability.ExportData) == TSC.Permission.Mode.Allow
    assert composite.capabilities.get(TSC.Permission.Capability.Delete) == TSC.Permission.Mode.Allow
    assert composite.capabilities.get(TSC.Permission.Capability.ViewComments) == TSC.Permission.Mode.Allow
    assert composite.capabilities.get(TSC.Permission.Capability.ExportXml) == TSC.Permission.Mode.Deny


def test_eq_false() -> None:
    grantee = ResourceReference("a", "user")
    rule1 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )
    rule2 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )

    assert rule1 != rule2


def test_eq_true() -> None:
    grantee = ResourceReference("a", "user")
    rule1 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )
    rule2 = TSC.PermissionsRule(
        grantee,
        {
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny,
        },
    )
    assert rule1 == rule2

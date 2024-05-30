import unittest

import tableauserverclient as TSC
from tableauserverclient.models.reference_item import ResourceReference


class TestPermissionsRules(unittest.TestCase):
    def test_and(self):
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

        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.ExportData), TSC.Permission.Mode.Allow)
        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.Delete), TSC.Permission.Mode.Deny)
        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.ViewComments), None)
        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.ExportXml), TSC.Permission.Mode.Deny)

    def test_or(self):
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

        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.ExportData), TSC.Permission.Mode.Allow)
        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.Delete), TSC.Permission.Mode.Allow)
        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.ViewComments), TSC.Permission.Mode.Allow)
        self.assertEqual(composite.capabilities.get(TSC.Permission.Capability.ExportXml), TSC.Permission.Mode.Deny)

    def test_eq_false(self):
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

        self.assertNotEqual(rule1, rule2)

    def test_eq_true(self):
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
        self.assertEqual(rule1, rule2)

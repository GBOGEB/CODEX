"""Native workbook state must contribute to the semantic release identity."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "native_manifest_test", ROOT / "07_ops/qps_roundtrip/Get-QpsSemanticManifest.py"
)
manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest)


def fixture(
    path,
    *,
    criterion="Open",
    state="hidden",
    calc="1",
    scope="0",
    name_hidden="1",
    hidden_row="1",
    formula_aca="0",
    formula_ca=None,
    sort_descending=None,
    duplicate=False,
    sort_custom_list=None,
    table_criterion=None,
    table_blank="0",
    table_descending="0",
):
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    name = f'<definedName name="_xlnm._FilterDatabase" localSheetId="{scope}" hidden="{name_hidden}">Data!$A$1:$B$3</definedName>'
    members = {
        "xl/workbook.xml": f'<workbook xmlns="{main}" xmlns:r="{rel}"><sheets><sheet name="Data" r:id="rId1"/><sheet name="Support" state="{state}" r:id="rId2"/></sheets><definedNames>{name}{name if duplicate else ""}</definedNames><calcPr forceFullCalc="{calc}"/></workbook>',
        "xl/_rels/workbook.xml.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet2.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{main}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Status</t></is></c></row><row r="2" hidden="{hidden_row}"><c r="B2"><f aca="{formula_aca}">1+1</f><v>2</v></c></row></sheetData><autoFilter ref="A1:B3"><filterColumn colId="0"><filters><filter val="{criterion}"/></filters></filterColumn></autoFilter></worksheet>',
        "xl/worksheets/sheet2.xml": f'<worksheet xmlns="{main}"><sheetData/></worksheet>',
    }
    if sort_custom_list is not None:
        key = "xl/worksheets/sheet1.xml"
        members[key] = members[key].replace(
            "</autoFilter>",
            f'<sortState ref="A2:B3"><sortCondition ref="A2:A3" customList="{sort_custom_list}"/></sortState></autoFilter>',
        )
    if table_criterion is not None:
        key = "xl/worksheets/sheet1.xml"
        members[key] = (
            members[key]
            .replace("<worksheet xmlns=", f'<worksheet xmlns:r="{rel}" xmlns=')
            .replace(
                "</worksheet>",
                '<tableParts count="1"><tablePart r:id="table1"/></tableParts></worksheet>',
            )
        )
        members["xl/worksheets/_rels/sheet1.xml.rels"] = (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="table1" Type="{rel}/table" Target="../tables/table1.xml"/>'
            "</Relationships>"
        )
        members["xl/tables/table1.xml"] = (
            f'<table xmlns="{main}" id="1" name="StatusTable" displayName="StatusTable" '
            f'ref="A1:B3"><autoFilter ref="A1:B3"><filterColumn colId="0">'
            f'<filters blank="{table_blank}"><filter val="{table_criterion}"/></filters></filterColumn>'
            f'</autoFilter><sortState ref="A2:B3"><sortCondition ref="A2:A3" descending="{table_descending}"/>'
            '</sortState><tableColumns count="2"><tableColumn id="1" name="Status"/>'
            '<tableColumn id="2" name="Value"/></tableColumns></table>'
        )
    if formula_ca is not None:
        key = "xl/worksheets/sheet1.xml"
        members[key] = members[key].replace("<f aca=", f'<f ca="{formula_ca}" aca=')
    if sort_descending is not None:
        key = "xl/worksheets/sheet1.xml"
        members[key] = members[key].replace(
            "</autoFilter>",
            '<sortState ref="A2:B3"><sortCondition ref="A2:A3" '
            f'descending="{sort_descending}"/></sortState></autoFilter>',
        )
    with zipfile.ZipFile(path, "w") as package:
        for key, value in members.items():
            package.writestr(key, value)


class NativeManifestTests(unittest.TestCase):
    def test_table_filter_change_changes_identity_with_same_cells_and_range(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = (
                Path(directory) / "open.xlsx",
                Path(directory) / "closed.xlsx",
            )
            fixture(first, table_criterion="Open")
            fixture(second, table_criterion="Closed")
            before, after = manifest.build(first), manifest.build(second)
            self.assertEqual(
                before["table_names_and_ranges"], after["table_names_and_ranges"]
            )
            self.assertEqual(
                before["normalized_formula_map"], after["normalized_formula_map"]
            )
            self.assertEqual(
                before["normalized_value_map_for_controlled_cells"],
                after["normalized_value_map_for_controlled_cells"],
            )
            self.assertNotEqual(
                before["native_feature_contract"]["table_filters"],
                after["native_feature_contract"]["table_filters"],
            )
            self.assertNotEqual(before["semantic_sha256"], after["semantic_sha256"])

    def test_table_filter_and_sort_booleans_normalize_without_losing_difference(self):
        with tempfile.TemporaryDirectory() as directory:
            values = []
            for boolean in ("1", "true", "false"):
                path = Path(directory) / (boolean + ".xlsx")
                fixture(
                    path,
                    table_criterion="Open",
                    table_blank=boolean,
                    table_descending=boolean,
                )
                values.append(manifest.build(path))
            self.assertEqual(values[0]["semantic_sha256"], values[1]["semantic_sha256"])
            self.assertNotEqual(
                values[0]["semantic_sha256"], values[2]["semantic_sha256"]
            )

    def test_formula_and_sort_booleans_normalize_without_merging_meanings(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second, different = (
                Path(directory) / name
                for name in ("one.xlsx", "true.xlsx", "false.xlsx")
            )
            fixture(first, formula_aca="1", formula_ca="1", sort_descending="1")
            fixture(
                second, formula_aca="true", formula_ca="true", sort_descending="true"
            )
            fixture(
                different,
                formula_aca="false",
                formula_ca="false",
                sort_descending="false",
            )
            a, b, c = (manifest.build(p) for p in (first, second, different))
            self.assertEqual(a["semantic_sha256"], b["semantic_sha256"])
            self.assertEqual(a["native_feature_contract"], b["native_feature_contract"])
            self.assertNotEqual(a["semantic_sha256"], c["semantic_sha256"])
            self.assertEqual(
                a["native_feature_contract"]["schema"], "codex-xlsx-native-features/v2"
            )

    def test_sort_custom_list_keeps_string_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = (
                Path(directory) / "first.xlsx",
                Path(directory) / "second.xlsx",
            )
            fixture(first, sort_custom_list="1")
            fixture(second, sort_custom_list="true")
            before, after = manifest.build(first), manifest.build(second)
            self.assertNotEqual(before["semantic_sha256"], after["semantic_sha256"])
            self.assertNotEqual(
                before["native_feature_contract"], after["native_feature_contract"]
            )

    def test_duplicate_scoped_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.xlsx"
            fixture(path, duplicate=True)
            with self.assertRaisesRegex(ValueError, "DUPLICATE_SCOPED_DEFINED_NAME"):
                manifest.build(path)

    def test_invalid_scope_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scope.xlsx"
            fixture(path, scope="99")
            with self.assertRaisesRegex(ValueError, "DEFINED_NAME_WITH_INVALID_SCOPE"):
                manifest.build(path)


def compare_variant(**change):
    def method(self):
        with tempfile.TemporaryDirectory() as directory:
            source, changed = (
                Path(directory) / "source.xlsx",
                Path(directory) / "changed.xlsx",
            )
            fixture(source)
            fixture(changed, **change)
            before, after = manifest.build(source), manifest.build(changed)
            self.assertEqual(
                before["normalized_formula_map"], after["normalized_formula_map"]
            )
            self.assertEqual(
                before["normalized_value_map_for_controlled_cells"],
                after["normalized_value_map_for_controlled_cells"],
            )
            self.assertNotEqual(before["semantic_sha256"], after["semantic_sha256"])
            self.assertNotEqual(
                before["native_feature_contract"], after["native_feature_contract"]
            )

    return method


for _field, _value in {
    "criterion": "Closed",
    "state": "visible",
    "calc": "0",
    "scope": "1",
    "name_hidden": "0",
    "hidden_row": "0",
    "formula_aca": "1",
}.items():
    setattr(
        NativeManifestTests,
        "test_changed_" + _field + "_changes_semantic_identity",
        compare_variant(**{_field: _value}),
    )


if __name__ == "__main__":
    unittest.main()

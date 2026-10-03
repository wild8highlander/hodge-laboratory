#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch DOCX footers for WPS compatibility (toc.md rules):

1. Remove empty <w:pgNumType/> from document.xml (cover section artifact).
2. Add explicit format switches to footer PAGE fields:
   - footer referenced by the section with pgNumType fmt="upperRoman" -> PAGE \\* ROMAN
   - footer referenced by the section with pgNumType fmt="decimal"    -> PAGE \\* arabic

Usage: python3 patch_docx_footers.py file.docx [file2.docx ...]
"""
import re
import shutil
import sys
import tempfile
import zipfile
import os


def patch(path):
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(path) as z:
            z.extractall(tmpdir)

        doc_path = os.path.join(tmpdir, 'word', 'document.xml')
        with open(doc_path, encoding='utf-8') as f:
            doc = f.read()

        # 1. drop empty pgNumType
        doc, n_removed = re.subn(r'<w:pgNumType/>', '', doc)

        # 2. map sectPr fmt -> footer rIds
        rels_path = os.path.join(tmpdir, 'word', '_rels', 'document.xml.rels')
        with open(rels_path, encoding='utf-8') as f:
            rels = f.read()
        rid_target = dict(re.findall(r'<Relationship[^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels))

        roman_targets, arabic_targets = set(), set()
        for sect in re.findall(r'<w:sectPr.*?</w:sectPr>', doc, flags=re.S):
            fmt = re.search(r'<w:pgNumType[^>]*w:fmt="([^"]+)"', sect)
            if not fmt:
                continue
            for rid in re.findall(r'<w:footerReference[^>]*r:id="([^"]+)"', sect):
                target = rid_target.get(rid, '')
                if target.startswith('footer'):
                    if fmt.group(1) == 'upperRoman':
                        roman_targets.add(target)
                    elif fmt.group(1) in ('decimal', 'lowerRoman', 'numberInDash'):
                        arabic_targets.add(target)

        def patch_footer(fname, switch):
            fpath = os.path.join(tmpdir, 'word', os.path.basename(fname))
            if not os.path.exists(fpath):
                return False
            with open(fpath, encoding='utf-8') as f:
                xml = f.read()
            xml2, n = re.subn(
                r'(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)',
                r'\g<1> PAGE \\* %s \\* MERGEFORMAT \g<2>' % switch,
                xml)
            if n:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(xml2)
            return bool(n)

        patched = []
        for t in roman_targets:
            if patch_footer(t, 'ROMAN'):
                patched.append((t, 'ROMAN'))
        for t in arabic_targets:
            if patch_footer(t, 'arabic'):
                patched.append((t, 'arabic'))

        if n_removed or patched:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc)

        # rezip
        newpath = path + '.tmp'
        with zipfile.ZipFile(newpath, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(tmpdir):
                for fn in files:
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, tmpdir)
                    z.write(full, arc)
        shutil.move(newpath, path)
        return n_removed, patched
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        n, patched = patch(p)
        print('%s: pgNumType removed=%d, footers patched=%s'
              % (os.path.basename(p), n, patched or 'none'))

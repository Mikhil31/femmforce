"""
Insert the FemmForce logo at the top of the content document.

python-docx is not available, so this edits the OOXML package directly: add the
image to word/media, register a relationship for it, and splice a paragraph pair
("Logo:" plus the picture) in at the start of the body.

The original is copied to *.backup.docx before anything is written.

    python add_logo_to_docx.py
"""
import os
import re
import shutil
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
DOCX = os.path.join(PROJECT, "FemmForce-Website-Content.docx")
IMAGE = os.path.join(HERE, "png", "lockup-vertical-onwhite.png")

EMU_PER_INCH = 914400
TARGET_WIDTH_IN = 2.3
MEDIA_NAME = "femmforce-logo.png"
REL_ID = "rIdFemmForceLogo"

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"


def drawing_xml(cx, cy):
    return (
        '<w:p><w:pPr><w:spacing w:before="120" w:after="60"/></w:pPr>'
        '<w:r><w:rPr><w:b/><w:sz w:val="24"/></w:rPr>'
        '<w:t xml:space="preserve">Logo:</w:t></w:r></w:p>'
        '<w:p><w:pPr><w:spacing w:after="240"/></w:pPr><w:r><w:drawing>'
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        '<wp:extent cx="%d" cy="%d"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        '<wp:docPr id="1001" name="FemmForce logo"/>'
        '<wp:cNvGraphicFramePr>'
        '<a:graphicFrameLocks xmlns:a="%s" noChangeAspect="1"/>'
        '</wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="%s">'
        '<a:graphicData uri="%s">'
        '<pic:pic xmlns:pic="%s">'
        '<pic:nvPicPr><pic:cNvPr id="1001" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
        % (cx, cy, A_NS, A_NS, PIC_NS, PIC_NS, MEDIA_NAME, REL_ID, cx, cy)
    )


def main():
    if not os.path.exists(DOCX):
        raise SystemExit("not found: %s" % DOCX)
    if not os.path.exists(IMAGE):
        raise SystemExit("not found: %s -- run build_assets.py first" % IMAGE)

    with Image.open(IMAGE) as im:
        iw, ih = im.size
    cx = int(TARGET_WIDTH_IN * EMU_PER_INCH)
    cy = int(cx * ih / iw)

    backup = DOCX.replace(".docx", ".backup.docx")
    if not os.path.exists(backup):
        shutil.copy2(DOCX, backup)
        print("backup written:", os.path.basename(backup))

    zin = zipfile.ZipFile(DOCX)
    entries = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    doc = entries["word/document.xml"].decode("utf8")
    if REL_ID in doc:
        print("logo already present; nothing to do")
        return

    # relationship for the image
    rels_path = "word/_rels/document.xml.rels"
    rels = entries[rels_path].decode("utf8")
    rel = ('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/'
           'officeDocument/2006/relationships/image" Target="media/%s"/>'
           % (REL_ID, MEDIA_NAME))
    entries[rels_path] = rels.replace("</Relationships>", rel + "</Relationships>").encode("utf8")

    # png is already declared in [Content_Types].xml for this package, but add it
    # if a future export drops the default
    ct = entries["[Content_Types].xml"].decode("utf8")
    if 'Extension="png"' not in ct:
        ct = ct.replace("</Types>",
                        '<Default Extension="png" ContentType="image/png"/></Types>')
        entries["[Content_Types].xml"] = ct.encode("utf8")

    entries["word/media/" + MEDIA_NAME] = open(IMAGE, "rb").read()

    m = re.search(r"<w:body>", doc)
    if not m:
        raise SystemExit("no <w:body> in document.xml")
    doc = doc[:m.end()] + drawing_xml(cx, cy) + doc[m.end():]
    entries["word/document.xml"] = doc.encode("utf8")

    with zipfile.ZipFile(DOCX, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            if not name.endswith("/"):
                zout.writestr(name, data)

    print("inserted logo at %.1f in wide (%d x %d EMU) into %s"
          % (TARGET_WIDTH_IN, cx, cy, os.path.basename(DOCX)))


if __name__ == "__main__":
    main()

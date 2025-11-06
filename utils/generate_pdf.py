import os
from docx2pdf import convert
from docx import Document


def generation_pdf(adh):
    doc = Document(f"{os.getcwd()}\\modele\\recu_don_modele.docx")
    Dictionary = {
        "recu_num": "test",
        "nom_adherent": "Boucher"
    }
    for i in Dictionary:
        for p in doc.paragraphs:
            if p.text.find(i) >= 0:
                p.text = p.text.replace(i, Dictionary[i])
    # save changed document
    doc.save(f"{os.getcwd()}\\modele\\test_recu_don_modele.docx")
    convert(f"{os.getcwd()}\\modele\\test_recu_don_modele.docx", f"{os.getcwd()}\\modele\\test_recu_don_modele.pdf")

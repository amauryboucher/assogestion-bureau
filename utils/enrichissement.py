from loguru import logger

from utils.models import assogestion_annuaire


def controle_enrichissement_ville(self):
    s = self.Session()
    self.cb_ville.setEditable(False)
    try:
        self.cb_ville.clear()
        if self.cp_edit.text() != "" and len(self.cp_edit.text()) == 5:
            res = s.query(assogestion_annuaire).filter_by(cp=self.cp_edit.text()).order_by(assogestion_annuaire.ville).all()
            for r in res:
                self.cb_ville.addItem(r.ville.upper())
            self.label_error_ville.setText(f"{len(res)} ville(s) trouvée(s)")
    except Exception as err:
        logger.error(err)
    finally:
        s.close()
import re


def coll_ctrl_001(self):
    if self.cb_titre.currentText() == "":
        return "COLL_CTRL_001"
    else:
        return ""


def coll_ctrl_002(self):
    if self.rs_edit.text() == "":
        return "COLL_CTRL_002"
    else:
        return ""


def coll_ctrl_003(self):
    if self.adresse_edit.text() == "":
        return "COLL_CTRL_003"
    else:
        return ""


def coll_ctrl_004(self):
    if self.cp_edit.text() == "":
        return "COLL_CTRL_004"
    else:
        return ""


def coll_ctrl_005(self):
    if self.cb_ville.currentText() == "":
        return "COLL_CTRL_005"
    else:
        return ""


def coll_ctrl_006(self):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if self.email_edit.text() != "":
        if re.match(pat, self.email_edit.text()):
            return ""
        else:
            return "COLL_CTRL_006"
    else:
        return ""
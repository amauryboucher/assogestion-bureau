import re


def CM_DEV_001(self):
    if self.rs_edit.text() == "":
        return "CM_DEV_001"
    else:
        return ""


def CM_DEV_002(self):
    if self.add_edit.text() == "":
        return "CM_DEV_002"
    else:
        return ""


def CM_DEV_003(self):
    if self.cp_edit.text() == "":
        return "CM_DEV_003"
    else:
        return ""


def CM_DEV_004(self):
    if self.cb_ville.currentText() == "":
        return "CM_DEV_004"
    else:
        return ""


def CM_DEV_005(self):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if self.mail_edit.text() != "":
        if re.match(pat, self.mail_edit.text()):
            return ""
        else:
            return "CM_DEV_005"
    else:
        return ""


def CM_DEV_006(self):
    if self.cb_client.currentText() == "":
        return "CM_DEV_006"
    else:
        return ""


def CM_DEV_007(base):
    if base == 0.00:
        return "CM_DEV_007"
    else:
        return ""
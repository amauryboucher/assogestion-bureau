def adh_act_001(self):
    new_nb = int(self.nb_edit.text()) + self.act.nb_participant_activite
    nb_max = self.act.nb_participant_max_activite
    if new_nb > nb_max:
        return "ADH_ACT_001"
    else:
        return ""

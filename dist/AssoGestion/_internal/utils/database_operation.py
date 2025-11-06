from loguru import logger

from utils.models import assogestion_adherents, assogestion_operations, assogestion_cotisation, assogestion_adh_dons


def insert_adherent_to_database(s, i, ligne):
    code_adherent, titre_adherent, nom_adherent, prenom_adherent, adresse_adherent, adresse_2_adherent, cp_adherent, ville_adherent, tel_adherent, email_adherent = ligne
    s = s()
    try:
        res = s.query(assogestion_adherents).filter_by(code_adherent=code_adherent).first()
        if res:
            pass
        else:
            new_res = assogestion_adherents(
                code_adherent=code_adherent,
                titre_adherent=titre_adherent,
                nom_adherent=nom_adherent,
                prenom_adherent=prenom_adherent,
                adresse_adherent=adresse_adherent,
                adresse_comp_adherent=adresse_2_adherent,
                cp_adherent=cp_adherent,
                ville_adherent=ville_adherent,
                telephone_adherent=tel_adherent,
                email_adherent=email_adherent
            )
            s.add(new_res)
            s.commit()
        return ""
    except Exception as err:
        logger.error(err)
        return f"{i} - erreur d'insertion de la ligne"
    finally:
        s.close()

def import_operation_to_database(s, ligne):
    cle, nom_complet, montant = ligne
    s = s()
    try:
        new_op = assogestion_operations(
            cle = cle,
            nom_complet = nom_complet,
            montant = float(montant)
        )
        s.add(new_op)
        s.commit()
        return ""
    except Exception as err:
        return str(err)
    finally:
        s.close()


def rapprochement_adherent_operation(s):
    s = s()
    liste_operation = []
    liste_operation_check=[]
    try:
        res_adh = s.query(assogestion_adherents).order_by(assogestion_adherents.code_adherent).all()
        for adh in res_adh:
            filtre = f"{adh.titre_adherent} {adh.nom_adherent} {adh.prenom_adherent}"
            res_operation = s.query(assogestion_operations).filter_by(nom_complet=filtre).all()
            if res_operation:
                for r in res_operation:
                    res_cot = s.query(assogestion_cotisation).all()
                    for rc in res_cot:
                        if rc.tarif + rc.dons == r.montant:
                            logger.info(f"{r.nom_complet} - {r.montant} - {rc.nom_cotisation}")
                            res_adh_cot = s.query(assogestion_adh_dons).filter_by(code_adherent=adh.code_adherent, date_debut_adh_don=rc.date_debut_cotisation).first()
                            if res_adh_cot:
                                logger.info("Ajout du complément en dons")
                                new_adh_dons = assogestion_adh_dons(
                                    code_adherent=adh.code_adherent,
                                    id_cotisation=18,
                                    montant_adh=0,
                                    montant_bulletin=0,
                                    montant_dons=r.montant,
                                    date_debut_adh_don=rc.date_debut_cotisation,
                                    date_fin_adh_don=rc.date_fin_cotisation
                                )
                                s.add(new_adh_dons)
                                s.commit()
                            else:
                                logger.info("Ajout de la cotisation de base")
                                new_adh_dons = assogestion_adh_dons(
                                    code_adherent=adh.code_adherent,
                                    id_cotisation = rc.id_cotisation,
                                    montant_adh = rc.tarif,
                                    montant_bulletin = rc.tarif_bulletin,
                                    montant_dons = rc.dons,
                                    date_debut_adh_don = rc.date_debut_cotisation,
                                    date_fin_adh_don = rc.date_fin_cotisation
                                )
                                s.add(new_adh_dons)
                                s.commit()
    except Exception as err:
        logger.error(err)
    finally:
        s.close()
from sqlalchemy import Column, String, Boolean, Integer, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class assogestion_app_param(Base):
    __tablename__ =  "assogestion_app_param"
    id_param = Column(Integer, primary_key=True, autoincrement=True)
    name_param = Column(String)
    value_param = Column(String)

class assogestion_users(Base):
    __tablename__ = "assogestion_users"
    email = Column(String, primary_key=True)
    username = Column(String)
    password = Column(String)
    actif = Column(Boolean)
    locked = Column(Boolean)
    adherents = Column(Boolean)
    activites = Column(Boolean)
    cotisations = Column(Boolean)
    devis_facture = Column(Boolean)
    utilisateurs = Column(Boolean)


class assogestion_adherents(Base):
    __tablename__ = "assogestion_adherents"
    code_adherent = Column(Integer, primary_key=True)
    titre_adherent = Column(String)
    fonction_adherent = Column(String)
    nom_adherent = Column(String)
    prenom_adherent = Column(String)
    adresse_adherent = Column(String)
    adresse_comp_adherent = Column(String)
    cp_adherent = Column(String)
    ville_adherent = Column(String)
    email_adherent = Column(String)
    telephone_adherent = Column(String)
    adherent_date_naissance = Column(Date)
    adherent_date_prospection = Column(Date)
    adherent_date_adhesion = Column(Date)
    adherent_moyen_paiement = Column(String)
    adherent_commentaire = Column(String)
    adherent_type = Column(String, default="Membre")
    adherent_categorie = Column(String, default="")
    locked = Column(Boolean, default=False)
    locked_by = Column(String)
    edited_by = Column(String)
    adherent_bulletin = Column(Boolean)


class assogestion_collectivite(Base):
    __tablename__ = "assogestion_collectivite"
    code_collectivite = Column(Integer, primary_key=True)
    titre_collectivite = Column(String)
    raison_sociale_collectivite = Column(String)
    contact_collectivite = Column(String)
    adresse_collectivite = Column(String)
    adresse_comp_collectivite = Column(String)
    cp_collectivite = Column(String)
    ville_collectivite = Column(String)
    email_collectivite = Column(String)
    telephone_collectivite = Column(String)
    date_prospection_collectivite = Column(Date)
    commentaire_collectivite = Column(String)
    categorie_collectivite = Column(String, default="Collectivité")
    locked = Column(Boolean, default=False)
    locked_by = Column(String)
    edited_by = Column(String)
    collectivite_bulletin = Column(Boolean)

class assogestion_collectivite_paiement(Base):
    __tablename__ = "assogestion_collectivite_paiement"
    id_paiement = Column(Integer, autoincrement=True, primary_key=True)
    code_collectivite = Column(Integer, ForeignKey('assogestion_collectivite.code_collectivite'))
    date_paiement = Column(Date)
    montant_paiement = Column(Float)


class assogestion_type_import(Base):
    __tablename__ = "assogestion_type_import"
    code_import = Column(Integer, primary_key=True)
    nom_import = Column(String)
    nommage_import = Column(String)


class assogestion_titre(Base):
    __tablename__ = "assogestion_titre"
    code_titre = Column(Integer, primary_key=True)
    nom_titre = Column(String)
    adherent = Column(Boolean)


class assogestion_cotisation(Base):
    __tablename__ = "assogestion_cotisation"
    id_cotisation = Column(Integer, primary_key=True, autoincrement=True)
    nom_cotisation = Column(String)
    date_debut_cotisation = Column(Date)
    date_fin_cotisation = Column(Date)
    tarif = Column(Float)
    tarif_bulletin = Column(Float)
    dons = Column(Float)
    locked = Column(Boolean, default=False)
    locked_by = Column(String)
    type = Column(String, default="Cotisation")
    bulletin = Column(Boolean)
    migrated = Column(Boolean, default=False)
    migration_status = Column(String, default="NOT_STARTED")


class assogestion_operations(Base):
    __tablename__= "assogestion_operations"
    cle = Column(String, primary_key=True)
    nom_complet = Column(String)
    montant = Column(Float)


class assogestion_adh_dons(Base):
    __tablename__ = "assogestion_adh_dons"
    id_adh_don = Column(Integer, primary_key=True, autoincrement=True)
    code_adherent = Column(Integer, ForeignKey('assogestion_adherents.code_adherent'))
    id_cotisation = Column(Integer, ForeignKey('assogestion_cotisation.id_cotisation'))
    montant_adh = Column(Float)
    montant_bulletin = Column(Float)
    montant_dons = Column(Float)
    date_debut_adh_don = Column(Date)
    date_fin_adh_don = Column(Date)
    export = Column(Boolean)
    date_export = Column(Date)


class assogestion_activite(Base):
    __tablename__ = "assogestion_activite"
    id_activite = Column(Integer, primary_key=True, autoincrement=True)
    libelle_activite = Column(String)
    date_activite = Column(Date)
    nb_participant_activite = Column(Integer)
    nb_participant_max_activite = Column(Integer)
    tarif_activite = Column(Float)
    locked = Column(Boolean)
    locked_by = Column(String)


class assogestion_act_adh(Base):
    __tablename__ = "assogestion_act_adh"
    id_act_adh = Column(Integer, primary_key=True, autoincrement=True)
    code_adherent = Column(Integer, ForeignKey('assogestion_adherents.code_adherent'))
    id_activite = Column(Integer, ForeignKey('assogestion_activite.id_activite'))
    montant = Column(Float)
    nombre = Column(Integer)
    a_payer = Column(Boolean)


class assogestion_client(Base):
    __tablename__ = "assogestion_client"
    id_client = Column(String, primary_key=True)
    raison_sociale = Column(String)
    adresse_client = Column(String)
    adresse_comp_client = Column(String)
    cp_client = Column(String)
    ville_client = Column(String)
    paiement_mode = Column(String)
    mail_client = Column(String)


class assogestion_facture(Base):
    __tablename__ = "assogestion_facture"
    inv_no = Column(Integer, primary_key=True)
    inv_number_full = Column(String, default="FCXXX")
    code_client = Column(String, ForeignKey('assogestion_client.id_client'))
    add_liv = Column(String)
    date = Column(Date)
    date_echeance = Column(Date)
    order_number = Column(String)
    order_date = Column(Date)
    total_ht = Column(Float, default=0.00)
    total_ttc = Column(Float, default=0.00)
    total_a_payer = Column(Float, default=0.00)

class assogestion_ligne_facture(Base):
    __tablename__ = "assogestion_ligne_facture"
    inv_no = Column(Integer, ForeignKey('assogestion_facture.inv_no'))
    id = Column(Integer, primary_key=True, autoincrement=True)
    inv_line_number = Column(Integer)
    code =  Column(String)
    desc = Column(String)
    qty = Column(Integer)
    prix_unitaire = Column(Float)

class assogestion_code_produit(Base):
    __tablename__="assogestion_code_produit"
    id=Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String)
    description = Column(String)
    prix_unitaire = Column(Float)
class assogestion_counter_facture(Base):
    __tablename__="assogestion_counter_facture"
    id=Column(Integer,primary_key=True, autoincrement=True)
    last_invoice_num = Column(Integer, default=1)

class assogestion_infos(Base):
    __tablename__ = "assogestion_infos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    raison_sociale= Column(String)
    adresse=Column(String)
    adresse_comp = Column(String)
    cp = Column(String)
    ville = Column(String)
    tel = Column(String)
    mail = Column(String)
class assogestion_devis(Base):
    __tablename__ = "assogestion_devis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_devis = Column(String)
    code_client = Column(String, ForeignKey('assogestion_client.id_client'))
    date = Column(Date)
    tva_percent = Column(String, default="Exonéré")
    base = Column(Float, default=0.00)
    tva_montant = Column(Float, default=0.00)
    total_ht = Column(Float, default=0.00)
    total_tva = Column(Float, default=0.00)
    total_ttc = Column(Float, default=0.00)
    total_regle = Column(Float, default=0.00)
    total_a_payer = Column(Float, default=0.00)


class assogestion_ligne_devis(Base):
    __tablename__ = "assogestion_ligne_devis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_devis = Column(Integer, ForeignKey('assogestion_devis.id', ondelete='CASCADE', onupdate='CASCADE'))
    code = Column(String, default="code")
    desc = Column(String, default="description")
    qty = Column(Integer, default=0)
    pu_ht = Column(Float, default=0.00)
    total_ht = Column(Float, default=0.00)


class assogestion_annuaire(Base):
    __tablename__="assogestion_annuaire"
    id = Column(Integer,  autoincrement=True, primary_key=True)
    cp = Column(String)
    ville = Column(String)


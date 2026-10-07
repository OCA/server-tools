# Rapport de migration — `auto_backup` vers Odoo 20.0

**Date :** 6 octobre 2026 **Périmètre :** module `auto_backup` uniquement **Objectif :**
déclarer et documenter la version Odoo 20.0 sans modifier le comportement fonctionnel du
module.

## Modifications effectuées

| Fichier                             | Avant                                                                | Après                                                                    |
| ----------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `__manifest__.py` — version         | `19.0.1.0.1`                                                         | `20.0.1.0.0`                                                             |
| `__manifest__.py` — droits chargés  | `security/ir.model.access.csv`                                       | `security/ir.access.csv`                                                 |
| `models/db_backup.py` — API de dump | `from odoo.service import db`, appels `db.dump_db()`                 | `from odoo.modules import db`, appels `db.dump()`                        |
| Droits — fichier                    | `security/ir.model.access.csv` et modèle de droits `ir.model.access` | `security/ir.access.csv` et modèle `ir.access`                           |
| Droits — lecture                    | Gestionnaire ERP : lecture seule (`1,0,0,0`)                         | Même droit (`r`) pour `base.group_erp_manager`                           |
| Droits — administration             | Groupe système : CRUD (`1,1,1,1`)                                    | Même droit (`crud`) pour `base.group_system`                             |
| `README.rst`                        | URLs et version de documentation `19.0`                              | Références de branche, traduction, Runboat et lien de signalement `20.0` |
| `static/description/index.html`     | URLs et version de documentation `19.0`                              | Références correspondantes mises à `20.0`                                |
| `i18n/auto_backup.pot`              | `Odoo Server 19.0`                                                   | `Odoo Server 20.0`                                                       |
| `MIGRATION_20.0.md`                 | Absent                                                               | Présent : compte rendu de migration                                      |

Les autres dépendances, fonctions, vues, données cron et tests restent inchangés.

## Code fonctionnel et comportement

Les changements fonctionnels sont limités aux adaptations d’API et de sécurité requises
par Odoo 20. Les vues XML, les données cron et les tests n’ont pas été modifiés.

Les fonctionnalités existantes restent donc inchangées :

- sauvegardes locales et distantes via SFTP ;
- formats ZIP avec filestore et dump PostgreSQL ;
- planification via l’action cron existante ;
- suppression automatique des anciennes sauvegardes selon la durée configurée ;
- journalisation des succès/échecs dans le chatter et test de connexion SFTP.

## Vérifications réalisées

- Installation du module et tests exécutés avec l’image Docker `odoo:20`, dans un
  conteneur jetable et une base PostgreSQL temporaire distincte des bases de l’instance
  de travail.
- Résultat Odoo 20 : `0 failed, 0 error(s) of 16 tests`. Les 14 tests de `auto_backup`
  ont été exécutés ; 2 tests web de l’environnement ont aussi été comptabilisés par
  Odoo.
- Les tests vérifient notamment la création de sauvegarde ZIP et le nettoyage
  automatique ; les journaux indiquent une sauvegarde et un nettoyage réussis.
- Alerte non bloquante du journal :
  `markdown2 is not installed, markdown will not be rendered` (rendu Markdown du chatter
  désactivé dans l'image de test). Aucun échec ou erreur de test associé.
- Analyse syntaxique Pylance : aucune erreur dans `models/db_backup.py` ni
  `__manifest__.py`.
- Les trois fichiers XML (`data/ir_cron.xml`, `data/mail_message_subtype.xml` et
  `view/db_backup_view.xml`) sont bien formés.
- L’instance Odoo 19 de travail et ses bases n’ont pas été utilisées pour le test.

## Limite de validation

Le test a été réalisé sur la dernière image Docker locale `odoo:20` et non sur une
instance Odoo 20 de production. Les tests unitaires du module passent dans cet
environnement isolé.

Au moment de la migration, la branche amont OCA `20.0` ne publie pas encore le
répertoire `auto_backup`. Les liens de branche et de traduction ont été préparés pour la
cible 20.0 ; ils pourront rester indisponibles jusqu’à la publication amont
correspondante.

## Fichiers hors périmètre

Aucun autre module, aucune base de l’instance Odoo 19 et aucun fichier de configuration
du dépôt n’ont été modifiés pour cette migration. La base et le conteneur PostgreSQL
temporaires du test ont été supprimés après vérification.

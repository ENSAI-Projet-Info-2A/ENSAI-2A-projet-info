from src.business_object.statistiques import Statistiques

class TestStatistiques:
    """Suite complète de tests pour la classe Statistiques"""
    
    # ========== Tests d'initialisation ==========
    
    def test_init_valeurs_par_defaut(self):
        """Teste l'initialisation avec les valeurs par défaut"""
        # GIVEN: Aucune valeur fournie
        
        # WHEN: On crée une instance de Statistiques
        stats = Statistiques()
        
        # THEN: Tous les attributs doivent avoir leurs valeurs par défaut
        assert stats.nb_conversations == 0
        assert stats.nb_messages == 0
        assert stats.heures_utilisation == 0.0
        assert stats.sujets_plus_frequents == []
        assert len(stats._sujet_counts) == 0

    def test_init_avec_valeurs(self):
        """Teste l'initialisation avec des valeurs spécifiques"""
        # GIVEN: Des valeurs numériques spécifiques
        nb_conv = 10
        nb_msg = 50
        heures = 2.5
        
        # WHEN: On crée une instance avec ces valeurs
        stats = Statistiques(
            nb_conversations=nb_conv,
            nb_messages=nb_msg,
            heures_utilisation=heures
        )
        
        # THEN: Les attributs doivent correspondre aux valeurs fournies
        assert stats.nb_conversations == 10
        assert stats.nb_messages == 50
        assert stats.heures_utilisation == 2.5

    def test_init_avec_sujets(self):
        """Teste l'initialisation avec une liste de sujets"""
        # GIVEN: Une liste de sujets avec doublons
        sujets = ["Python", "Django", "Python", "Flask"]
        
        # WHEN: On crée une instance avec ces sujets
        stats = Statistiques(sujets_plus_frequents=sujets)
        
        # THEN: Les sujets doivent être comptabilisés correctement
        assert "Python" in stats.sujets_plus_frequents
        assert "Django" in stats.sujets_plus_frequents
        assert stats._sujet_counts["Python"] == 2

    def test_init_conversion_types(self):
        """Teste la conversion automatique des types"""
        # GIVEN: Des valeurs sous forme de chaînes de caractères
        
        # WHEN: On crée une instance avec ces chaînes
        stats = Statistiques(
            nb_conversations="5",
            nb_messages="10",
            heures_utilisation="3.7"
        )
        
        # THEN: Les valeurs doivent être converties dans les bons types
        assert stats.nb_conversations == 5
        assert stats.nb_messages == 10
        assert stats.heures_utilisation == 3.7

    # ========== Tests d'incrémentation ==========
    
    def test_incrementer_conversations_defaut(self):
        """Teste l'incrémentation par défaut (1)"""
        # GIVEN: Une instance avec 5 conversations
        stats = Statistiques(nb_conversations=5)
        
        # WHEN: On incrémente sans préciser de valeur
        stats.incrementer_conversations()
        
        # THEN: Le nombre doit augmenter de 1
        assert stats.nb_conversations == 6

    def test_incrementer_conversations_valeur(self):
        """Teste l'incrémentation avec une valeur spécifique"""
        # GIVEN: Une instance avec 5 conversations
        stats = Statistiques(nb_conversations=5)
        
        # WHEN: On incrémente de 10
        stats.incrementer_conversations(10)
        
        # THEN: Le nombre doit augmenter de 10
        assert stats.nb_conversations == 15

    def test_incrementer_messages_defaut(self):
        """Teste l'incrémentation des messages par défaut"""
        # GIVEN: Une instance avec 20 messages
        stats = Statistiques(nb_messages=20)
        
        # WHEN: On incrémente sans préciser de valeur
        stats.incrementer_messages()
        
        # THEN: Le nombre doit augmenter de 1
        assert stats.nb_messages == 21

    def test_incrementer_messages_valeur(self):
        """Teste l'incrémentation des messages avec valeur"""
        # GIVEN: Une instance avec 20 messages
        stats = Statistiques(nb_messages=20)
        
        # WHEN: On incrémente de 5
        stats.incrementer_messages(5)
        
        # THEN: Le nombre doit augmenter de 5
        assert stats.nb_messages == 25

    def test_ajouter_temps(self):
        """Teste l'ajout de temps"""
        # GIVEN: Une instance avec 1.5 heures
        stats = Statistiques(heures_utilisation=1.5)
        
        # WHEN: On ajoute 2.5 heures
        stats.ajouter_temps(2.5)
        
        # THEN: Le total doit être 4.0 heures
        assert stats.heures_utilisation == 4.0

    def test_ajouter_temps_multiples(self):
        """Teste plusieurs ajouts de temps"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute plusieurs fois du temps
        stats.ajouter_temps(1.0)
        stats.ajouter_temps(0.5)
        stats.ajouter_temps(2.25)
        
        # THEN: Le total doit être la somme de tous les ajouts
        assert stats.heures_utilisation == 3.75

    # ========== Tests de gestion des sujets ==========
    
    def test_ajouter_sujets_simple(self):
        """Teste l'ajout de sujets simples"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute 3 sujets distincts
        stats.ajouter_sujets(["Python", "Java", "C++"])
        
        # THEN: Les 3 sujets doivent être présents
        assert len(stats.sujets_plus_frequents) == 3
        assert "Python" in stats.sujets_plus_frequents

    def test_ajouter_sujets_doublons(self):
        """Teste l'ajout de sujets avec doublons"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute des sujets avec doublons
        stats.ajouter_sujets(["Python", "Python", "Java", "Python"])
        
        # THEN: Les occurrences doivent être comptées correctement
        assert stats._sujet_counts["Python"] == 3
        assert stats._sujet_counts["Java"] == 1

    def test_ajouter_sujets_avec_espaces(self):
        """Teste le nettoyage des espaces"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute des sujets avec des espaces superflus
        stats.ajouter_sujets(["  Python  ", "Java", " C++ "])
        
        # THEN: Les espaces doivent être supprimés
        assert "Python" in stats._sujet_counts
        assert "  Python  " not in stats._sujet_counts

    def test_ajouter_sujets_vides_ignores(self):
        """Teste que les chaînes vides sont ignorées"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute une liste contenant des chaînes vides
        stats.ajouter_sujets(["Python", "", "   ", "Java"])
        
        # THEN: Seuls les sujets non vides doivent être ajoutés
        assert len(stats._sujet_counts) == 2
        assert "" not in stats._sujet_counts

    def test_ajouter_sujets_non_string_ignores(self):
        """Teste que les non-strings sont ignorés"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute une liste avec des types mixtes
        stats.ajouter_sujets(["Python", 123, None, "Java", ["nested"]])
        
        # THEN: Seules les chaînes valides doivent être ajoutées
        assert len(stats._sujet_counts) == 2
        assert "Python" in stats._sujet_counts
        assert "Java" in stats._sujet_counts

    def test_top_sujets_defaut(self):
        """Teste la récupération des top sujets par défaut"""
        # GIVEN: Une instance avec plusieurs sujets de fréquences différentes
        stats = Statistiques()
        sujets = ["A"] * 5 + ["B"] * 3 + ["C"] * 8 + ["D"] * 2
        stats.ajouter_sujets(sujets)
        
        # WHEN: On récupère les top sujets
        top = stats.top_sujets()
        
        # THEN: Ils doivent être triés par fréquence décroissante
        assert top[0] == "C"
        assert top[1] == "A"
        assert top[2] == "B"

    def test_top_sujets_limite(self):
        """Teste la limitation du nombre de top sujets"""
        # GIVEN: Une instance avec 20 sujets différents
        stats = Statistiques()
        sujets = [f"Sujet{i}" for i in range(20)]
        stats.ajouter_sujets(sujets)
        
        # WHEN: On demande les 5 premiers
        top5 = stats.top_sujets(5)
        
        # THEN: On doit obtenir exactement 5 sujets
        assert len(top5) == 5

    def test_vider_sujets(self):
        """Teste le vidage des sujets"""
        # GIVEN: Une instance avec des sujets
        stats = Statistiques()
        stats.ajouter_sujets(["Python", "Java", "C++"])
        
        # WHEN: On vide les sujets
        stats.vider_sujets()
        
        # THEN: Tous les sujets doivent être supprimés
        assert len(stats._sujet_counts) == 0
        assert stats.sujets_plus_frequents == []

    # ========== Tests de fusion ==========
    
    def test_fusionner_stats_simples(self):
        """Teste la fusion de statistiques simples"""
        # GIVEN: Deux instances avec des valeurs différentes
        stats1 = Statistiques(nb_conversations=10, nb_messages=50, heures_utilisation=2.0)
        stats2 = Statistiques(nb_conversations=5, nb_messages=25, heures_utilisation=1.5)
        
        # WHEN: On fusionne stats2 dans stats1
        resultat = stats1.fusionner(stats2)
        
        # THEN: Les valeurs doivent être additionnées et retourner stats1
        assert resultat.nb_conversations == 15
        assert resultat.nb_messages == 75
        assert resultat.heures_utilisation == 3.5
        assert resultat is stats1

    def test_fusionner_avec_sujets(self):
        """Teste la fusion avec des sujets"""
        # GIVEN: Deux instances avec des sujets différents
        stats1 = Statistiques(sujets_plus_frequents=["Python", "Python", "Java"])
        stats2 = Statistiques(sujets_plus_frequents=["Python", "C++", "C++"])
        
        # WHEN: On fusionne stats2 dans stats1
        stats1.fusionner(stats2)
        
        # THEN: Les occurrences de tous les sujets doivent être cumulées
        assert stats1._sujet_counts["Python"] == 3
        assert stats1._sujet_counts["Java"] == 1
        assert stats1._sujet_counts["C++"] == 2

    def test_fusionner_pattern_fluent(self):
        """Teste le chaînage de fusions"""
        # GIVEN: Trois instances distinctes
        stats1 = Statistiques(nb_conversations=10)
        stats2 = Statistiques(nb_conversations=5)
        stats3 = Statistiques(nb_conversations=3)
        
        # WHEN: On chaîne plusieurs fusions
        resultat = stats1.fusionner(stats2).fusionner(stats3)
        
        # THEN: Toutes les valeurs doivent être cumulées et retourner stats1
        assert resultat.nb_conversations == 18
        assert resultat is stats1

    # ========== Tests de représentation ==========
    
    def test_afficher_stats_sans_sujets(self):
        """Teste l'affichage sans sujets"""
        # GIVEN: Une instance avec des valeurs mais sans sujets
        stats = Statistiques(nb_conversations=10, nb_messages=50, heures_utilisation=2.5)
        
        # WHEN: On génère l'affichage
        affichage = stats.afficher_stats()
        
        # THEN: Toutes les valeurs doivent apparaître avec "—" pour les sujets
        assert "conversations=10" in affichage
        assert "messages=50" in affichage
        assert "heures=2.50" in affichage
        assert "—" in affichage

    def test_afficher_stats_avec_sujets(self):
        """Teste l'affichage avec sujets"""
        # GIVEN: Une instance avec des sujets
        stats = Statistiques(sujets_plus_frequents=["Python", "Java", "C++"])
        
        # WHEN: On génère l'affichage
        affichage = stats.afficher_stats()
        
        # THEN: Les sujets doivent apparaître dans l'affichage
        assert "Python" in affichage
        assert "Java" in affichage
        assert "C++" in affichage

    def test_str_methode(self):
        """Teste que __str__ appelle afficher_stats"""
        # GIVEN: Une instance quelconque
        stats = Statistiques(nb_conversations=5)
        
        # WHEN: On appelle str() sur l'instance
        str_result = str(stats)
        
        # THEN: Le résultat doit être identique à afficher_stats()
        assert str_result == stats.afficher_stats()

    # ========== Tests de cas limites ==========
    
    def test_valeurs_negatives_conversations(self):
        """Teste le comportement avec des valeurs négatives"""
        # GIVEN: Une instance avec 10 conversations
        stats = Statistiques(nb_conversations=10)
        
        # WHEN: On incrémente avec une valeur négative
        stats.incrementer_conversations(-5)
        
        # THEN: Le nombre doit diminuer
        assert stats.nb_conversations == 5

    def test_liste_vide_sujets(self):
        """Teste l'ajout d'une liste vide"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute une liste vide
        stats.ajouter_sujets([])
        
        # THEN: Aucun sujet ne doit être ajouté
        assert stats.sujets_plus_frequents == []

    def test_top_sujets_k_zero(self):
        """Teste top_sujets avec k=0"""
        # GIVEN: Une instance avec des sujets
        stats = Statistiques(sujets_plus_frequents=["Python", "Java"])
        
        # WHEN: On demande 0 sujets
        top = stats.top_sujets(0)
        
        # THEN: On doit obtenir une liste vide
        assert top == []

    def test_top_sujets_k_superieur_nombre_sujets(self):
        """Teste top_sujets avec k > nombre de sujets"""
        # GIVEN: Une instance avec 2 sujets
        stats = Statistiques(sujets_plus_frequents=["Python", "Java"])
        
        # WHEN: On demande 10 sujets
        top = stats.top_sujets(10)
        
        # THEN: On doit obtenir seulement les 2 sujets disponibles
        assert len(top) == 2

    def test_heures_utilisation_precision(self):
        """Teste la précision des heures d'utilisation"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On ajoute des temps avec décimales
        stats.ajouter_temps(0.1)
        stats.ajouter_temps(0.2)
        
        # THEN: Le résultat doit être précis (pas d'erreur de float)
        assert abs(stats.heures_utilisation - 0.3) < 1e-10

    def test_fusionner_avec_stats_vides(self):
        """Teste la fusion avec des stats vides"""
        # GIVEN: Une instance avec des valeurs et une instance vide
        stats1 = Statistiques(nb_conversations=10)
        stats2 = Statistiques()
        
        # WHEN: On fusionne l'instance vide
        stats1.fusionner(stats2)
        
        # THEN: Les valeurs de stats1 ne doivent pas changer
        assert stats1.nb_conversations == 10

    # ========== Tests d'intégration ==========
    
    def test_scenario_utilisation_complete(self):
        """Teste un scénario d'utilisation complet"""
        # GIVEN: Une instance vide
        stats = Statistiques()
        
        # WHEN: On simule une journée d'activité
        stats.incrementer_conversations(5)
        stats.incrementer_messages(25)
        stats.ajouter_temps(1.5)
        stats.ajouter_sujets(["Python", "Django", "Python", "Flask"])
        
        # THEN: Toutes les statistiques doivent être mises à jour correctement
        assert stats.nb_conversations == 5
        assert stats.nb_messages == 25
        assert stats.heures_utilisation == 1.5
        assert stats._sujet_counts["Python"] == 2
        assert len(stats.top_sujets(3)) == 3

    def test_scenario_fusion_multiples(self):
        """Teste la fusion de plusieurs sources de stats"""
        # GIVEN: Des statistiques pour deux jours différents
        stats_jour1 = Statistiques(
            nb_conversations=3,
            nb_messages=15,
            heures_utilisation=0.5,
            sujets_plus_frequents=["Python", "Django"]
        )
        
        stats_jour2 = Statistiques(
            nb_conversations=5,
            nb_messages=30,
            heures_utilisation=1.0,
            sujets_plus_frequents=["Python", "Flask", "Docker"]
        )
        
        # WHEN: On fusionne les statistiques dans une instance totale
        stats_totales = Statistiques()
        stats_totales.fusionner(stats_jour1).fusionner(stats_jour2)
        
        # THEN: Les statistiques totales doivent refléter le cumul
        assert stats_totales.nb_conversations == 8
        assert stats_totales.nb_messages == 45
        assert stats_totales.heures_utilisation == 1.5
        assert stats_totales._sujet_counts["Python"] == 2


# Exécution des tests avec pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
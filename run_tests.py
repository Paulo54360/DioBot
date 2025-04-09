
import unittest
import sys
import os
from termcolor import colored
import time
import inspect
from datetime import datetime

# Ajouter le répertoire racine au chemin de recherche
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_tests():
    """Exécute les tests unitaires avec un affichage amélioré."""
    # Bannière de début
    print("\n" + "="*80)
    print(colored("🤖 EXÉCUTION DES TESTS UNITAIRES DU BOT DISCORD 🤖", "cyan", attrs=["bold"]))
    print("="*80 + "\n")
    
    # Découvrir et charger les tests
    start_time = time.time()
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    
    # Créer un runner personnalisé
    class DetailedTestResult(unittest.TextTestResult):
        def __init__(self, stream, descriptions, verbosity):
            super().__init__(stream, descriptions, verbosity)
            self.test_details = []
            self.current_test_start_time = None
            self.current_test = None
        
        def startTest(self, test):
            self.current_test = test
            self.current_test_start_time = time.time()
            super().startTest(test)
            
            # Afficher le nom du test en cours
            test_name = self.getDescription(test)
            self.stream.write(colored(f"\n▶️ Exécution de: {test_name}\n", "blue"))
            
            # Afficher la docstring du test
            doc = test._testMethodDoc
            if doc:
                self.stream.write(colored(f"   Description: {doc}\n", "blue"))
            
            # Afficher le fichier source et la ligne
            test_method = getattr(test, test._testMethodName)
            file_path = inspect.getfile(test_method)
            line_no = inspect.getsourcelines(test_method)[1]
            rel_path = os.path.relpath(file_path)
            self.stream.write(colored(f"   Fichier: {rel_path}:{line_no}\n", "blue"))
            
            self.stream.write(colored("   Statut: ", "blue"))
        
        def addSuccess(self, test):
            super().addSuccess(test)
            duration = time.time() - self.current_test_start_time
            self.stream.write(colored('✅ SUCCÈS', 'green'))
            self.stream.write(colored(f" ({duration:.3f}s)\n", "blue"))
            
            self.test_details.append({
                'name': self.getDescription(test),
                'status': 'success',
                'duration': duration,
                'message': None
            })
        
        def addError(self, test, err):
            super().addError(test, err)
            duration = time.time() - self.current_test_start_time
            self.stream.write(colored('❌ ERREUR', 'red'))
            self.stream.write(colored(f" ({duration:.3f}s)\n", "blue"))
            
            error_message = self._exc_info_to_string(err, test)
            self.stream.write(colored(f"   Détails de l'erreur:\n{error_message}\n", "red"))
            
            self.test_details.append({
                'name': self.getDescription(test),
                'status': 'error',
                'duration': duration,
                'message': error_message
            })
        
        def addFailure(self, test, err):
            super().addFailure(test, err)
            duration = time.time() - self.current_test_start_time
            self.stream.write(colored('⚠️ ÉCHEC', 'yellow'))
            self.stream.write(colored(f" ({duration:.3f}s)\n", "blue"))
            
            failure_message = self._exc_info_to_string(err, test)
            self.stream.write(colored(f"   Détails de l'échec:\n{failure_message}\n", "yellow"))
            
            self.test_details.append({
                'name': self.getDescription(test),
                'status': 'failure',
                'duration': duration,
                'message': failure_message
            })
        
        def addSkip(self, test, reason):
            super().addSkip(test, reason)
            duration = time.time() - self.current_test_start_time
            self.stream.write(colored('⏭️ IGNORÉ', 'cyan'))
            self.stream.write(colored(f" ({duration:.3f}s)\n", "blue"))
            self.stream.write(colored(f"   Raison: {reason}\n", "cyan"))
            
            self.test_details.append({
                'name': self.getDescription(test),
                'status': 'skip',
                'duration': duration,
                'message': reason
            })
    
    class DetailedTestRunner(unittest.TextTestRunner):
        def _makeResult(self):
            return DetailedTestResult(self.stream, self.descriptions, self.verbosity)
        
        def run(self, test):
            result = super().run(test)
            return result
    
    # Exécuter les tests
    runner = DetailedTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher un résumé
    elapsed_time = time.time() - start_time
    print("\n" + "="*80)
    print(colored(f"RÉSUMÉ DES TESTS ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})", "cyan", attrs=["bold"]))
    print("="*80)
    
    total = result.testsRun
    success = total - len(result.errors) - len(result.failures) - len(result.skipped)
    
    print(f"\nTests exécutés : {total}")
    print(colored(f"✅ Réussis    : {success}", "green"))
    
    if result.failures:
        print(colored(f"⚠️ Échecs     : {len(result.failures)}", "yellow"))
    else:
        print(f"⚠️ Échecs     : 0")
    
    if result.errors:
        print(colored(f"❌ Erreurs    : {len(result.errors)}", "red"))
    else:
        print(f"❌ Erreurs    : 0")
    
    if hasattr(result, 'skipped') and result.skipped:
        print(colored(f"⏭️ Ignorés    : {len(result.skipped)}", "cyan"))
    else:
        print(f"⏭️ Ignorés    : 0")
    
    print(f"\nTemps d'exécution total : {elapsed_time:.2f} secondes")
    
    # Afficher les tests les plus lents
    if hasattr(result, 'test_details') and result.test_details:
        slowest_tests = sorted(result.test_details, key=lambda x: x['duration'], reverse=True)[:5]
        if slowest_tests:
            print("\n" + "-"*80)
            print(colored("TESTS LES PLUS LENTS", "yellow"))
            print("-"*80)
            for i, test in enumerate(slowest_tests, 1):
                status_color = {
                    'success': 'green',
                    'failure': 'yellow',
                    'error': 'red',
                    'skip': 'cyan'
                }.get(test['status'], 'white')
                
                status_icon = {
                    'success': '✅',
                    'failure': '⚠️',
                    'error': '❌',
                    'skip': '⏭️'
                }.get(test['status'], '❓')
                
                duration = test['duration']
                print(f"{i}. {colored(status_icon, status_color)} {test['name']} - {colored(f'{duration:.3f}s', 'yellow')}")
    
    # Générer un rapport HTML
    try:
        from jinja2 import Template
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rapport de tests - DioBot</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .summary { margin: 20px 0; }
                .success { color: green; }
                .failure { color: orange; }
                .error { color: red; }
                .skip { color: gray; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .details { margin-top: 10px; font-family: monospace; white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h1>Rapport de tests - DioBot</h1>
            <div class="summary">
                <p>Date: {{ date }}</p>
                <p>Tests exécutés: {{ total }}</p>
                <p class="success">Réussis: {{ success }}</p>
                <p class="failure">Échecs: {{ failures }}</p>
                <p class="error">Erreurs: {{ errors }}</p>
                <p class="skip">Ignorés: {{ skipped }}</p>
                <p>Temps d'exécution: {{ elapsed_time }}s</p>
            </div>
            
            <h2>Détails des tests</h2>
            <table>
                <tr>
                    <th>Test</th>
                    <th>Statut</th>
                    <th>Durée</th>
                    <th>Détails</th>
                </tr>
                {% for test in tests %}
                <tr>
                    <td>{{ test.name }}</td>
                    <td class="{{ test.status }}">{{ test.status|upper }}</td>
                    <td>{{ "%.3f"|format(test.duration) }}s</td>
                    <td>
                        {% if test.message %}
                        <div class="details">{{ test.message }}</div>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_report = template.render(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total=total,
            success=success,
            failures=len(result.failures),
            errors=len(result.errors),
            skipped=len(result.skipped) if hasattr(result, 'skipped') else 0,
            elapsed_time=round(elapsed_time, 2),
            tests=result.test_details if hasattr(result, 'test_details') else []
        )
        
        report_dir = "test-reports"
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with open(report_file, 'w') as f:
            f.write(html_report)
        
        print(f"\nRapport HTML généré: {report_file}")
    except ImportError:
        print("\nLa génération du rapport HTML nécessite jinja2. Installez-le avec 'pip install jinja2'.")
    except Exception as e:
        print(f"\nErreur lors de la génération du rapport HTML: {e}")
    
    # Retourner le code de sortie approprié
    return 0 if success == total else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 
import os
from dotenv import load_dotenv
import anthropic
import time
import requests
from urllib.parse import urlparse
from generator import get_seo_keywords_for_topic
from prompts_and_texts import REFERENCE_TONE_TEXT, CLIENT_INTRO_EXAMPLE

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Global variables to store reference data and SEO data
reference_information = None
reference_style = REFERENCE_TONE_TEXT  # Hardcoded reference tone
seo_keywords = []

def get_topic_input():
    """Get legal topic from user"""
    print("=== Legal SEO Content Generator ===")
    topic = input("Bitte geben Sie das juristische Thema ein: ").strip()
    
    # Ask for separate keyword topic if needed
    print(f"\nThema für Content: '{topic}'")
    use_different_keyword_topic = input("Möchten Sie ein anderes Thema für Keyword-Recherche verwenden? (j/n): ").strip().lower()
    
    keyword_topic = topic  # Default to same topic
    if use_different_keyword_topic in ['j', 'ja', 'y', 'yes']:
        keyword_topic = input("Keyword-Recherche-Thema (z.B. 'betäubungsmittelstrafrecht' statt '§ 29 und § 29a BTMG'): ").strip()
        print(f"Keyword-Thema: '{keyword_topic}'")
    
    return topic, keyword_topic

def ask_for_reference_inputs():
    """Ask for optional reference information input"""
    print("\n--- Referenz-Information (für Analyse) ---")
    use_ref_info = input("Möchten Sie eine Quelle für relevante Rechtsinformationen angeben? (j/n): ").strip().lower()
    ref_info_source = None
    if use_ref_info in ['j', 'ja', 'y', 'yes']:
        ref_info_source = input("URL oder Dateipfad für Rechtsinformationen: ").strip()
    
    return ref_info_source

def fetch_reference_information(source):
    """Fetch reference information from URL or file path"""
    try:
        # Check if it's a URL
        parsed = urlparse(source)
        if parsed.scheme in ['http', 'https']:
            print("Lade Referenz-Information von URL...")
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            return response.text
        else:
            # Treat as file path
            print("Lade Referenz-Information aus Datei...")
            with open(source, 'r', encoding='utf-8') as file:
                return file.read()
    except Exception as e:
        print(f"Fehler beim Laden der Referenz-Information: {e}")
        return None

def analyze_reference_information(content, topic):
    """Analyze content to extract only relevant legal information for a specific topic"""
    if not content:
        return None
    
    print("Analysiere Referenz-Information...")
    
    prompt = f"""
Du sollst aus folgendem Text AUSSCHLIESSLICH relevante Rechtsinformationen zum Thema "{topic}" extrahieren:

EXTRAHIERE NUR (relevant für "{topic}"):
- Relevante Paragraphen und Gesetze (§§)
- Wichtige rechtliche Definitionen
- Schlüsselinformationen zum Rechtsgebiet
- Verfahrensschritte oder rechtliche Prozesse
- Relevante Strafen oder Rechtsfolgen

IGNORIERE:
- Technische Website-Details
- HTML-Code oder Meta-Informationen
- Irrelevante Werbetexte
- Formatierungen oder Design-Elemente
- Informationen, die nichts mit "{topic}" zu tun haben

Quelle:
{content[:4000]}...

Gib NUR die relevanten Rechtsinformationen zurück, die für das Schreiben von Rechtstexten zum Thema "{topic}" nützlich sind.
"""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Fehler bei der Informationsanalyse: {e}")
        return None

def generate_outline(topic):
    """Generate comprehensive outline focused purely on legal content - NO SEO keywords"""
    base_prompt = f"""
Du bist ein erfahrener Anwalt und SEO-Experte. Erstelle eine vollständige Gliederung mit H1- und H2-Überschriften zu dem Thema "{topic}".

Die Gliederung muss relevanten juristischen Aspekte enthalten, die ein Mandant wissen muss oder wonach er suchen könnte.
Was würde ein Betroffener alles wissen wollen? Welche Fragen stellen Mandanten? 

Die Gliederung soll NUR das juristische Thema behandeln. KEINE Abschnitte über Kontakt/Über uns...

Fokus ausschließlich auf rechtliche Inhalte zum Thema "{topic}".

Formatiere die Gliederung so:
- Verwende # für H1 Überschriften (Hauptthemen)  
- Verwende ## für H2 Überschriften (Unterthemen)

Beispiel:
# Hauptthema 1
## Unterthema 1.1
## Unterthema 1.2
# Hauptthema 2
## Unterthema 2.1
"""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        temperature=0.4,
        messages=[{"role": "user", "content": base_prompt}]
    )
    return response.content[0].text.strip()

def generate_complete_content(topic, outline, target_length=None):
    """Generate complete informational content - NO SEO integration here"""
    
    base_prompt = f"""
Du bist ein professioneller SEO- und Rechtstext-Autor, spezialisiert auf Strafrecht. 
Schreibe einen informativen, überzeugenden Text zu dem Thema "{topic}".

Verwende folgende Gliederung:
{outline}
"""
    
    # Only add length instruction if user specified one
    if target_length:
        length_guides = {
            "short": "LÄNGE: Maximal 1500-2000 Wörter. Konzentriere dich auf das Wesentliche.",
            "medium": "LÄNGE: Etwa 2500-3500 Wörter. Ausgewogene Tiefe und Übersichtlichkeit.",
            "long": "LÄNGE: Etwa 4000-5000 Wörter. Umfassende und detaillierte Behandlung."
        }
        base_prompt += f"\n{length_guides.get(target_length, '')}\n"
    
    base_prompt += f"""
Anforderungen:
- Juristisch korrekt und vollständig
- Alle relevanten Paragraphen und Gesetze nennen
- Strafen und Rechtsfolgen aufzeigen
- Für Laien und Mandanten verständlich aber fachlich fundiert
- Betone Komplexität und Risiken, um Wert anwaltlicher Hilfe zu verdeutlichen
- Informiere Betroffene und zeige den Wert professioneller Verteidigung

FOKUS & RELEVANZ:
- Bleibe STRENG beim Thema "{topic}" - keine allgemeinen Rechtsbelehrungen
- Vermeide generische Verteidigungsstrategien, die für jedes Delikt gelten
- Keine Abschnitte über allgemeine Rechtfertigungsgründe (Notwehr, Notstand) - diese gehören auf eigene Seiten
- KEIN generischer "Anwalt-Bot-Content" - alles muss spezifisch für "{topic}" sein
- Google-Bot-Optimierung: Jeder Absatz muss direkt mit "{topic}" zu tun haben

Stil: Sachlich, fachkompetent, ultra ansprechend. 
Verwende gelegentlich "wir"-Formulierungen (z.B. "Wir helfen Ihnen", "Gemeinsam entwickeln wir Ihre Verteidigung").
Vermeide akademische Ausschweifungen und Redundanz.
"""

    global reference_information, reference_style
    
    if reference_information:
        base_prompt += f"""
Berücksichtige diese relevanten Rechtsinformationen, aber beschränke dich nicht darauf:
{reference_information}
"""

    # Client intro instruction
    base_prompt += f"""
EINLEITUNG: Beginne den Artikel mit einer empathischen Mandanten-Einleitung nach diesem Muster (als INSPIRATION, nicht zum Kopieren):
{CLIENT_INTRO_EXAMPLE}
Schreibe eine ähnliche Einleitung für das Thema "{topic}". Passe alle Details an (Delikt, Paragraphen, spezifische Situation), variiere die Formulierungen und Struktur.
"""

    # Reference style is always available (hardcoded)
    base_prompt += f"""
TONALITÄT: Orientiere dich am Ton und Schreibstil des folgenden Referenztextes. Übernimm NUR den Ton und Stil, NICHT die rechtlichen Inhalte, weil es um ein anderes Thema da geht.
REFERENZTEXT:
{reference_style}
"""
    
    # Use streaming to show progress
    print("Starte Content-Generierung mit Streaming...")
    try:
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=15000,
            temperature=0.4,
            messages=[{"role": "user", "content": base_prompt}]
        ) as stream:
            result = ""
            char_count = 0
            for text in stream.text_stream:
                result += text
                char_count += len(text)
                # Print progress every 1000 characters
                if char_count % 1000 == 0:
                    print(f"  ... {char_count} Zeichen generiert")
        
        print(f"✅ Content-Generierung abgeschlossen: {len(result)} Zeichen")
        return result.strip()
        
    except Exception as e:
        print(f"[ERROR] Content generation failed: {e}")
        # Fallback to non-streaming if streaming fails
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20000,
            temperature=0.4,
            messages=[{"role": "user", "content": base_prompt}]
        )
        return response.content[0].text.strip()
    
def verify_and_fix_legal_content(content, topic):
    """Verify legal accuracy and fix any errors found"""
    
    print("Prüfe rechtliche Korrektheit und behebe Fehler...")
    
    prompt = f"""
Deine Aufgabe: Prüfe diesen rechtlichen Text zum Thema "{topic}" auf Fehler und korrigiere sie DIREKT im Text.

TEXT:
{content}

KRITISCHE PRÜFPUNKTE FÜR "{topic}":

1. PARAGRAPHEN & GESETZE:
   - Falsche oder nicht existierende Paragraphen
   - Falsche Zuordnungen zum Thema "{topic}"

2. RECHTLICHE DEFINITIONEN ZU "{topic}":
   - Unvollständige oder unpräzise Definitionen
   - Fehlende Tatbestandsmerkmale

3. STRAFMASSE & RECHTSFOLGEN:
   - Falsche Mindest- oder Höchststrafen bei "{topic}"
   - Fehlende Qualifikationen oder minder schwere Fälle

4. IRRELEVANTER INHALT:
   - Entferne Abschnitte ohne direkten Bezug zu "{topic}"
   - Streiche Wiederholungen

WENN UNSICHER → LÖSCHEN
- Bei zweifelhafter Korrektheit → ENTFERNEN
- Bei fehlendem Bezug zu "{topic}" → ENTFERNEN
- Grundregel: Lieber löschen als Fehler stehen lassen

NICHT ÄNDERN:
- Stil und Tonalität
- Korrekte Inhalte zu "{topic}"

Gib nur den korrigierten Text zurück:
"""
    
    try:
        print("Starte rechtliche Prüfung (Streaming)...")
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=30000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            result = ""
            for text in stream.text_stream:
                result += text
        
        print(f"✅ Rechtliche Prüfung abgeschlossen (Länge: {len(result)} Zeichen)")
        return result.strip()
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return content


def rework_complete_content(corrected_content, topic, keywords):
    """Integrate SEO keywords into legally-correct content"""
    print(f"Starte SEO-Integration mit {len(keywords) if keywords else 0} Keywords...")
    
    if not keywords:
        return corrected_content
    
    # Add rate limiting delay
    time.sleep(3)
    print(f"Keywords to integrate: {keywords}")
    keywords_text = ", ".join(keywords)
    
    prompt = f"""
Du bist SEO-Experte. Integriere Keywords NATÜRLICH in diesen KORREKTEN rechtlichen Text.

KEYWORDS für "{topic}": {keywords_text}

WICHTIG - NICHT ÄNDERN:
- Rechtliche Fakten
- Paragraphen (§§)
- Strafmaße
- Rechtsfolgen

WAS DU TUN SOLLST:
- Keywords natürlich in Überschriften und Fließtext einbauen (KEIN Keyword-Stuffing!)
- Überschriftenstruktur verbessern: # für H1, ## für H2, ### für H3
- Finde 1-2 Stellen, wo Aufzählungspunkte (•) die Lesbarkeit verbessern
- Mache extrem wichtige Informationen BOLD mit **text** (z.B. Strafmaße, kritische Fristen, Paragraphen, Höchststrafen)
  Beispiel: "**§ 29 BtMG**", "**Freiheitsstrafe bis zu 5 Jahren**", "**binnen 2 Wochen**" - nur für wirklich wichtige rechtliche Fakten
- WICHTIG: Redundanzen und Wiederholungen aktiv entfernen

VERMEIDE:
- Keyword-Stuffing (Keywords müssen natürlich wirken)
- Wiederholte Informationen
- Unnötige Redundanz
- Zu viel Fettdruck (maximal 3-5 Stellen im gesamten Text)

Der rechtliche Inhalt muss identisch bleiben!

TEXT:
{corrected_content}

Gib NUR den überarbeiteten Text zurück, ohne Erklärungen:
"""
    
    try:
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=30000,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            result = ""
            for text in stream.text_stream:
                result += text
        
        print(f"✅ SEO-Integration abgeschlossen (Länge: {len(result)} Zeichen)")
        return result.strip()
        
    except Exception as e:
        if "rate_limit" in str(e):
            print("Rate limit erreicht, warte 10 Sekunden...")
            time.sleep(10)
            return rework_complete_content(corrected_content, topic, keywords)
        else:
            print(f"[ERROR] SEO integration failed: {e}")
            return corrected_content
        
def humanize_content(content, topic, deep_mode=False):
    """Reduce AI detection while maintaining legal accuracy and readability"""
    
    print(f"Humanisiere Text {'(Deep Mode)' if deep_mode else ''}...")
    
    # Concise humanization guidelines
    base_techniques = """
Du bist ein professioneller Rechtstext-Autor. Überarbeite den Text, um natürlicher zu wirken.

WIE DU SCHREIBEN SOLLST:
- Sätze: 10-20 Wörter im Durchschnitt, gelegentlich länger
- Aktive Stimme bevorzugen (90%)
- Satzlängen variieren (kurz, mittel, lang mischen)
- Einfache Verbindungen: 'und', 'aber', 'also', 'dann'
- Konkrete Fakten nennen (Zahlen, Paragraphen, Fristen)
- Professionell aber zugänglich bleiben
- Unwichtige Redundanzen und Wiederholungen entfernen

WAS DU VERMEIDEN MUSST:
- Steife Übergänge: "Darüber hinaus", "Ferner", "Zudem", "Des Weiteren", "Im Wesentlichen", "Grundsätzlich"
- Zu perfekte, gleichförmige Strukturen
- Jeden Absatz mit Übergangswort beginnen
- Übermäßig komplexe Verschachtelungen
- Passiv-Konstruktionen wo möglich

PROFESSIONELLE NATÜRLICHKEIT:
- Variiere Satzanfänge
- Gelegentliche kurze Einschübe (in Klammern oder mit Gedankenstrichen)
- Balance zwischen Fachsprache und Verständlichkeit
- Autoritativ aber nicht roboterhaft
"""
    
    if deep_mode:
        base_techniques += """

TIEFE HUMANISIERUNG:
- Noch stärkere Variation in Satzstruktur und -länge
- Eliminiere alle verbliebenen KI-typischen Phrasen
- Mehr natürliche Übergänge, weniger formale Konstruktionen
"""
    
    prompt = f"""
Überarbeite diesen Rechtstext zum Thema "{topic}" für natürlichere Sprache.

TEXT:
{content}

{base_techniques}

KRITISCH - NICHT ÄNDERN:
- Rechtliche Fakten (Paragraphen, Strafmaße, Definitionen, Verfahren)
- Fachbegriffe und juristische Terminologie
- SEO-Keywords
- Inhaltliche Aussagen

BLEIBE PROFESSIONELL: Dies ist ein Rechtstext für Mandanten. Fachlich korrekt, verständlich, aber niemals unprofessionell oder zu locker.

Gib NUR den überarbeiteten Text zurück:
"""
    
    try:
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=30000,
            temperature=0.80 if deep_mode else 0.75,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            result = ""
            for text in stream.text_stream:
                result += text
        
        print(f"✅ Humanisierung abgeschlossen (Länge: {len(result)} Zeichen)")
        return result.strip()
        
    except Exception as e:
        if "rate_limit" in str(e):
            print("Rate limit erreicht, warte 10 Sekunden...")
            time.sleep(10)
            return humanize_content(content, topic, deep_mode)
        else:
            print(f"[ERROR] Humanization failed: {e}")
            return content
        
if __name__ == "__main__":
    # Step 1: Topic Input & Reference Inputs
    topic, keyword_topic = get_topic_input()
    
    # Get reference inputs (only info, style is hardcoded)
    ref_info_source = ask_for_reference_inputs()
    
    # Process reference information (for analysis)
    if ref_info_source:
        content = fetch_reference_information(ref_info_source)
        if content:
            info = analyze_reference_information(content)
            if info:
                reference_information = info
                print("✅ Referenz-Information erfolgreich extrahiert!")
                print("\n" + "="*50)
                print("EXTRAHIERTE RECHTSINFORMATIONEN:")
                print(info)
                print("="*50)
            else:
                print("❌ Fehler bei der Informationsextraktion.")
        else:
            print("❌ Referenz-Information konnte nicht geladen werden.")
    
    print(f"\n✅ Standard-Referenz-Ton aktiv (Körperverletzung-Stil)")
    
    # Step 2: Generate outline
    print("\n== GLIEDERUNG ==")
    outline = generate_outline(topic)
    print(outline)

    # Step 3: Generate complete content
    print(f"\n== ORIGINAL ARTIKEL ==")
    print("Generiere vollständigen Artikel...")
    complete_content = generate_complete_content(topic, outline)
    print(complete_content[:500] + "..." if len(complete_content) > 500 else complete_content)
    
    # Step 4: Verify and fix legal errors
    print(f"\n== RECHTLICHE PRÜFUNG UND KORREKTUR ==")
    corrected_content = verify_and_fix_legal_content(complete_content, topic)
    print(corrected_content[:500] + "..." if len(corrected_content) > 500 else corrected_content)
    
    # Step 5: SEO Keyword Research
    print(f"\n== SEO KEYWORD RESEARCH (Thema: '{keyword_topic}') ==")
    seo_keywords = get_seo_keywords_for_topic(keyword_topic)
    if seo_keywords:
        print("✅ SEO Keywords erfolgreich generiert:")
        for i, kw in enumerate(seo_keywords, 1):
            print(f"  {i}. {kw}")
    else:
        print("❌ Keine Keywords erhalten.")
        print("💡 Tipp: Versuchen Sie ein breiteres Keyword-Thema (z.B. 'betäubungsmittelstrafrecht' statt '§ 29 BtMG')")
    
    # Step 6: SEO Integration
    if seo_keywords:
        print(f"\n== SEO-OPTIMIERUNG ==")
        print("Integriere Keywords in korrigierten Text...")
        seo_optimized_content = rework_complete_content(corrected_content, topic, seo_keywords)
        print(seo_optimized_content[:500] + "..." if len(seo_optimized_content) > 500 else seo_optimized_content)
    else:
        print(f"\n== NACH RECHTLICHER KORREKTUR ==")
        seo_optimized_content = corrected_content
        print(corrected_content[:500] + "..." if len(corrected_content) > 500 else corrected_content)
    
    # Step 7: Humanization (NEW!)
    print(f"\n== HUMANISIERUNG ==")
    print("Reduziere KI-Erkennbarkeit...")
    humanized_content = humanize_content(seo_optimized_content, topic)
    
    print("\n== FINALER HUMANISIERTER ARTIKEL ==")
    print(humanized_content)
    
    print("\n" + "="*50)
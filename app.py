import streamlit as st
import main
from generator import get_seo_keywords_for_topic
from image_generator import generate_image_prompt, generate_article_image_realistic, generate_article_image_iconic
from pdf_generator import generate_pdf, generate_html

# =======================
# SIMPLE PASSWORD GATE
# =======================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password in session
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, ask for password
        st.text_input("Enter password:", type="password", key="password", on_change=password_entered)
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password:", type="password", key="password", on_change=password_entered)
        st.error("❌ Wrong password.")
        st.stop()

check_password()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Legal SEO Content Generator",
    page_icon="⚖️",
    layout="wide"
)

# ============================================================================
# REFERENCE INFORMATION PROCESSING
# ============================================================================
def process_reference_info(ref_info_source, topic):
    """Process reference information input"""
    
    with st.spinner("Analysiere Referenz-Information..."):
        content = ref_info_source.strip()
        
        if content:
            info = main.analyze_reference_information(content, topic)
            if info:
                main.reference_information = info
                st.session_state.ref_info_processed = True
                st.success("✅ Referenz-Information erfolgreich extrahiert!")
                
                with st.expander("📊 Extrahierte Rechtsinformationen anzeigen"):
                    st.write(info)
            else:
                st.error("Fehler bei der Informationsextraktion.")
        else:
            st.error("Referenz-Information konnte nicht geladen werden.")

# ============================================================================
# ARTICLE GENERATION PIPELINE
# ============================================================================
def generate_complete_article(topic, target_length=None):
    """Generate complete article with debug output"""
    
    # Initialize progress tracking
    progress = st.progress(0)
    status = st.empty()
    log_container = st.container()
    
    # Setup logging container
    with log_container:
        st.subheader("📋 Generierungs-Log")
        log_placeholder = st.empty()
        logs = []
    
    def add_log(message):
        """Helper function to add log messages"""
        logs.append(message)
        with log_placeholder:
            for log in logs:
                st.write(log)
    
    # Start generation process
    add_log("🚀 Starte Artikel-Generierung...")
    add_log(f"📝 Content-Thema: '{topic}'")
    
    # ------------------------------------------------------------------------
    # STEP 1: OUTLINE (Use edited outline or generate new)
    # ------------------------------------------------------------------------
    
    # Check if we have an edited outline from the UI
    if 'edited_outline' in st.session_state and st.session_state.edited_outline:
        status.text("Schritt 1/5: Verwende bearbeitete Gliederung...")
        progress.progress(0.12)
        add_log("✅ Verwende bearbeitete Gliederung aus Editor")
        outline = st.session_state.edited_outline
        st.session_state.outline = outline
        
        with st.expander("📋 Verwendete Gliederung"):
            st.markdown(outline)
        
        add_log(f"📊 Gliederung hat {len(outline.split('#'))} Hauptabschnitte")
        progress.progress(0.24)
    else:
        # Generate new outline if not already edited
        status.text("Schritt 1/5: Erstelle Gliederung...")
        progress.progress(0.12)
        
        try:
            add_log("⏳ Generiere Gliederung...")
            outline = main.generate_outline(topic)
            st.session_state.outline = outline
            add_log("✅ Gliederung erfolgreich erstellt")
            
            with st.expander("📋 Zeige Gliederungs-Output"):
                st.markdown(outline)
            
            add_log(f"📊 Gliederung hat {len(outline.split('#'))} Hauptabschnitte")
            progress.progress(0.24)
        except Exception as e:
            add_log(f"❌ Fehler bei Gliederungserstellung: {str(e)}")
            st.error(f"Fehler: {str(e)}")
            return
    
    try:
        
        # ------------------------------------------------------------------------
        # STEP 2: CONTENT GENERATION
        # ------------------------------------------------------------------------
        status.text("Schritt 2/5: Generiere kompletten Artikel...")
        add_log("⏳ Generiere vollständigen Artikel-Inhalt...")

        if main.reference_information:
            add_log("📊 Nutze zusätzliche Referenz-Informationen")

        complete_content = main.generate_complete_content(topic, outline, target_length)
        st.session_state.complete_article = complete_content
        
        word_count = len(complete_content.split())
        char_count = len(complete_content)
        add_log(f"✅ Original-Artikel generiert: {word_count:,} Wörter, {char_count:,} Zeichen")
        
        with st.expander("📄 Zeige Content-Output (erste 1000 Zeichen)"):
            st.markdown(complete_content[:1000] + "...")
        
        progress.progress(0.40)
        
        # ------------------------------------------------------------------------
        # STEP 3: LEGAL VERIFICATION
        # ------------------------------------------------------------------------
        status.text("Schritt 3/5: Prüfe und korrigiere rechtliche Fehler...")
        add_log("⏳ Starte rechtliche Prüfung und Korrektur...")
        
        corrected_content = main.verify_and_fix_legal_content(complete_content, topic)
        st.session_state.corrected_article = corrected_content
        
        corrected_words = len(corrected_content.split())
        corrected_chars = len(corrected_content)
        add_log(f"✅ Rechtliche Prüfung abgeschlossen")
        add_log(f"📊 Korrigierte Version: {corrected_words:,} Wörter, {corrected_chars:,} Zeichen")
        
        if complete_content == corrected_content:
            add_log("ℹ️ Keine rechtlichen Fehler gefunden")
        else:
            char_diff = corrected_chars - char_count
            add_log(f"✏️ Änderungen vorgenommen: {char_diff:+,} Zeichen")
        
        progress.progress(0.56)
        
        # Check if keywords are available
        keywords_available = 'seo_keywords' in st.session_state and st.session_state.seo_keywords
        add_log(f"🔍 Keywords verfügbar: {'Ja' if keywords_available else 'Nein'}")
        
        if keywords_available:
            add_log(f"🔑 Anzahl Keywords: {len(st.session_state.seo_keywords)}")
        
        # ------------------------------------------------------------------------
        # STEP 4: SEO INTEGRATION
        # ------------------------------------------------------------------------
        status.text("Schritt 4/5: Integriere SEO-Keywords...")
        
        if keywords_available:
            add_log("⏳ Starte SEO-Integration...")
            seo_optimized_content = main.rework_complete_content(
                corrected_content,
                topic, 
                st.session_state.seo_keywords
            )
            st.session_state.seo_optimized_article = seo_optimized_content
            
            seo_length = len(seo_optimized_content)
            seo_words = len(seo_optimized_content.split())
            
            add_log(f"✅ SEO-Integration abgeschlossen")
            add_log(f"📊 SEO-Version: {seo_words:,} Wörter, {seo_length:,} Zeichen")
            
            with st.expander("🔑 Zeige SEO-Output (erste 1000 Zeichen)"):
                st.markdown(seo_optimized_content[:1000] + "...")
        else:
            add_log("ℹ️ Keine SEO-Keywords - verwende korrigierte Version")
            seo_optimized_content = corrected_content
            st.session_state.seo_optimized_article = seo_optimized_content
        
        progress.progress(0.72)
        
        # ------------------------------------------------------------------------
        # STEP 5: HUMANIZATION
        # ------------------------------------------------------------------------
        status.text("Schritt 5/5: Humanisiere Text...")
        add_log("⏳ Starte Humanisierung des Textes...")
        
        humanized_content = main.humanize_content(seo_optimized_content, topic)
        st.session_state.humanized_article = humanized_content
        
        humanized_words = len(humanized_content.split())
        humanized_chars = len(humanized_content)
        add_log(f"✅ Humanisierung abgeschlossen")
        add_log(f"📊 Finale Version: {humanized_words:,} Wörter, {humanized_chars:,} Zeichen")
        
        with st.expander("👨🏼 Zeige Humanisierungs-Output (erste 1000 Zeichen)"):
            st.markdown(humanized_content[:1000] + "...")
        
        progress.progress(1.0)
        status.text("✅ Artikel erfolgreich erstellt!")
        add_log("🎉 Generierung erfolgreich abgeschlossen!")
        
        st.success("🎉 Artikel erfolgreich erstellt!")
        
    except Exception as e:
        add_log(f"❌ Fehler aufgetreten: {str(e)}")
        st.error(f"Fehler bei der Artikelerstellung: {e}")
        status.text("❌ Fehler bei der Generierung")

# ============================================================================
# ARTICLE DISPLAY & DOWNLOAD
# ============================================================================
def display_complete_article():
    """Display the complete generated article"""
    
    st.header("📄 Generierter Artikel")
    
    # Display outline if available
    if 'outline' in st.session_state:
        with st.expander("📋 Gliederung anzeigen"):
            st.markdown(st.session_state.outline)
    
    # Display keywords if available
    if 'seo_keywords' in st.session_state and st.session_state.seo_keywords:
        with st.expander("🔑 Verwendete SEO-Keywords anzeigen"):
            cols = st.columns(3)
            for i, keyword in enumerate(st.session_state.seo_keywords):
                with cols[i % 3]:
                    st.write(f"• {keyword}")
    
    # ------------------------------------------------------------------------
    # DISPLAY MODE SELECTION
    # ------------------------------------------------------------------------
    display_mode = st.radio(
        "Ansichtsmodus wählen:",
        options=["Tabs (Standard)", "Nebeneinander vergleichen"],
        horizontal=True
    )
    
    # Side-by-side comparison view
    if display_mode == "Nebeneinander vergleichen":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 SEO-Optimiert (VORHER)")
            if 'seo_optimized_article' in st.session_state:
                st.markdown(st.session_state.seo_optimized_article)
                word_count = len(st.session_state.seo_optimized_article.split())
                char_count = len(st.session_state.seo_optimized_article)
                st.info(f"📊 {word_count:,} Wörter • {char_count:,} Zeichen")
        
        with col2:
            st.subheader("👨🏼 Humanisiert (NACHHER)")
            if 'humanized_article' in st.session_state:
                st.markdown(st.session_state.humanized_article)
                word_count = len(st.session_state.humanized_article.split())
                char_count = len(st.session_state.humanized_article)
                st.info(f"📊 {word_count:,} Wörter • {char_count:,} Zeichen")
    
    # Tabbed view
    else:
        tab1, tab2, tab3 = st.tabs(["👨🏼 Humanisierter Artikel (FINAL)", "📝 SEO-Version", "📄 Original"])
        
        with tab1:
            st.subheader("✍️ Humanisierter Artikel (Final)")
            if 'humanized_article' in st.session_state:
                st.markdown(st.session_state.humanized_article)
                word_count = len(st.session_state.humanized_article.split())
                st.info(f"📊 {word_count:,} Wörter")
        
        with tab2:
            st.subheader("📝 SEO-Optimierte Version")
            if 'seo_optimized_article' in st.session_state:
                st.markdown(st.session_state.seo_optimized_article)
        
        with tab3:
            st.subheader("📄 Original Artikel")
            if 'complete_article' in st.session_state:
                st.markdown(st.session_state.complete_article)
    
    # ------------------------------------------------------------------------
    # DOWNLOAD OPTIONS
    # ------------------------------------------------------------------------

    st.subheader("📥 Download")

    if 'humanized_article' in st.session_state:
        col1, col2 = st.columns(2)
        
        # PDF Download
        with col1:
            pdf_bytes = generate_pdf(st.session_state.humanized_article)
            
            if pdf_bytes:
                st.download_button(
                    label="📄 Als PDF herunterladen",
                    data=pdf_bytes,
                    file_name=f"{st.session_state.topic.replace(' ', '_')}_final.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.error("❌ PDF fehlgeschlagen")
        
        # HTML Download
        with col2:
            html_content = generate_html(st.session_state.humanized_article)
            
            st.download_button(
                label="🌐 Als HTML herunterladen",
                data=html_content,
                file_name=f"{st.session_state.topic.replace(' ', '_')}_final.html",
                mime="text/html",
                use_container_width=True,
                type="secondary"
            )
# ============================================================================
# SIDEBAR STATUS & INFO
# ============================================================================
def sidebar_info():
    """Display workflow information in sidebar"""
    
    # Workflow status tracking
    st.sidebar.header("🔄 Workflow Status")
    
    steps = [
        ("Topic eingegeben", 'topic' in st.session_state and st.session_state.topic),
        ("SEO-Keywords generiert", 'seo_keywords' in st.session_state),
        ("Referenz-Info analysiert", 'ref_info_processed' in st.session_state),
        ("Artikel generiert", 'seo_optimized_article' in st.session_state),
    ]
    
    for step_name, completed in steps:
        if completed:
            st.sidebar.write(f"✅ {step_name}")
        else:
            st.sidebar.write(f"⏳ {step_name}")
    
    # Reference status
    st.sidebar.subheader("📋 Referenz Status")
    st.sidebar.write("📄 Standard-Ton aktiv (Körperverletzung)")
    
    if main.reference_information:
        st.sidebar.write("📊 Zusätzliche Rechtsinformationen verfügbar")
    
    # SEO keywords display
    if 'seo_keywords' in st.session_state and st.session_state.seo_keywords:
        st.sidebar.subheader("🔑 SEO-Keywords")
        for kw in st.session_state.seo_keywords[:5]:
            st.sidebar.write(f"• {kw}")
        if len(st.session_state.seo_keywords) > 5:
            st.sidebar.write(f"... und {len(st.session_state.seo_keywords) - 5} weitere")
    
    # Article statistics
    if 'humanized_article' in st.session_state:
        st.sidebar.subheader("📊 Artikel-Info")
        word_count = len(st.session_state.humanized_article.split())
        st.sidebar.write(f"Wörter: {word_count:,}")
        st.sidebar.write(f"Zeichen: {len(st.session_state.humanized_article):,}")
        st.sidebar.write("👨🏼 Humanisiert")
    
    # Reset button
    if st.sidebar.button("🔄 Neu starten"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        main.reference_information = None
        st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================
def main_app():
    st.title("⚖️ Legal SEO Content Generator")
    
    tab1, tab2 = st.tabs(["📝 Artikel Generator", "🖼️ Bild Generator"])
    
    # ========================================================================
    # TAB 1: ARTICLE GENERATOR
    # ========================================================================
    with tab1:
        # --------------------------------------------------------------------
        # STEP 1: TOPIC & SEO KEYWORDS
        # --------------------------------------------------------------------
        st.header("📋 Schritt 1: Topic & SEO-Keywords")
        
        topic = st.text_input(
            "Bitte geben Sie das juristische Thema ein:",
            placeholder="z.B. Betäubungsmittelstrafrecht, § 29 BtMG, Steuerhinterziehung...",
            key="article_topic"
        )
        
        if topic:
            st.session_state.topic = topic
        
        # SEO Keywords section
        st.subheader("🔑 SEO-Keywords Generierung")

        # Remember user settings
        use_different_keyword_topic = st.checkbox(
            "Anderes Thema für Keyword-Recherche verwenden",
            help="Hilfreich wenn das Hauptthema zu spezifisch für SEMrush ist",
            key="use_different_keyword_topic"
        )

        if use_different_keyword_topic:
            keyword_topic = st.text_input(
                "Keyword-Recherche-Thema:",
                placeholder="z.B. 'betäubungsmittelstrafrecht'",
                key="keyword_topic_input"
            )
        else:
            keyword_topic = None
            st.session_state.keyword_topic_input = None  # reset if unchecked

        # Ensure latest topic is saved
        st.session_state.topic = topic

        # Debug display (optional)
        st.info(f"Content-Thema: '{st.session_state.topic}' | Keyword-Thema: '{st.session_state.get('keyword_topic_input')}'")

        # Generate button
        if st.button("SEO-Keywords generieren", use_container_width=True, key="gen_keywords"):
            # ✅ Pull from session_state, not local vars
            search_topic = (
                st.session_state.get("keyword_topic_input")
                if st.session_state.get("use_different_keyword_topic") and st.session_state.get("keyword_topic_input")
                else st.session_state.get("topic")
            )

            if st.session_state.get("use_different_keyword_topic") and not st.session_state.get("keyword_topic_input"):
                st.error("Bitte geben Sie ein Keyword-Thema ein oder deaktivieren Sie die Option.")
            else:
                with st.spinner(f"Generiere SEO-Keywords für '{search_topic}'..."):
                    seo_keywords = get_seo_keywords_for_topic(search_topic)

                if seo_keywords:
                    st.session_state.seo_keywords_all = seo_keywords
                    st.session_state.keyword_topic_used = search_topic
                else:
                    st.error("❌ Keine SEO-Keywords erhalten.")

        
        # Display and allow selection of keywords
        if 'seo_keywords_all' in st.session_state:
            st.success(f"✅ {len(st.session_state.seo_keywords_all)} SEO-Keywords erfolgreich generiert!")
            st.subheader("🔑 Generierte SEO-Keywords - Wählen Sie aus:")
            
            cols = st.columns(2)
            for i, keyword in enumerate(st.session_state.seo_keywords_all):
                with cols[i % 2]:
                    st.checkbox(keyword, value=True, key=f"kw_{st.session_state.keyword_topic_used}_{i}")
            
            # Collect selected keywords
            selected_keywords = []
            for i, keyword in enumerate(st.session_state.seo_keywords_all):
                if st.session_state.get(f"kw_{st.session_state.keyword_topic_used}_{i}", True):
                    selected_keywords.append(keyword)
            
            st.session_state.seo_keywords = selected_keywords
            
            st.subheader("✅ Ausgewählte Keywords für SEO-Integration:")
            if selected_keywords:
                selected_text = ", ".join(selected_keywords)
                st.info(f"**{len(selected_keywords)} Keywords ausgewählt:** {selected_text}")
            else:
                st.warning("Keine Keywords ausgewählt.")
        
        # --------------------------------------------------------------------
        # STEP 2: REFERENCE INFORMATION (OPTIONAL)
        # --------------------------------------------------------------------
        st.header("📊 Schritt 2: Referenz-Information (Optional)")
        st.write("*Quelle für relevante Rechtsinformationen*")

        use_ref_info = st.radio(
            "Möchten Sie zusätzliche Rechtsinformationen angeben?",
            options=["Nein", "Ja"],
            horizontal=True,
            key="ref_info_radio"
        )

        if use_ref_info == "Ja":
            ref_info_source = st.text_area(
                "Rechtsinformationen Text hier eingeben:",
                height=150,
                placeholder="Fügen Sie relevante Rechtsinformationen ein...",
                key="ref_info_text"
            )
            
            if ref_info_source and ref_info_source.strip():
                if st.button("📊 Referenz-Information analysieren", key="analyze_ref_info"):
                    process_reference_info(ref_info_source, topic)
        
        # --------------------------------------------------------------------
        # STEP 3: CONTENT GENERATION
        # --------------------------------------------------------------------
        st.header("📝 Schritt 3: Content-Generierung")

        # Optional article length control
        with st.expander("⚙️ Artikellänge Option (Optional)"):
            use_length_control = st.checkbox("Artikellänge manuell festlegen")

            article_length = None
            custom_length = None

            if use_length_control:
                article_length = st.radio(
                    "Gewünschte Länge:",
                    options=["short", "medium", "long", "custom"],
                    format_func=lambda x: {
                        "short": "Kurz (1500–2000 Wörter)",
                        "medium": "Mittel (2500–3500 Wörter)",
                        "long": "Lang (4000–5000 Wörter)",
                        "custom": "Benutzerdefiniert"
                    }[x],
                    index=1
                )

                if article_length == "custom":
                    custom_length = st.number_input(
                        "Geben Sie die gewünschte Wortanzahl ein:",
                        min_value=0,
                        max_value=10000,
                        step=100,
                        value=2500,
                        help="Anzahl der Wörter, die der Artikel ungefähr haben soll."
                    )

            # Save to session state for use later
            if article_length == "custom" and custom_length:
                st.session_state.article_length = (max(100, custom_length - 500), min(10000, custom_length + 500))
            else:
                st.session_state.article_length = article_length


        # --------------------------------------------------------------------
        # OUTLINE GENERATION AND EDITING
        # --------------------------------------------------------------------
        st.divider()
        
        # Button 1: Generate Outline
        if st.button("📋 Gliederung generieren", type="primary", use_container_width=True, key="gen_outline"):
            with st.spinner("Generiere Gliederung..."):
                outline = main.generate_outline(topic)
                st.session_state.generated_outline = outline
                st.session_state.edited_outline = outline  # Set this immediately so button becomes enabled
        
        # Button 2: Generate Article (disabled until outline exists)
        outline_exists = 'edited_outline' in st.session_state and st.session_state.edited_outline
        if st.button("✅ SEO-optimierten Artikel generieren", type="primary", use_container_width=True, disabled=not outline_exists):
            generate_complete_article(
                topic, 
                article_length if use_length_control else None,
            )
        
        st.divider()
        
        # Display and allow editing of outline (only if generated)
        if 'generated_outline' in st.session_state:
            st.info("💡 Sie können die Gliederung jetzt bearbeiten, bevor der vollständige Artikel generiert wird.")
            
            edited_outline = st.text_area(
                "Gliederung bearbeiten:",
                value=st.session_state.get('edited_outline', st.session_state.generated_outline),
                height=400,
                key="outline_editor",
                help="Bearbeiten Sie die Gliederung nach Ihren Wünschen. Verwenden Sie # für H1 und ## für H2 Überschriften."
            )
            
            # Save edited outline to session state
            st.session_state.edited_outline = edited_outline
            
            # Preview of outline structure
            with st.expander("👁️ Gliederungs-Vorschau"):
                st.markdown(edited_outline)

    
            # Display generated article
        if 'humanized_article' in st.session_state:
            display_complete_article()
            
            # ===== ADD THIS ENTIRE BLOCK HERE =====
            st.divider()
            
            # Re-humanize section
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("💡 Noch zu viel KI-Erkennung? Führe eine tiefere Humanisierung durch.")
            with col2:
                if st.button("🔄 Tiefer humanisieren", use_container_width=True):
                    with st.spinner("Führe tiefere Humanisierung durch..."):
                        deep_humanized = main.humanize_content(
                            st.session_state.humanized_article,
                            st.session_state.topic,
                            deep_mode=True
                        )
                        st.session_state.humanized_article = deep_humanized
                        st.session_state.deep_humanized = True
                        st.success("✅ Tiefere Humanisierung abgeschlossen!")
                        st.rerun()
    # ========================================================================
    # TAB 2: IMAGE GENERATOR
    # ========================================================================
    with tab2:
        st.header("🖼️ Standalone Bild Generator")
        st.write("Generieren Sie professionelle Bilder für rechtliche Themen")
        
        # --------------------------------------------------------------------
        # IMAGE TOPIC INPUT
        # --------------------------------------------------------------------
        image_topic = st.text_input(
            "Thema für Bild-Generierung:",
            placeholder="z.B. Raub § 249 StGB, Betrug...",
            key="image_topic"
        )
        
        col1, col2 = st.columns(2)
        
        # Generate image prompt suggestions
        with col1:
            if st.button("Bild-Vorschläge generieren"):
                if image_topic:
                    image_prompt_suggestions = generate_image_prompt(image_topic)
                    st.session_state.image_prompt_suggestions = image_prompt_suggestions
                else:
                    st.warning("Bitte geben Sie ein Thema ein.")

        # Allow custom user prompt
        with col2:
            user_prompt = st.text_input("Oder geben Sie Ihre eigene Idee ein:", 
                                        placeholder="z.B. A masked thief")
            use_own_idea = st.checkbox("Eigene Idee verwenden", value=False)

        # Display and select from suggestions
        selected_option = None
        if "image_prompt_suggestions" in st.session_state:
            suggestions = st.session_state.image_prompt_suggestions.split("\n")
            suggestions = [s.strip() for s in suggestions if s.strip()]
            
            if suggestions:
                selected_option = st.radio(
                    "Wählen Sie ein Bild-Vorschlag aus:",
                    options=suggestions,
                    index=0
                )

        # Set final prompt based on user selection
        if use_own_idea and user_prompt:
            st.session_state.user_prompt = user_prompt
        elif selected_option:
            st.session_state.user_prompt = selected_option

        st.write(f"Ausgewählter Bild-Text: {st.session_state.user_prompt if 'user_prompt' in st.session_state else ''}")

        # --------------------------------------------------------------------
        # IMAGE GENERATION SETTINGS
        # --------------------------------------------------------------------
        with st.expander("🖼️ Bild-Generierung"):
            image_style = st.radio(
                "Wählen Sie den Bild-Stil:",
                options=["Realistic Illustration", "Iconic Illustration"],
                index=0
            )
            
            col1, col2 = st.columns(2)
            with col1:
                image_quality = st.selectbox(
                    "Qualität:",
                    options=["standard", "hd"],
                    index=0
                )
            
            with col2:
                image_size = st.selectbox(
                    "Größe:",
                    options=["1024x1024", "1792x1024", "1024x1792"],
                    index=0,
                    format_func=lambda x: {
                        "1024x1024": "Quadratisch (1024x1024)",
                        "1792x1024": "Breit (1792x1024)",
                        "1024x1792": "Hoch (1024x1792)"
                    }[x]
                )
        
        # Generate image button
        if st.button("🎨 Bild generieren", type="primary", use_container_width=True, key="gen_image_standalone"):
            if not image_topic and not user_prompt:
                st.error("Bitte geben Sie ein Thema ein.")
            else:
                with st.spinner("Generiere Bild..."):
                    try:
                        if image_style == "Realistic Illustration":
                            image_url = generate_article_image_realistic(
                                st.session_state.user_prompt,
                                size=image_size,
                                quality=image_quality
                            )
                        else:
                            image_url = generate_article_image_iconic(
                                st.session_state.user_prompt,
                                size=image_size,
                                quality=image_quality
                            )
                        
                        if image_url:
                            st.session_state.standalone_image_url = image_url
                            st.session_state.standalone_image_topic = image_topic
                            st.success("✅ Bild erfolgreich generiert!")
                        else:
                            st.error("❌ Bild-Generierung fehlgeschlagen.")
                            
                    except Exception as e:
                        st.error(f"❌ Fehler: {str(e)}")

        # --------------------------------------------------------------------
        # DISPLAY GENERATED IMAGE
        # --------------------------------------------------------------------
        if 'standalone_image_url' in st.session_state:
            st.divider()
            st.subheader(f"🖼️ Generiertes Bild: {st.session_state.standalone_image_topic}")
            
            # Display image centered
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.image(
                    st.session_state.standalone_image_url,
                    caption=st.session_state.standalone_image_topic,
                    use_container_width=True
                )
            
            # Display URL
            st.write("**Bild-URL:**")
            st.code(st.session_state.standalone_image_url, language=None)
            
            
            with col2:
                import requests
                try:
                    response = requests.get(st.session_state.standalone_image_url)
                    st.download_button(
                        label="💾 Bild herunterladen",
                        data=response.content,
                        file_name=f"{st.session_state.standalone_image_topic.replace(' ', '_')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                except:
                    st.error("Download fehlgeschlagen")
            

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    sidebar_info()
    main_app()
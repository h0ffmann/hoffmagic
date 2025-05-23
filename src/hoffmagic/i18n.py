"""
Internationalization module for hoffmagic blog.
"""

# English translations
en = {
    # General
    "brand_name": "hoffmagic",
    "home": "Home",
    "about": "About",
    "writing": "Writing",
    "essays": "Essays",
    "contact": "Contact",
    "tags": "Tags",
    "search_placeholder": "Search...",
    "search_button_label": "Submit search",
    "read_more": "Read More →",
    "previous": "Previous",
    "next": "Next",
    "page": "Page",
    "of": "of",
    # Header Nav
    "nav_writing": "Writing",
    "nav_about": "About",
    "nav_projects": "Projects", # Future use
    "nav_contact": "Contact",
    # Language Toggle
    "lang_en_short": "EN",
    "lang_en_long": "English",
    "lang_pt_short": "PT",
    "toggle_language": "Toggle Language",

    # Home page
    "latest_writing": "Latest Writing",
    "subscribe": "Subscribe",
    "subscribe_desc": "Get new posts and essays delivered directly to your inbox.",
    "email_address": "Email Address:",
    "subscribe_button": "Subscribe",
    
    # Blog/Writing page
    "blog_title": "Writing",
    "blog_description": "Thoughts, insights, and explorations on various topics",
    "read_more": "Read More →",
    "search_placeholder": "Search articles...",
    
    # About page
    "about_title": "About Me",
    "about_description": "The story behind hoffmagic and its author.",
    
    # Projects page
    "projects_title": "Projects",
    "projects_description": "A collection of my work and open-source contributions.",
    
    # Contact form
    "contact_title": "Contact",
    "send_message": "Send a Message",
    "name": "Name",
    "email": "Email",
    "subject": "Subject",
    "message": "Message",
    "send_button": "Send Message",
    
    # Footer
    "all_rights_reversed": "All rights reversed.",
}

# Portuguese translations
pt = {
    # General
    "brand_name": "hoffmagic",
    "home": "Início",
    "about": "Sobre",
    "writing": "Textos",
    "essays": "Ensaios",
    "contact": "Contato",
    "tags": "Etiquetas",
    "search_placeholder": "Buscar...",
    "search_button_label": "Enviar busca",
    "read_more": "Ler Mais →",
    "previous": "Anterior",
    "next": "Próximo",
    "page": "Página",
    "of": "de",
    # Header Nav
    "nav_writing": "Textos",
    "nav_about": "Sobre",
    "nav_projects": "Projetos", # Uso futuro
    "nav_contact": "Contato",
    # Language Toggle
    "lang_en_short": "EN",
    "lang_en_long": "English",
    "lang_pt_short": "PT",
    "toggle_language": "Alternar Idioma",

    # Home page
    "latest_writing": "Últimos Textos",
    "subscribe": "Inscreva-se",
    "subscribe_desc": "Receba novos posts e ensaios diretamente na sua caixa de entrada.",
    "email_address": "Endereço de Email:",
    "subscribe_button": "Inscrever",
    
    # Blog/Writing page
    "blog_title": "Textos",
    "blog_description": "Pensamentos, insights e explorações sobre vários tópicos",
    "read_more": "Leia Mais →",
    "search_placeholder": "Buscar artigos...",
    
    # About page
    "about_title": "Sobre Mim",
    "about_description": "A história por trás do hoffmagic e seu autor.",
    
    # Projects page
    "projects_title": "Projetos",
    "projects_description": "Uma coleção do meu trabalho e contribuições open-source.",
    
    # Contact form
    "contact_title": "Contato",
    "send_message": "Enviar uma Mensagem",
    "name": "Nome",
    "email": "Email",
    "subject": "Assunto",
    "message": "Mensagem",
    "send_button": "Enviar Mensagem",
    
    # Footer
    "all_rights_reversed": "Todos os direitos invertidos.",
}

def get_translations(lang: str):
    """Get translations dictionary for specified language."""
    if lang.lower() == "pt":
        return pt
    return en  # default to English

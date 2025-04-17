from contacts.admin import ekmutua_admin_site

def admin_site(request):
    """
    Context processor that makes the custom admin site available in templates.
    
    Returns:
        dict: Contains the 'admin_site' variable that will be available in all templates.
    """
    return {
        'admin_site': ekmutua_admin_site,
        'site_header': ekmutua_admin_site.site_header,
        'site_title': ekmutua_admin_site.site_title,
        'site_url': ekmutua_admin_site.site_url,
    }
import json
from typing import List, Dict, Any

# 🔐 Constantes (evita hardcodear strings sensibles)
FIELD_EMAIL = "email"
FIELD_PASSWORD = "password"
FIELD_FIRST_NAME = "first_name"
FIELD_LAST_NAME = "last_name"
FIELD_PHONE = "phone"

REQUIRED_FIELDS = {FIELD_EMAIL, FIELD_PASSWORD}


def get_auth_script(site_id: int, registration_fields: List[str] = None, custom_fields: List[Dict] = None) -> str:
    """Script simple para login, registro, user-info y logout"""

    if registration_fields is None:
        registration_fields = [FIELD_EMAIL, FIELD_PASSWORD, FIELD_FIRST_NAME, FIELD_LAST_NAME]

    if custom_fields is None:
        custom_fields = []

    # =========================
    # BUILD REGISTRATION HTML
    # =========================
    reg_fields_html = ""

    label_map = {
        FIELD_EMAIL: "Correo Electronico",
        FIELD_PASSWORD: "Contrasena",
        FIELD_FIRST_NAME: "Nombre",
        FIELD_LAST_NAME: "Apellido",
        FIELD_PHONE: "Telefono",
    }

    for field in registration_fields:
        label = label_map.get(field, field.replace("_", " ").title())

        if field == FIELD_PASSWORD:
            input_type = "password"
        elif field == FIELD_EMAIL:
            input_type = "email"
        else:
            input_type = "text"

        required = "required" if field in REQUIRED_FIELDS else ""

        reg_fields_html += (
            f'<div style="margin-bottom:12px;">'
            f'<label style="display:block;margin-bottom:4px;font-size:13px;">{label}</label>'
            f'<input type="{input_type}" name="{field}" {required} '
            f'style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box;">'
            f'</div>'
        )

    # =========================
    # CUSTOM FIELDS
    # =========================
    for cf in custom_fields:
        name = cf.get("name", "")
        label = cf.get("label", name)

        reg_fields_html += (
            f'<div style="margin-bottom:12px;">'
            f'<label style="display:block;margin-bottom:4px;font-size:13px;">{label}</label>'
            f'<input type="text" name="custom_{name}" '
            f'style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box;">'
            f'</div>'
        )

    # =========================
    # SCRIPT JS
    # =========================
    return f"""<script>
(function() {{
    var siteId = {site_id};
    var API = '/api/v1/sites/' + siteId + '/auth';

    function getDisplayName() {{
        var userStr = localStorage.getItem('site_' + siteId + '_user');
        if (!userStr) return null;
        try {{
            var user = JSON.parse(userStr);
            if (user.first_name && user.first_name.trim()) return user.first_name.trim();
            if (user.email) return user.email;
            return null;
        }} catch(e) {{ return null; }}
    }}

    function updateAuthUI() {{
        var token = localStorage.getItem('site_' + siteId + '_token');
        var displayName = getDisplayName();

        document.querySelectorAll('.auth-user-info').forEach(function(div) {{
            var nameEl = div.querySelector('.auth-user-name');
            if (token && displayName) {{
                if (nameEl) nameEl.textContent = 'Hola, ' + displayName + '!';
                div.style.display = 'flex';
            }} else {{
                div.style.display = 'none';
            }}
        }});

        document.querySelectorAll('.auth-login-btn').forEach(function(b) {{
            b.style.display = token ? 'none' : '';
        }});

        document.querySelectorAll('.auth-register-btn').forEach(function(b) {{
            b.style.display = token ? 'none' : '';
        }});
    }}

    // ================= LOGIN =================
    function login(email, pass) {{
        return fetch(API + '/login', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                email: email,
                password: pass
            }})
        }})
        .then(r => r.json().then(d => ({{ ok: r.ok, data: d }})));
    }}

    // ================= REGISTER =================
    function register(data) {{
        return fetch(API + '/register', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(data)
        }})
        .then(r => r.json().then(d => ({{ ok: r.ok, data: d }})));
    }}

    updateAuthUI();
}})();
</script>"""
    

def get_register_script(
    site_id: int,
    site_slug: str,
    registration_fields: List[str] = None,
    custom_fields: List[Dict] = None
) -> str:
    return get_auth_script(site_id, registration_fields, custom_fields)
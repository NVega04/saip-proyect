"""
test_saip_15_vistas_doble_prueba.py
===================================
Suite de automatizacion Selenium para SAIP (Sistema Administrativo Integral de Productos).

Prueba 15 vistas del frontend con DOBLE prueba por vista:
  - Caso NEGATIVO: acceso sin sesion / datos erroneos o formulario vacio
  - Caso POSITIVO: acceso con sesion valida / datos correctos

Estrategias de localizacion usadas: By.ID, By.CSS_SELECTOR, By.XPATH
Evidencias: screenshots PNG en la carpeta actual (una por caso).
Resumen final: total PASS / FAIL por vista y global.

Ejecucion:
    python test_saip_15_vistas_doble_prueba.py
"""

import os
import sys
import time
import traceback
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# ──────────────────────────────────────────────────────────────────────────────
# Configuracion
# ──────────────────────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:5173"
API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@saip.com"
ADMIN_PASSWORD = "admin123"
BAD_EMAIL = "usuario_inexistente@saip.com"
BAD_PASSWORD = "clave_incorrecta_123"

WAIT_TIMEOUT = 12
# Headless por defecto: en maquinas con poca RAM Chrome visible colapsa
# (tab crashed) en vistas tardias. Override con SAIP_HEADLESS=0/1.
HEADLESS = os.environ.get("SAIP_HEADLESS", "1") != "0"
WIN_W, WIN_H = 1366, 768

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS = []  # [(vista, ruta, caso, estado, detalle, screenshot)]
SESSION = {}  # copia del localStorage tras un login valido (token, user, modules)


# ──────────────────────────────────────────────────────────────────────────────
# Setup / Teardown del driver
# ──────────────────────────────────────────────────────────────────────────────
def build_driver():
    """Crea el driver del navegador disponible: Chrome; si no, Firefox."""
    if _chrome_binary_available():
        opts = webdriver.ChromeOptions()
        if HEADLESS:
            opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1366,768")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        # Flags para reducir uso de memoria y evitar "tab crashed"
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-background-networking")
        opts.add_argument("--disable-default-apps")
        opts.add_argument("--disable-sync")
        opts.add_argument("--no-first-run")
        opts.add_argument("--renderer-process-limit=2")
        opts.add_argument("--js-flags=--max-old-space-size=512")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)

    print("Chrome no encontrado -> usando Firefox.")
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions

    fopts = FirefoxOptions()
    if HEADLESS:
        fopts.add_argument("-headless")
    service = FirefoxService(GeckoDriverManager().install())
    return webdriver.Firefox(service=service, options=fopts)


def _chrome_binary_available() -> bool:
    from shutil import which
    return any(
        which(b)
        for b in ("google-chrome", "google-chrome-stable", "chrome", "chromium",
                  "chromium-browser")
    )


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def screenshot(driver, name: str) -> str:
    """Toma captura en la carpeta actual con nombre claro. Retorna el filename."""
    fname = f"{name}_{STAMP}.png"
    try:
        driver.save_screenshot(fname)
    except WebDriverException:
        fname = ""
    return fname


def record(vista: str, ruta: str, caso: str, ok: bool, detalle: str, shot: str):
    RESULTS.append((vista, ruta, caso, "PASS" if ok else "FAIL", detalle, shot))
    icon = "[PASS]" if ok else "[FAIL]"
    print(f"  {icon} {caso:<9} | {vista:<22} | {detalle}")


def goto(driver, path: str):
    driver.get(f"{BASE_URL}{path}")


def wait_visible(driver, locator, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


def wait_clickable(driver, locator, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def accept_terms_modal_if_present(driver) -> bool:
    """Si aparece el modal de Terminos y Condiciones tras el login, lo acepta."""
    try:
        modal = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".saip-modal__box"))
        )
        if "Términos" in modal.text or "Terminos" in modal.text:
            btn = modal.find_element(
                By.XPATH, ".//button[contains(., 'Aceptar y continuar')]"
            )
            btn.click()
            time.sleep(0.5)
            return True
    except TimeoutException:
        pass
    return False


def do_login(driver, email: str, password: str) -> bool:
    """Login desde /login usando By.ID. Retorna True si termina en /dashboard."""
    goto(driver, "/login")

    email_input = wait_visible(driver, (By.ID, "email"))
    pass_input = driver.find_element(By.ID, "password")

    email_input.clear()
    email_input.send_keys(email)
    pass_input.clear()
    pass_input.send_keys(password)

    # Boton submit via CSS_SELECTOR
    submit = wait_clickable(driver, (By.CSS_SELECTOR, "form.login-form .btn-submit"))
    submit.click()

    # Aceptar terminos si el backend lo exige (primer login)
    try:
        WebDriverWait(driver, 4).until(
            lambda d: d.current_url != f"{BASE_URL}/login"
            or d.find_elements(By.CSS_SELECTOR, ".saip-modal__box")
        )
    except TimeoutException:
        pass
    accept_terms_modal_if_present(driver)

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: "/dashboard" in d.current_url
        )
        return True
    except TimeoutException:
        return False


def login_as_admin(driver) -> bool:
    """Garantiza sesion admin activa (login directo si hace falta)."""
    driver.execute_script("window.localStorage.clear();")
    return do_login(driver, ADMIN_EMAIL, ADMIN_PASSWORD)


def capture_session(driver):
    """Guarda una copia del localStorage de la sesion activa."""
    SESSION.clear()
    data = driver.execute_script(
        "const o={}; for (let i=0;i<localStorage.length;i++){"
        "const k=localStorage.key(i); o[k]=localStorage.getItem(k);} return o;"
    )
    SESSION.update(data or {})


def restore_session(driver):
    """Reinyecta el token/estado de sesion guardado sin re-loguear (evita rate-limit)."""
    goto(driver, "/login")
    for k, v in SESSION.items():
        driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);", k, v
        )


def clear_session(driver):
    """Elimina cualquier token/estado de sesion en localStorage."""
    goto(driver, "/login")
    driver.execute_script("window.localStorage.clear();")


def api_request(method: str, path: str, body=None):
    """Llamada HTTP directa al backend usando el token de sesion capturado
    (urllib de stdlib; no requiere dependencias extra)."""
    import json as _json
    import urllib.request as _ur
    token = (SESSION.get("session_token") or "").encode()
    req = _ur.Request(
        f"{API_BASE}{path}",
        method=method,
        data=_json.dumps(body).encode() if body is not None else None,
        headers={
            "Content-Type": "application/json",
            "session-token": token,
        },
    )
    try:
        with _ur.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode()
    except _ur.HTTPError as e:
        return e.code, e.read().decode()


def ensure_unit_available() -> bool:
    """Crea via API una unidad de medida si el catalogo esta vacio, para que la
    vista Crear Producto tenga un <option> seleccionable (el DB limpio no siembra
    unidades). Retorna True si al menos una unidad queda disponible."""
    try:
        status, raw = api_request("GET", "/units/")
        if status != 200:
            return False
        import json as _json
        if _json.loads(raw or "[]"):
            return True
        status, raw = api_request(
            "POST", "/units/",
            {"name": "Kilogramo", "abbreviation": "kg", "quantity": 1},
        )
        return status == 201
    except Exception:
        return False


def restart_driver_with_session(old_driver):
    """Cierra el driver colapsado y abre uno nuevo con la sesion restaurada."""
    try:
        if old_driver:
            old_driver.quit()
    except Exception:
        pass
    d = build_driver()
    d.set_window_size(WIN_W, WIN_H)
    try:
        restore_session(d)
    except Exception:
        pass
    print("  [OK] Navegador reiniciado tras colapso; sesion restaurada.")
    return d


def react_select(driver, select_el, value: str):
    """Selecciona un <option> en un select controlado por React usando el
    setter nativo + eventos (evita que React ignore el cambio)."""
    driver.execute_script(
        """
        const sel = arguments[0], val = arguments[1];
        const proto = window.HTMLSelectElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
        setter.call(sel, val);
        sel.dispatchEvent(new Event('change', {bubbles: true}));
        sel.dispatchEvent(new Event('input',  {bubbles: true}));
        """,
        select_el,
        value,
    )
    time.sleep(0.3)
    if select_el.get_attribute("value") != value:
        Select(select_el).select_by_value(value)
        time.sleep(0.3)


def xpath_ci(texto: str) -> str:
    """XPath contains() insensible a mayusculas/acentos basicos via translate()."""
    may = "ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ"
    minu = "abcdefghijklmnopqrstuvwxyzáéíóúüñ"
    t = texto.translate(str.maketrans(may, minu))
    return (
        f"contains(translate(normalize-space(.), '{may}', '{minu}'), '{t}')"
    )


def is_redirected_away(driver, route: str) -> bool:
    """True si la URL actual ya NO contiene la ruta protegida solicitada."""
    return route not in driver.current_url.replace(BASE_URL, "")


# ──────────────────────────────────────────────────────────────────────────────
# Caso negativo generico para vistas protegidas: acceso SIN token
# ──────────────────────────────────────────────────────────────────────────────
def neg_sin_sesion(driver, vista: str, ruta: str):
    clear_session(driver)
    goto(driver, ruta)
    time.sleep(1.2)  # React Router resuelve <Navigate>
    shot = screenshot(driver, f"{vista}_negativo")
    ok = is_redirected_away(driver, ruta)
    detalle = (
        "Redirigido correctamente al no haber session_token"
        if ok
        else f"Se accedio a {ruta} sin token (deberia redirigir)"
    )
    record(vista, ruta, "NEGATIVO", ok, detalle, shot)


# ──────────────────────────────────────────────────────────────────────────────
# Vistas 1-15: cada funcion ejecuta NEGATIVO + POSITIVO
# ──────────────────────────────────────────────────────────────────────────────
def vista_01_login(driver):
    vista, ruta = "01_Login", "/login"

    # NEGATIVO: credenciales erroneas
    try:
        clear_session(driver)
        goto(driver, ruta)
        email_input = wait_visible(driver, (By.ID, "email"))
        pass_input = wait_visible(driver, (By.ID, "password"))
        email_input.clear()
        email_input.send_keys(BAD_EMAIL)
        pass_input.clear()
        pass_input.send_keys(BAD_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "form.login-form .btn-submit").click()
        # Espera tolerante: el backend responde 401 y api.ts redirige a "/"
        # (la alerta de error normalmente no llega a mostrarse)
        texto_alerta = ""
        for _ in range(16):
            alertas = driver.find_elements(By.CSS_SELECTOR, ".saip-alerta[role='alert']")
            if alertas and alertas[0].is_displayed():
                texto_alerta = alertas[0].text
                break
            if "/login" not in driver.current_url:
                break  # la app redirigio solo ante el rechazo
            time.sleep(0.5)
        shot = screenshot(driver, f"{vista}_negativo")
        rechazado = "/login" not in driver.current_url or texto_alerta
        destino = driver.current_url.replace(BASE_URL, "") or "/"
        ok = rechazado
        detalle = (
            f"Credenciales erroneas rechazadas; la app expulso al usuario a '{destino}'"
            + (f" | Alerta: '{texto_alerta[:50]}'" if texto_alerta else "")
        )
        record(vista, ruta, "NEGATIVO", ok, detalle, shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_negativo_error")
        record(vista, ruta, "NEGATIVO", False,
               f"{type(e).__name__}: {e}", shot)

    # POSITIVO: credenciales correctas
    try:
        clear_session(driver)
        ok_login = do_login(driver, ADMIN_EMAIL, ADMIN_PASSWORD)
        if ok_login:
            capture_session(driver)  # sesion canonica para las demas vistas
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", ok_login,
               f"Login admin exitoso -> {driver.current_url}" if ok_login
               else "No se llego a /dashboard con credenciales validas", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def vista_02_dashboard(driver):
    vista, ruta = "02_Dashboard", "/dashboard"
    neg_sin_sesion(driver, vista, ruta)
    try:
        restore_session(driver)
        goto(driver, ruta)
        # El dashboard no usa .saip-loading: carga stats asincronos. La seccion
        # "Productos terminados" vive en la pestana Productos; validamos el
        # primer bloque real que se renderiza por defecto.
        h3 = wait_visible(driver, (By.XPATH, "//h3[contains(text(),'Consumo diario de insumos')]"))
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", h3.is_displayed(),
               "Dashboard carga con KPIs y grafico 'Consumo diario de insumos'", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def vista_03_productos(driver):
    vista, ruta = "03_Productos", "/products"
    neg_sin_sesion(driver, vista, ruta)
    try:
        restore_session(driver)
        goto(driver, ruta)
        # Espera a que desaparezca el loader y aparezca el boton crear
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".saip-loading"))
        )
        btn = wait_visible(driver, (By.XPATH, "//button[contains(., 'Crear producto')]"))
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", btn.is_displayed(),
               "Listado de productos cargado con boton 'Crear producto'", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def vista_04_crear_producto(driver):
    vista, ruta = "04_CrearProducto", "/products (modal)"

    def abrir_modal():
        wait_clickable(driver, (By.XPATH, "//button[contains(., 'Crear producto')]")).click()
        return wait_visible(driver, (By.CSS_SELECTOR, ".saip-modal__box form.pf"))

    # NEGATIVO: enviar formulario vacio -> errores de validacion
    try:
        restore_session(driver)
        goto(driver, "/products")
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".saip-loading"))
        )
        form = abrir_modal()
        form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        error = wait_visible(driver, (By.CSS_SELECTOR, ".pf__error"))
        shot = screenshot(driver, f"{vista}_negativo")
        record(vista, ruta, "NEGATIVO", error.is_displayed(),
               f"Formulario vacio rechazado: '{error.text[:50]}'", shot)
        # cerrar modal
        try:
            driver.find_element(By.CSS_SELECTOR, ".saip-modal__close").click()
            time.sleep(0.4)
        except NoSuchElementException:
            pass
    except Exception as e:
        shot = screenshot(driver, f"{vista}_negativo_error")
        record(vista, ruta, "NEGATIVO", False,                f"{type(e).__name__}: {e}", shot)

    # POSITIVO: crear producto con datos validos
    nombre_prod = f"Prod Selenium {STAMP}"
    try:
        restore_session(driver)
        goto(driver, "/products")
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".saip-loading"))
        )
        form = abrir_modal()
        inputs = form.find_elements(By.CSS_SELECTOR, "input.pf__input")
        inputs[0].clear()
        inputs[0].send_keys(nombre_prod)          # Nombre *
        selects = form.find_elements(By.CSS_SELECTOR, "select.pf__select")
        sel_el = selects[0]                        # Unidad de medida *
        # Espera a que las unidades (fetch async) carguen en el select.
        # El placeholder es <option value={0}>, se excluyen valores "0"/vacios.
        def hay_unidades(_):
            return any(
                (v or "").strip() not in ("", "0")
                for v in (o.get_attribute("value") for o in Select(sel_el).options)
            )
        WebDriverWait(driver, 8).until(hay_unidades)
        opciones = [
            o.get_attribute("value")
            for o in Select(sel_el).options
            if (o.get_attribute("value") or "").strip() not in ("", "0")
        ]
        if not opciones:
            raise RuntimeError("No hay unidades de medida disponibles en el select")
        react_select(driver, sel_el, opciones[0])
        form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        # Exito = modal se cierra; Fracaso = aparecen errores de validacion
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: (not d.find_elements(By.CSS_SELECTOR, ".saip-modal__box"))
                or d.find_elements(By.CSS_SELECTOR, ".pf__error")
            )
        except TimeoutException:
            pass
        errores = driver.find_elements(By.CSS_SELECTOR, ".pf__error")
        if errores:
            shot = screenshot(driver, f"{vista}_positivo_error")
            record(vista, ruta, "POSITIVO", False,
                   f"El backend/form rechazo el producto: '{errores[0].text[:60]}'", shot)
            return
        fila = None
        try:
            # La tabla pagina a 10 filas: se usa su buscador para filtrar
            buscador = wait_visible(
                driver,
                (By.CSS_SELECTOR, "input[placeholder='Buscar producto']"),
                timeout=5,
            )
            buscador.clear()
            buscador.send_keys(nombre_prod)
            time.sleep(0.8)
            # La tabla renderiza los nombres en MAYUSCULAS: comparacion CI
            fila = wait_visible(
                driver,
                (By.XPATH, f"//td[{xpath_ci(nombre_prod)}]"),
                timeout=6,
            )
        except TimeoutException:
            pass
        shot = screenshot(driver, f"{vista}_positivo")
        ok = fila is not None
        record(vista, ruta, "POSITIVO", ok,
               f"Producto '{nombre_prod}' creado"
               + (" y visible en la tabla" if ok else " (modal cerro; fila no verificada)"),
               shot)
        # Limpieza best-effort del dato creado
        try:
            fila.find_element(
                By.XPATH, "./ancestor::tr//button[contains(@class,'danger')]"
            ).click()
            for texto in ("Eliminar", "Confirmar", "Aceptar", "Sí"):
                try:
                    driver.find_element(
                        By.XPATH, f"//button[normalize-space(.)='{texto}']"
                    ).click()
                    break
                except NoSuchElementException:
                    continue
            time.sleep(0.6)
        except Exception:
            pass
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def _vista_con_titulo(driver, vista: str, ruta: str, xpath_titulo: str, titulo: str):
    """NEGATIVO sin sesion + POSITIVO verificando un titulo/h2 real de la vista."""
    neg_sin_sesion(driver, vista, ruta)
    try:
        restore_session(driver)
        goto(driver, ruta)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".saip-loading"))
        )
        el = wait_visible(driver, (By.XPATH, xpath_titulo))
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", el.is_displayed(),
               f"Vista carga con titulo '{titulo}'", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def _vista_con_boton_crear(driver, vista: str, ruta: str, texto_boton: str):
    """NEGATIVO sin sesion + POSITIVO verificando que la vista y su boton crear cargan."""
    neg_sin_sesion(driver, vista, ruta)
    try:
        restore_session(driver)
        goto(driver, ruta)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".saip-loading"))
        )
        btn = wait_visible(driver, (By.XPATH, f"//button[contains(., '{texto_boton}')]"))
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", btn.is_displayed(),
               f"Vista cargada con boton '{texto_boton}' visible", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def vista_05_inventario(driver):
    _vista_con_titulo(driver, "05_Inventario", "/inventario",
                      "//h2[contains(@class,'inventory__title')]",
                      "Consolidado de inventario")


def vista_06_movimientos(driver):
    # Ruta original /inventario/movimientos no existe -> adaptada a /produccion
    _vista_con_boton_crear(driver, "06_Movimientos_adaptada_produccion", "/produccion",
                           "Nueva orden")


def vista_07_ventas(driver):
    _vista_con_boton_crear(driver, "07_Ventas", "/ventas", "Registrar venta")


def vista_08_nueva_venta(driver):
    # Ruta original /ventas/nueva no existe -> adaptada a /ventas (seccion historial)
    _vista_con_titulo(driver, "08_NuevaVenta_adaptada_historial", "/ventas",
                      "//h2[contains(@class,'sales-hist__title')]",
                      "Historial de ventas")


def vista_09_clientes(driver):
    # Ruta original /clientes no existe -> adaptada a /supplies (insumos)
    _vista_con_boton_crear(driver, "09_Clientes_adaptada_supplies", "/supplies",
                           "Crear insumo")


def vista_10_proveedores(driver):
    _vista_con_boton_crear(driver, "10_Proveedores", "/proveedores", "Crear proveedor")


def vista_11_compras(driver):
    # Ruta original /compras no existe -> adaptada a /units (unidades de medida)
    _vista_con_boton_crear(driver, "11_Compras_adaptada_units", "/units", "Crear unidad")


def vista_12_usuarios(driver):
    _vista_con_boton_crear(driver, "12_Usuarios", "/usuarios", "Crear usuario")


def vista_13_roles(driver):
    _vista_con_boton_crear(driver, "13_Roles", "/roles", "Crear rol")


def vista_14_reportes(driver):
    vista, ruta = "14_Reportes", "/reportes"
    neg_sin_sesion(driver, vista, ruta)
    try:
        restore_session(driver)
        goto(driver, ruta)
        h1 = wait_visible(driver, (By.XPATH, "//h1[contains(text(),'Reportes')]"))
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", h1.is_displayed(),
               "Vista Reportes carga con su titulo", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


def vista_15_configuracion(driver):
    # Ruta original /configuracion no existe -> adaptada a /perfil
    vista, ruta = "15_Configuracion_adaptada_perfil", "/perfil"

    # NEGATIVO: sin token la pagina no debe mostrar datos de usuario
    try:
        clear_session(driver)
        goto(driver, ruta)
        time.sleep(1.5)
        fullname = driver.find_elements(By.CSS_SELECTOR, ".perfil-fullname")
        shot = screenshot(driver, f"{vista}_negativo")
        ok = len(fullname) == 0 or not fullname[0].is_displayed() \
            or not fullname[0].text.strip()
        record(vista, ruta, "NEGATIVO", ok,
               "Sin sesion no se muestran datos personales del perfil", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_negativo_error")
        record(vista, ruta, "NEGATIVO", False,                f"{type(e).__name__}: {e}", shot)

    # POSITIVO: con sesion muestra nombre del usuario
    try:
        restore_session(driver)
        goto(driver, ruta)
        fullname = wait_visible(driver, (By.CSS_SELECTOR, ".perfil-fullname"))
        shot = screenshot(driver, f"{vista}_positivo")
        record(vista, ruta, "POSITIVO", bool(fullname.text.strip()),
               f"Perfil carga datos del usuario: '{fullname.text.strip()[:40]}'", shot)
    except Exception as e:
        shot = screenshot(driver, f"{vista}_positivo_error")
        record(vista, ruta, "POSITIVO", False,                f"{type(e).__name__}: {e}", shot)


# ──────────────────────────────────────────────────────────────────────────────
# Orquestacion
# ──────────────────────────────────────────────────────────────────────────────
VISTAS = [
    vista_01_login,
    vista_02_dashboard,
    vista_03_productos,
    vista_04_crear_producto,
    vista_05_inventario,
    vista_06_movimientos,
    vista_07_ventas,
    vista_08_nueva_venta,
    vista_09_clientes,
    vista_10_proveedores,
    vista_11_compras,
    vista_12_usuarios,
    vista_13_roles,
    vista_14_reportes,
    vista_15_configuracion,
]


def main() -> int:
    print("=" * 78)
    print(" SAIP - Suite Selenium: 15 vistas x doble prueba (negativa + positiva)")
    print(f" Inicio: {datetime.now():%Y-%m-%d %H:%M:%S}   BASE_URL={BASE_URL}")
    print("=" * 78)

    driver = None
    exit_code = 0
    try:
        driver = build_driver()
        driver.set_window_size(WIN_W, WIN_H)

        # vista_01 va primero: su login positivo deja la sesion activa que
        # se captura UNA sola vez (cada nuevo login invalida las sesiones previas)
        print("\n--- vista_01_login ---")
        try:
            vista_01_login(driver)
        except Exception:
            traceback.print_exc()
            record("vista_01_login", "/login", "NEGATIVO", False,
                   "Fallo no controlado en la vista", "")
            record("vista_01_login", "/login", "POSITIVO", False,
                   "Fallo no controlado en la vista", "")

        if not SESSION:
            capture_session(driver)
        if not SESSION.get("session_token"):
            raise RuntimeError(
                "No hay session_token tras vista_01; las vistas protegidas no pueden probarse"
            )
        print(f"\n  [OK] Sesion capturada ({len(SESSION)} claves en localStorage).")

        # Setup de datos: garantiza una unidad de medida para la vista Crear Producto
        if ensure_unit_available():
            print("  [OK] Catalogo de unidades de medida disponible (siembra via API).")
        else:
            print("  [WARN] No se pudo garantizar una unidad de medida.")

        for fn in VISTAS[1:]:
            print(f"\n--- {fn.__name__} ---")
            try:
                fn(driver)
            except WebDriverException as e:
                # Chrome colapso (tab crashed): reinicia el navegador y continua
                traceback.print_exc()
                record(fn.__name__, "-", "NEGATIVO", False,
                       f"Navegador colapsado: {e}", "")
                record(fn.__name__, "-", "POSITIVO", False,
                       f"Navegador colapsado: {e}", "")
                driver = restart_driver_with_session(driver)
            except Exception:
                traceback.print_exc()
                record(fn.__name__, "-", "NEGATIVO", False,
                       "Fallo no controlado en la vista", "")
                record(fn.__name__, "-", "POSITIVO", False,
                       "Fallo no controlado en la vista", "")
    except Exception as e:
        print(f"\nERROR FATAL preparando el navegador: {e}")
        exit_code = 2
    finally:
        if driver:
            try:
                driver.quit()
                print("\nNavegador cerrado correctamente (driver.quit()).")
            except Exception:
                pass

    # ── Resumen final ──
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r[3] == "PASS")
    failed = total - passed

    print("\n" + "=" * 78)
    print(" RESUMEN POR VISTA")
    print("=" * 78)
    vistas = []
    for r in RESULTS:
        if r[0] not in [v[0] for v in vistas]:
            vistas.append(r)
    seen = set()
    for vista, ruta, _, _, _, _ in RESULTS:
        if vista in seen:
            continue
        seen.add(vista)
        casos = [r for r in RESULTS if r[0] == vista]
        p = sum(1 for c in casos if c[3] == "PASS")
        estado = "OK" if p == len(casos) else "FALLO"
        print(f" {vista:<38} {ruta:<20} {p}/{len(casos)} pruebas  [{estado}]")

    print("\n" + "=" * 78)
    print(f" TOTAL: {total} pruebas  |  PASARON: {passed}  |  FALLARON: {failed}")
    print("=" * 78)

    shots = [r[5] for r in RESULTS if r[5]]
    print(f"\n Evidencias (screenshots) generadas: {len(shots)}")
    for s in shots:
        existe = "OK" if os.path.exists(s) else "??"
        print(f"   [{existe}] {s}")

    print(f"\n Fin: {datetime.now():%Y-%m-%d %H:%M:%S}")
    return exit_code if exit_code else (1 if failed else 0)


if __name__ == "__main__":
    sys.exit(main())
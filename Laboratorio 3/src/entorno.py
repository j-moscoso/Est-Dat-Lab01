"""Captura hardware y software para documentarlos automáticamente (requisito de la sustentación)."""
import datetime
import platform
import subprocess
import sys


def _nombre_cpu():
    try:
        if sys.platform.startswith("linux"):
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for linea in f:
                    if linea.lower().startswith("model name"):
                        return linea.split(":", 1)[1].strip()
        elif sys.platform == "darwin":
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True, timeout=10).strip()
        elif sys.platform == "win32":
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
                text=True, timeout=20).strip()
            if out:
                return out
    except Exception:
        pass
    return platform.processor() or "desconocido"


def _version(modulo):
    try:
        return __import__(modulo).__version__
    except Exception:
        return "no instalado"


def capturar_entorno():
    info = {
        "fecha_hora": datetime.datetime.now().isoformat(timespec="seconds"),
        "sistema_operativo": platform.platform(),
        "python": f"{platform.python_implementation()} {platform.python_version()}",
        "cpu": _nombre_cpu(),
        "numpy": _version("numpy"),
        "pandas": _version("pandas"),
        "matplotlib": _version("matplotlib"),
    }
    try:
        import psutil
        info["nucleos_fisicos"] = psutil.cpu_count(logical=False)
        info["nucleos_logicos"] = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq()
        info["frecuencia_cpu_mhz"] = round(freq.max or freq.current) if freq else None
        info["ram_total_gb"] = round(psutil.virtual_memory().total / 2**30, 1)
        bat = psutil.sensors_battery()
        info["conectado_a_corriente"] = None if bat is None else bool(bat.power_plugged)
    except Exception:
        pass
    return info


def advertencias_de_entorno(info):
    """Recomendaciones de las infografías del profesor: equipo estable, sin Colab, con corriente."""
    avisos = []
    if "google.colab" in sys.modules:
        avisos.append("Estás en Google Colab: la variabilidad y los recursos compartidos invalidan las mediciones.")
    if info.get("conectado_a_corriente") is False:
        avisos.append("El portátil está con batería: conéctalo a la corriente (modo 'alto rendimiento') antes de medir.")
    avisos.append("Cierra navegadores, IDEs pesados, videollamadas y descargas antes de ejecutar el experimento completo.")
    return avisos

"""
ULPF Dedicated Desktop & Web Application Launcher.
Bootstraps sample logs, starts local FastAPI/Uvicorn server, and opens default web browser.
"""
import os
import sys
import time
import threading
import traceback
import webbrowser
from pathlib import Path

# Auto-register all parsers
import ulpf.parsers  # noqa: F401
from ulpf.dashboard.app import create_app, _resolve_output_dir, _find_sample_logs_dir, find_available_port
from ulpf.core.ingestion import FileReader
from ulpf.cli import _build_pipeline, _find_schema_dir, _find_config_dir
import uvicorn


def print_banner(port: int, output_dir: Path):
    print("")
    print("========================================================================")
    print("        Universal Log Pre-processing Framework (ULPF) App Launcher       ")
    print("========================================================================")
    print(f"  [+] Status:              ONLINE")
    print(f"  [+] Dashboard URL:       http://127.0.0.1:{port}")
    print(f"  [+] Storage Directory:   {output_dir.resolve()}")
    print(f"  [+] Registered Parsers:  11 Formats (CEF, LEEF, Syslog, XML, Cloud, CSV)")
    print("========================================================================")
    print("  Opening web browser automatically...")
    print("  To stop the application, close this window or press Ctrl+C.")
    print("========================================================================")
    print("")


def bootstrap_sample_data_if_needed(output_dir: Path) -> None:
    events_file = output_dir / "events.ndjson"
    if not events_file.exists() or events_file.stat().st_size == 0:
        sample_dir = _find_sample_logs_dir()
        if sample_dir and sample_dir.exists():
            print(f"[*] First launch detected: initializing sample logs into {output_dir}...")
            try:
                p, s, v = _build_pipeline(
                    output=output_dir,
                    schema_dir=_find_schema_dir(),
                    cfg=_find_config_dir() / "sources.yaml",
                    sink_type="ndjson",
                    enrich=True,
                )
                reader = FileReader(str(sample_dir))
                stats = p.run(reader)
                v.close()
                for snk in s:
                    snk.close()
                print(f"[+] Successfully loaded {stats['valid']} sample events into {output_dir}")
            except Exception as e:
                print(f"[!] Sample data initialization note: {e}")


def launch_browser(url: str, delay: float = 1.0) -> None:
    def _open():
        time.sleep(delay)
        try:
            if sys.platform == "win32":
                os.startfile(url)
            else:
                webbrowser.open(url)
        except Exception:
            webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("ULPF Operations Dashboard")
        except Exception:
            pass

    host = "127.0.0.1"
    port = find_available_port(host=host, start_port=8000)
    output_dir = _resolve_output_dir(None)

    bootstrap_sample_data_if_needed(output_dir)
    print_banner(port, output_dir)

    url = f"http://{host}:{port}"
    launch_browser(url, delay=1.2)

    app = create_app(output_dir=output_dir)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[+] ULPF Operations Dashboard stopped by user.")
    except Exception as e:
        print("\n" + "=" * 72)
        print("  [ERROR] An unexpected error occurred while running ULPF:")
        print("=" * 72)
        traceback.print_exc()
        print("=" * 72)
        try:
            input("\nPress Enter to exit...")
        except Exception:
            pass

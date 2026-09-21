import os
import sys
import httpx
import zipfile
import subprocess
from pathlib import Path


def download_file(url: str, dest: str):
    print(f"Downloading {url}...")
    with httpx.Client(follow_redirects=True, timeout=300.0) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r  {pct:.1f}% ({downloaded}/{total})", end="", flush=True)
    print(f"\n  Saved to: {dest}")


def get_llama_cpp_url():
    return "https://github.com/ggml-org/llama.cpp/releases/latest/download/llama-ubuntu-arm64-vulkan.zip"


def download_model():
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    model_url = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
    model_path = models_dir / "qwen2.5-3b-instruct-q4_k_m.gguf"

    if model_path.exists():
        print(f"Model already exists: {model_path}")
        return

    download_file(model_url, str(model_path))


def download_llama_cpp():
    llama_dir = Path("llama.cpp")
    if llama_dir.exists() and any(llama_dir.glob("*.exe")):
        print("llama.cpp already downloaded")
        return

    print("Downloading llama.cpp...")
    zip_url = "https://github.com/ggml-org/llama.cpp/releases/latest/download/llama-ubuntu-arm64-vulkan.zip"
    zip_path = "llama.zip"

    download_file(zip_url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(".")

    os.remove(zip_path)
    print("llama.cpp extracted")


def start_server():
    llama_dir = Path("llama.cpp")
    server_exe = list(llama_dir.glob("**/llama-server*"))

    if not server_exe:
        print("llama-server not found. Run download first.")
        return

    server = server_exe[0]
    model = "models/qwen2.5-3b-instruct-q4_k_m.gguf"

    cmd = [str(server), "-m", model, "-c", "4096", "--host", "127.0.0.1", "--port", "8080"]
    print(f"Starting: {' '.join(cmd)}")
    subprocess.run(cmd)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "model":
            download_model()
        elif sys.argv[1] == "llama":
            download_llama_cpp()
        elif sys.argv[1] == "start":
            start_server()
        else:
            print("Usage: python setup.py [model|llama|start]")
    else:
        download_model()
        download_llama_cpp()

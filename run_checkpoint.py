"""
Run a checkpoint session without conflicting with the top-level app/ folder.

Usage:
    python run_checkpoint.py session-03-embeddings
    python run_checkpoint.py session-06-logging
    python run_checkpoint.py --restore   (if app/ was not restored after a crash)

The script temporarily renames app/ → _app_dev/ so Python finds
the checkpoint's app/ package instead of the top-level one.
On exit (Ctrl+C), it restores the folder automatically.
"""

import sys
import os

import uvicorn


def main():
    # Handle --restore flag
    if len(sys.argv) == 2 and sys.argv[1] == "--restore":
        if os.path.isdir("_app_dev") and not os.path.isdir("app"):
            os.rename("_app_dev", "app")
            print("[runner] Restored app/ from _app_dev/.")
        elif os.path.isdir("app"):
            print("[runner] app/ already exists, nothing to restore.")
        else:
            print("[runner] Neither app/ nor _app_dev/ found.")
        sys.exit(0)

    if len(sys.argv) < 2:
        # Auto-recover from previous crash before showing help
        if os.path.isdir("_app_dev") and not os.path.isdir("app"):
            os.rename("_app_dev", "app")
            print("[runner] Recovered app/ from previous interrupted run.")

        print("Usage: python run_checkpoint.py <session-folder-name>\n")
        print("Available checkpoints:")
        checkpoints_dir = "checkpoints"
        if os.path.isdir(checkpoints_dir):
            for d in sorted(os.listdir(checkpoints_dir)):
                if os.path.isdir(os.path.join(checkpoints_dir, d)):
                    print(f"  {d}")
        sys.exit(1)

    session = sys.argv[1]
    checkpoint = os.path.join("checkpoints", session)

    if not os.path.isdir(checkpoint):
        print(f"Error: {checkpoint} not found")
        sys.exit(1)

    # Auto-recover from previous crash
    if os.path.isdir("_app_dev") and not os.path.isdir("app"):
        os.rename("_app_dev", "app")
        print("[runner] Recovered app/ from previous interrupted run.")

    # Temporarily hide top-level app/ to avoid import conflicts
    renamed = False
    if os.path.isdir("app"):
        os.rename("app", "_app_dev")
        renamed = True
        print(f"[runner] Temporarily renamed app/ -> _app_dev/")

    try:
        print(f"[runner] Starting {session} on http://localhost:8000")
        print(f"[runner] Swagger UI: http://localhost:8000/docs")
        print(f"[runner] Press Ctrl+C to stop\n")
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_dirs=[checkpoint],
            app_dir=checkpoint,
        )
    finally:
        if renamed and os.path.isdir("_app_dev"):
            os.rename("_app_dev", "app")
            print(f"\n[runner] Restored _app_dev/ -> app/")


if __name__ == "__main__":
    main()

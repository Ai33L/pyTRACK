import os
import ctypes

def main():
    # Path to the installed package
    import pyTRACK
    lib_path = os.path.join(os.path.dirname(pyTRACK.__file__), "_lib", "libtrack.so")

    print(f"Checking if libtrack.so exists at: {lib_path}")
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"libtrack.so not found at {lib_path}")

    try:
        # Load the library
        lib = ctypes.CDLL(lib_path)
        print("libtrack.so loaded successfully!")

        # Check if track_main symbol exists
        if hasattr(lib, "track_main"):
            print("track_main symbol found in library ✅")
        else:
            print("track_main symbol NOT found ❌")
    except Exception as e:
        print("Error loading libtrack.so:", e)

if __name__ == "__main__":
    main()

import importlib


def run_all_figures():
    # List of figure generation scripts (without .py extension)
    figure_scripts = [
        "figure1",
        "figure2",
        "figure3",
        "figure4",
        "sup_figure1",
        "sup_figure2",
        "sup_figure3",
        "sup_figure4",
    ]

    for script in figure_scripts:
        try:
            module = importlib.import_module(script)
            if hasattr(module, "main"):
                print(f"Running {script}.main()...")
                module.main()
            else:
                print(f"Skipping {script}: no main() function found.")
        except Exception as e:
            print(f"Error running {script}: {e}")

if __name__ == "__main__":
    run_all_figures()

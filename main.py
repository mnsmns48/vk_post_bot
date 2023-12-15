from autoposting.start import start_autoposting


def main():
    start_autoposting()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

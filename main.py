import argparse
import os
import sys
from pathlib import Path

from staticjinja import Site


def get_context() -> dict[str, str]:
    context = {}
    prefix = "SJP_"

    for key, value in os.environ.items():
        if key.startswith(prefix):
            context[key.removeprefix(prefix).lower()] = value

    return context


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render HTML pages from Jinja templates",
    )
    parser.add_argument(
        "-w",
        "--watch",
        help="Render the site, and re-render on changes to <srcpath>",
        action="store_true",
    )
    parser.add_argument(
        "--srcpath",
        help="The directory to look in for templates (defaults to './wireframes')",
        default=Path(".") / "wireframes",
        type=Path,
    )
    parser.add_argument(
        "--outpath",
        help="The directory to place rendered files in (defaults to './rendered_pages')",
        default=Path(".") / "rendered_pages",
        type=Path,
    )

    args = parser.parse_args()

    src_path = args.srcpath
    output_path = args.outpath
    static_path = src_path / "assets"

    if not src_path.exists():
        raise FileNotFoundError(
            f"Не найден каталог с файлами для рендера: {src_path}"
        )

    if not src_path.is_dir():
        raise NotADirectoryError(
            f"Указанный путь не является каталогом: {src_path}"
        )

    templates = list(src_path.glob("*.html"))
    if not templates:
        raise FileNotFoundError(
            f"В каталоге {src_path} не найдены исходные HTML-файлы для рендера"
        )

    unreadable_templates = [template for template in templates if not os.access(template, os.R_OK)]
    if unreadable_templates:
        unreadable_paths = "\n".join(str(path) for path in unreadable_templates)
        raise PermissionError(
            "Нет доступа на чтение файлов для рендера:\n"
            f"{unreadable_paths}"
        )

    site = Site.make_site(
        searchpath=str(src_path),
        outpath=output_path,
        staticpaths=[str(static_path)],
        contexts=[(".*.html", get_context)],
    )

    site.render(use_reloader=args.watch)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as error:
        print(f"Ошибка доступа: {error}", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f"Неизвестная ошибка: {error}", file=sys.stderr)
        sys.exit(1)
.PHONY: test run package-windows package-windows-alt package-windows-docker package-windows-script

test:
	poetry run pytest tests/

run:
	poetry run python game.py

package-windows:
	poetry run pyinstaller --onefile --windowed --name ludum --add-data "assets:assets" --add-data "audio:audio" --add-data "sprites:sprites" --add-data "config:config" --add-data "engine:engine" --add-data "objects:objects" --add-data "rain:rain" --add-data "utils:utils" game.py

package-windows-alt:
	python -m pip install pyinstaller
	python -m PyInstaller --onefile --windowed --name ludum --add-data "assets:assets" --add-data "audio:audio" --add-data "sprites:sprites" --add-data "config:config" --add-data "engine:engine" --add-data "objects:objects" --add-data "rain:rain" --add-data "utils:utils" game.py

package-windows-docker:
	docker build -f Dockerfile.packaging -t ludum-packager .
	docker run --rm -v "$(PWD)/dist:/app/dist" ludum-packager
	@echo "Executable created in dist/ directory"

package-windows-script:
	python package_windows.py --windows
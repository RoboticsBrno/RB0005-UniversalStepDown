web: build/web build/web/index.html build/web/eval5v build/web/eval3v3 build/web/index.html build/web/eval5v_v2

build/web:
	mkdir -p build/web/resources

build/web/index.html: evaluation/assets/header.jpg evaluation/assets/style.css
	cp evaluation/assets/header.jpg evaluation/assets/style.css \
		evaluation/assets/normalize.css evaluation/assets/skeleton.css \
	    build/web/resources/
	pandoc -o $@ --template evaluation/template.pandoc -s --metadata pagetitle="RB0005" README.md
	sed -i 's/evaluation\/assets/resources/g' $@

build/web/eval5v: evaluation/plot.py evaluation/data/v0.1-5V.csv
	cd evaluation && ./plot.py template.handlebars \
		data/v0.1-5V.csv \
		../build/web/eval5v \
		--pagename "Performance of UniversalStepdown 5V version"


build/web/eval3v3: evaluation/plot.py evaluation/data/v0.1-3V3.csv
	cd evaluation && ./plot.py template.handlebars \
		data/v0.1-3V3.csv \
		../build/web/eval3v \
		--pagename "Performance of UniversalStepdown 3V3 version"

build/web/eval5v_v2: evaluation/plot.py evaluation/data/v0.2-5V.csv
	cd evaluation && ./plot.py template.handlebars \
		data/v0.2-5V.csv \
		../build/web/eval5v_v2 \
		--pagename "Performance of UniversalStepdown v0.2 5V version"
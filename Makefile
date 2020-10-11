
.PHONY: clean

all: build/stepDown3V3-panel build/stepDown5V-panel

build:
	mkdir -p build

build/stepDown3V3.kicad_pcb: board/universalStepDown.kicad_pcb build
	sed 's/VOLTAGE_VARIANT/3V3/g' $< > $@

build/stepDown5V.kicad_pcb: board/universalStepDown.kicad_pcb build
	sed 's/VOLTAGE_VARIANT/5V/g' $< > $@

build/%-panel.kicad_pcb: build/%.kicad_pcb
	kikit panelize grid -s 2 -g 4 4 --tabwidth 2.5 --tabheight 2.5 --tolerance 40  \
		--mousebites 0.2 0.35 0 --radius 0.75 --railsTb 5 \
		--tooling 2.5 2.5 1.152 \
		$< $@

build/stepDown3V3-panel: build/stepDown3V3-panel.kicad_pcb board/universalStepDown.sch
	kikit fab jlcpcb --assembly --schematic board/universalStepDown.sch \
		--missingError --field LCSC_3V3,LCSC \
		--ignore J1 \
		$< $@

build/stepDown5V-panel: build/stepDown5V-panel.kicad_pcb board/universalStepDown.sch
	kikit fab jlcpcb --assembly --schematic board/universalStepDown.sch \
		--missingError --field LCSC_5V,LCSC \
		--ignore J1 \
		$< $@

clean:
	rm -rf build
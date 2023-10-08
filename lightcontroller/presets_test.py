reactors = [
	"zylinder"
]

palettes = [
	[ # palette 1, the entire hue spectrum divided equally into 8 colors
		"FF0000", "FFBF00", "80FF00", "00FF40", "00FFFF", "0040FF", "8000FF", "FF00BF"
	]
]
presets = {
	0: { # simple sync on bass, for drops
		"zylinder": {
			"preset": [
				("focus", "simpleSync"),
				("input/channel", "256"),
				("input/smooth", "5"),
			],
			"variations": {
				0: [("input/colorindex", "0")],
				1: [("input/colorindex", "2")],
				2: [("input/colorindex", "4")],
				3: [("input/colorindex", "6")],
			},
		},
	},
	1: { # barFadeStereoSync
		"zylinder": {
			"preset": [
				("focus", "barSync"),
				("input/smooth", "0"),
			],
			"variations": {
				0: [("input/colorindex", "0")],
				1: [("input/colorindex", "2")],
				2: [("input/colorindex", "4")],
				3: [("input/colorindex", "6")],
				4: [("input/orientation", "H"), ("input/direction", "OUT"), ("input/interval", "2")],
				5: [("input/direction", "U"), ("input/interval", "4")],
				6: [("input/direction", "D"), ("input/interval", "4")],
			},
		},
	},
	2: { # rippleSync, good for calm sections
		"zylinder": {
			"preset": [
				("focus", "rippleSync"),
				("input/channel", "0"),
				("input/smooth", "5"),
			],
			"variations": {
				0: [("input/colorindex", "0")],
				1: [("input/colorindex", "2")],
				2: [("input/colorindex", "4")],
				3: [("input/colorindex", "6")],
				4: [("input/orientation", "H"), ("input/direction", "OUT"), ("input/interval", "2")],
				5: [("input/direction", "U"), ("input/interval", "4")],
				6: [("input/direction", "D"), ("input/interval", "4")],
			},
		},
	},
	3: { # hotbutton flashes, for cool shit
		"zylinder": {
			"preset": [
				("focus", "simpleHB"),
			],
			"variations": {
				0: [("input/colorindex", "0")],
				1: [("input/colorindex", "2")],
				2: [("input/colorindex", "4")],
				3: [("input/colorindex", "6")],
				4: [("input/strips", "1")],
				5: [("input/strips", "4")],
				6: [("input/strips", "8")],
				7: [("input/orientation", "H")],
				8: [("input/orientation", "V")],
			},
		},
    },
}
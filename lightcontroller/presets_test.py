reactors = [
	"zylinder",
	"zylinder_leo"
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
		"zylinder_leo": {
			"preset": [
				("focus", "simpleSync"),
				("input/channel", "256"),
				("input/smooth", "5"),
			],
			"variations": {
				0: [("input/colorindex", "3")],
				1: [("input/colorindex", "5")],
				2: [("input/colorindex", "7")],
				3: [("input/colorindex", "1")],
			},
		},
	},
	1: { # barFadeStereoSync
		"zylinder": {
			"preset": [
				("focus", "barSync"),
				("input/channel", "128"),
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
		"zylinder_leo": {
			"preset": [
				("focus", "barSync"),
				("input/channel", "129"),
				("input/smooth", "0"),
			],
			"variations": {
				0: [("input/colorindex", "3")],
				1: [("input/colorindex", "5")],
				2: [("input/colorindex", "7")],
				3: [("input/colorindex", "1")],
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
				("input/channel", "128"),
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
		"zylinder_leo": {
			"preset": [
				("focus", "rippleSync"),
				("input/channel", "129"),
				("input/smooth", "5"),
			],
			"variations": {
				0: [("input/colorindex", "3")],
				1: [("input/colorindex", "5")],
				2: [("input/colorindex", "7")],
				3: [("input/colorindex", "1")],
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
				5: [("input/strips", "2"), ("input/orientation", "H")],
				6: [("input/strips", "4"), ("input/orientation", "H")],
				7: [("input/strips", "8"), ("input/orientation", "V")],
			},
		},
		"zylinder_leo": {
			"preset": [
				("focus", "simpleHB"),
			],
			"variations": {
				0: [("input/colorindex", "0")],
				1: [("input/colorindex", "2")],
				2: [("input/colorindex", "4")],
				3: [("input/colorindex", "6")],
				4: [("input/strips", "1"), ("input/offset", "1")],
				5: [("input/strips", "2"), ("input/offset", "2"), ("input/orientation", "H")],
				6: [("input/strips", "4"), ("input/offset", "4"), ("input/orientation", "H")],
				7: [("input/strips", "7"), ("input/offset", "0"), ("input/orientation", "V")],
			},
		},
    },
}
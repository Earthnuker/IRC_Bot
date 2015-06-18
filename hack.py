import random
markers={
	"abbreviation":["TCP","HTTP","SDD","RAM","GB","CSS","SSL","AGP","SQL","FTP","PCI","AI","ADP","RSS","XML","EXE","COM","HDD","THX","SMTP","SMS","USB","PNG","SAS","IB","SCSI","JSON","XSS","JBOD"],
	"adjective":["auxiliary","primary","back-end","digital","open-source","virtual","cross-platform","redundant","online","haptic","multi-byte","bluetooth","wireless","1080p","neural"," optical","solid state","mobile"],
	"noun":["driver","protocol","bandwidth","panel","microchip","program","port","card","array","interface","system","sensor","firewall","hard drive","pixel","alarm","feed","monitor","application","transmitter","bus","circuit","capacitor","matrix"],
	"verb":["back up","bypass","hack","override","compress","copy","navigate","index","connect","generate","quantify","calculate","synthesize","input","transmit","program","reboot","parse"],
	"ingverb":["backing up","bypassing","hacking","overriding","compressing","copying","navigating","indexing","connecting","generating","quantifying","calculating"," synthesizing","transmitting","programming","parsing"],
}
phrases=[
	"If we {verb} the {noun}, we can get to the {abbreviation} {noun} through the {adjective} {abbreviation} {noun}!",
	"We need to {verb} the {adjective} {abbreviation} {noun}!",
	"Try to {verb} the {abbreviation} {noun}, maybe it will {verb} the {adjective} {noun}!",
	"You can't {verb} the {noun} without {ingverb} the {adjective} {abbreviation} {noun}!",
	"Use the {adjective} {abbreviation} {noun}, then you can {verb} the {adjective} {noun}!",
	"The {abbreviation} {noun} is down, {verb} the {adjective} {noun} so we can {verb} the {abbreviation} {noun}!",
	"{ingverb} the {noun} won't do anything, we need to {verb} the {adjective} {abbreviation} {noun}!",
	"I'll {verb} the {adjective} {abbreviation} {noun}, that should {noun} the {abbreviation} {noun}!"
]
def run():
	phrase=random.choice(phrases)
	for marker in markers:
		while "{"+marker+"}" in phrase:
			phrase=phrase.replace("{"+marker+"}",random.choice(markers[marker]),1)
	return phrase
if __name__=="__main__":
	print(run())
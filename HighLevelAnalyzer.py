from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

class Hla(HighLevelAnalyzer):
	data_type = ChoicesSetting(['Tx', 'Rx'])

	result_types = {
		'match': {
			'format': '{{data.data}}'
		},
	}

	def __init__(self):
		self.cmd_start_time = None
		self.cmd_end_time = None
		self.cmd = []
		self.cmdInfo = ""
		
	def parseCmd(self, cmd, msb, lsb):
		cmdDict = {
			0x01: {'Tx':['Play Next track', 'none'], 'Rx':[]},
			0x02: {'Tx':['Play Previous track', 'none'], 'Rx':[]},
			0x03: {'Tx':['Playback track {} in root folder', 'msb+lsb'], 'Rx':[]},
			0x04: {'Tx':['Increase volume', 'none'], 'Rx':[]},
			0x05: {'Tx':['Decrease volume', 'none'], 'Rx':[]},
			0x06: {'Tx':['Set volume to {}', 'lsb'], 'Rx':[]},
			0x07: {'Tx':['Set EQ to {}', 'parselsb', {0:'Normal', 1:'Pop', 2:'Rock', 3:'Jazz', 4:'Classic', 5:'Bass'}], 'Rx':[]},
			0x08: {'Tx':['Set Single REPEAT to track {}', 'msb+lsb'], 'Rx':[]},
			0x09: {'Tx':['Specify {} to play', 'parselsb', {0:'USB Stick', 2:'SD Card', 4:'USB cable to PC'}], 'Rx':[]},
			0x0A: {'Tx':['Set Sleep', 'none'], 'Rx':[]},
			0x0C: {'Tx':['Reset', 'none'], 'Rx':[]},
			0x0D: {'Tx':['Play', 'none'], 'Rx':[]},
			0x0E: {'Tx':['Pause', 'none'], 'Rx':[]},
			0x0F: {'Tx':['Play track {} from folder {}', 'msb:lsb'], 'Rx':[]},
			0x10: {'Tx':['Audio amplification setting to {}', 'lsb'], 'Rx':[]},
			0x11: {'Tx':['Set all repeat playback', 'lsb'], 'Rx':[]},
			0x12: {'Tx':['Play track {} from MP3 folder', 'msb+lsb' ], 'Rx':[]},
			0x13: {'Tx':['Play track {} from ADVERT folder', 'msb+lsb' ], 'Rx':[]},
			0x15: {'Tx':['Stop advertisement and go back to interrupted music', 'none'], 'Rx':[]},
			0x16: {'Tx':['Stop', 'none'], 'Rx':[]},
			0x17: {'Tx':['Set folder {} to REPEAT playback', 'lsb'], 'Rx':[]},
			0x18: {'Tx':['Set RANDOM playback', 'none'], 'Rx':[]},
			0x19: {'Tx':['Set REPEAT playback of current track', 'none'], 'Rx':[]},
			0x1A: {'Tx':['Set DAC: {}', 'parselsb', {0x00:'Turn ON', 0x01:'Turn OFF'}], 'Rx':[]},
			0x3A: {'Tx':[], 'Rx':['Storage {} is plugged in', 'parselab', {1:'USB Stick', 2:'SD Card', 4:'USB cable to PC'}]},
			0x3B: {'Tx':[], 'Rx':['Storage {} is pulled out :', 'parselab', {1:'USB Stick', 2:'SD Card', 4:'USB cable to PC'}]},
			0x3C: {'Tx':[], 'Rx':['USB Stick finish playing track {}', 'msb+lsb']},
			0x3D: {'Tx':[], 'Rx':['SD Card finish playing track {}', 'msb+lsb']},
			0x3E: {'Tx':[], 'Rx':['USB cable to PC finish playing track {}', 'msb+lsb']},
			0x3F: {'Tx':['Query current online storage', 'none'], 'Rx':['(PowerOn Report) Current online storage: {}', 'parselsb', { 0x0:'None', 0x01:'USB Stic', 0x02:'SD Card', 0x03:'USB Stick & SD Card', 0x04:'PC', 0x0F:'SD Card & USB Stick & PC'}]},
			0x40: {'Tx':[], 'Rx':['Module returns error', 'parselsb', {1:'Module Busy', 2:'Currently sleep mode', 3:'Serial rx error', 4:'Checksum incorrect', 5:'Track out of scope', 6:'Track not found', 7:'Insertion error', 8:'SD card reading failed', 9:'Entered into sleep mode'}]},
			0x41: {'Tx':[], 'Rx':['Module ACK', 'none']},
			0x42: {'Tx':['Query current status', 'none'], 'Rx':['Report current status: {}', 'parsemsb+lsb', {0:'' ,1:'USB Stick', 2:'SD Card', 3:'Module in sleep mode'}, {0:'Stopped', 1:'Playing', 2:'Paused'}]},
			0x43: {'Tx':['Query current volume', 'none'], 'Rx':['Report current volume', 'lsb']},
			0x44: {'Tx':['Query current EQ', 'none'], 'Rx':['Report current EQ', 'parselsb', {0:'Normal', 1:'Pop', 2:'Rock', 3:'Jazz', 4:'Classic', 5:'Bass'}]},
			0x47: {'Tx':['Query number of tracks in root of USB Stick', 'none'], 'Rx':['There are {} tracks in root of USB Stick', 'msb+lsb']},
			0x48: {'Tx':['Query number of tracks in root of SD Card', 'none'], 'Rx':['There are {} tracks in root of SD Card', 'msb+lsb']},
			0x4B: {'Tx':['Query current track in USB Stick', 'none'], 'Rx':['Current playing track in USB Stick: {}', 'msb+lsb']},
			0x4C: {'Tx':['Query current track in SD Card', 'none'], 'Rx':['Current playing track in SD Card: {}', 'msb+lsb']},
			0x4E: {'Tx':['Query number of tracks in folder {}', 'lsb'], 'Rx':['There are {} tracks in folder', 'lsb']},
			0x4F: {'Tx':['Query number of folders in current storage', 'none'], 'Rx':['There are {} folders in current storage', 'lsb']},
		}

		#print("cmd = %x, msb = %x, lsb = %x" % (cmd, msb, lsb))
		
		try:
			info = cmdDict[cmd][self.data_type]
		except:
			print("Unknown command: %x %x %x" % (cmd, msb, lsb))
			return ''
			
		if (info[1] == 'none'):
			message = info[0]
		else:
			if (info[1] == 'lsb'):
				message = info[0].format(lsb)
			elif (info[1] == 'msb+lsb'):
				message = info[0].format(msb * 256 + lsb)
			elif (info[1] == 'msb:lsb'):
				message = info[0].format(msb,lsb)
			elif (info[1] == 'parsemsb+lsb'):
				if (info[2][msb] == ''):
					message = info[0]
				else:
					message = info[0].format(info[2][msb] + ' ' + info[3][lsb])
			elif (info[1] == 'parselsb'):
				message = info[0].format(info[2][lsb])
				
		print(hex(cmd) + ' ' + message)
		return '['+ hex(cmd) + '] ' + message

	def decode(self, frame: AnalyzerFrame):
		ch = frame.data['data'][0]

		if (ch == 0x7E):
			self.cmd.clear()
			self.cmd.append(ch)
			self.cmd_start_time = frame.start_time
		else:
			self.cmd.append(ch)
			if (ch==0xEF):
				self.cmd_end_time = frame.end_time
		
		if (len(self.cmd)==10):
			self.cmdInfo = self.parseCmd(self.cmd[3], self.cmd[5], self.cmd[6])
			return AnalyzerFrame('match', self.cmd_start_time, self.cmd_end_time, {
				'data': self.cmdInfo
			})


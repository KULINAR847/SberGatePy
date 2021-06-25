import ctypes
import os
from ctypes import *
from ctypes import wintypes
import sys
import functools
import serial.tools.list_ports

KO_INITIALIZATION = 0
KO_FINALIZATION = 1
KO_FUNCTIONS_COUNT = 2
KO_SIZE_OF_CHEQUE = 4
KO_GET_LAST_CHEQUE = 5
KO_GET_ERROR_TEXT = 14
KO_SALE = 4000 
KO_REFUND = 4002
KO_TOTALS = 6000
KO_COMMIT_TRANSACTION = 6001
KO_SUSPEND_TRANSACTION = 6003
KO_ROLLBACK_TRANSACTION = 6004
KO_FULL_REPORT = 7000
KO_TEST_PINPAD = 7003
KO_GET_TERMINAL_AND_MERCHENT_ID = 7007

MAX_TRACK2 = 40
MAX_NAME = 38  #///< Длина названия карты (Visa, Maestro, ...)
MAX_DATE = 10  #///< Длина строки даты (ДД.ММ.ГГГГ)
MAX_TIME = 8  #///< Длина времени операции (ЧЧ:ММ:СС)
MAX_TERM = 8
MAX_MERCHANT_LN = 15
MAX_AUTH_CODE = 6
MAX_RRN = 12
MAX_CARD_NUM = 30
MAX_PAN_N = 19
MAX_CARD_DATE = 4
MAX_PAYMENT_TAG = 32
MAX_PAYMENT_VALUE = 200
MAX_FIO_N = 58
MAX_TEXT_MESSAGE = 700
MAX_GOODS_NAME = 25
MAX_GOODS_CODE = 24
MAX_CLIENT_NAME = 80
MAX_CARD_LS_DATA = 800
MAX_HASH = 20

KERNEL_MINIMAL_VERSION = 0x00030101
DEPARTMENT_NOT_SPECIFIED = 0xFFFFFFFF
F_HAVE_DOCUMENT = 0x00000001
ERR_OK = 0

import json
def read_file():
	filename = 'errors.json'
	if os.path.exists(filename):
		with open('errors.json', encoding='utf-8') as f:
			return json.loads(f.read())
	return {}

class TdisTCPTrxInfo:
	def __init__(self):
		self.Id = None
		self.CardType = None
		self.TermNum = None
		self.AuthCode = None
		self.MerchTSN = None
		self.MerchBatch = None
		self.CardName = None
		self.CardNum = None
		self.ExpDate = None
		self.RRN = None
		self.SignIsReq = None
		self.IsSbrf = None

def hex_2_ascii(source, sz):
	destn = []
	i = 0
	j = 0
	for _ in range(sz):
		c = source[j]
		if c < 0:
			c = 256 + c

		a = c >> 4
		if int(a) <= 9:
			destn.append(  a + ord('0')  )
		else:
			destn.append(  a + ord('7')  )
		
		c = source[j]
		if c < 0:
			c = 256 + c
		j = j + 1
		a = int(c) & 0x0f

		if int(a) <= 9:
			destn.append(  a + ord('0')  )
		else:
			destn.append(  a + ord('7')  )
	destn = ''.join( list( map(chr, destn) ) )
	return destn

class struct_in0(ctypes.Structure):
	_fields_ = [
		("AppVersion", wintypes.DWORD),
		("UIData", c_void_p),
		("Reserved", c_void_p)
	]

class struct_in_cl4(ctypes.Structure):
	_fields_ = [
		("Amount", wintypes.DWORD),
		("Track2", c_char * (MAX_TRACK2 + 1)),
		("CardType", wintypes.BYTE)
	]
	
class struct_in_cl5(ctypes.Structure):
	_fields_ = [		
		("Track2", c_char * (MAX_TRACK2 + 1)),		
		("CardType", wintypes.BYTE)
	]

class struct_out13(ctypes.Structure):
	_fields_ = [
		("Model", wintypes.BYTE), # ///< Модель пинпада
		("Version", wintypes.BYTE), # ///< Номер версии планового прелиза.
		("Release", wintypes.BYTE), #  ///< Номер версии срочного релиза.
		("Build", wintypes.BYTE), # ///< Номер версии сборки.
		("HasCtls", wintypes.BYTE), # ///< Признак "бесконтактный считыватель в наличии и включен".
		("bPPScreenWidth", wintypes.BYTE), # ///< Ширина экрана пинпада
		("bPPScreenHeight", wintypes.BYTE), # ///< Высота экрана пинпада
		("SN", c_char * (12 + 1))		 # ///< Серийный номер пинпада
	]

class struct_in13(ctypes.Structure):
	_fields_ = [
		("ScrId", wintypes.DWORD), #///< Устаревшее поле. Не используется. Долен быть равен 0.
		("DlgNum", c_int), #///< Устаревшее поле. Не используется. Долен быть равен 0.
		("RFU", wintypes.BYTE * 56) # ///< Устаревшее поле. Не используется. Долен быть равен 0.
	]

class EnumStruct(ctypes.Structure):
	_fields_ = [
		("FuncID", wintypes.DWORD),
		("Options", wintypes.DWORD),
		("Name", c_char * 64)
	]

class TBatchRecord(ctypes.Structure):
	_fields_ = [
		("TrxType", wintypes.BYTE),
		("AmountClear", wintypes.DWORD),    #// сумма операции без учета комиссии / скидки
		("Amount", wintypes.DWORD),         #// сумма операции с учетом комиссии / скидки
		("CardName", c_char * (MAX_NAME+1) ),   #  // название карты (Visa, Maestro и т.д.)
		("CardType", wintypes.BYTE),			#  ///<тип карты. @see CardTypes
		("TrxDate", c_char * (MAX_DATE+1)),		# // дата операции  (ДД.ММ.ГГГГ)
		("TrxTime", c_char * (MAX_TIME+1)),		# // время операции (ЧЧ:ММ:СС)
		("AuthCode", c_char * (MAX_AUTH_CODE+1)), # // код авторизации
		("RRN", c_char * (MAX_RRN+1)),			# //номер ссылки
		("MerchantTSN", wintypes.WORD),			# // номер транзакции в пакете терминала
		("MerchantBatchNum", wintypes.WORD),	# // номер пакета терминала по магн.картам
		("ClientCard", c_char * (MAX_CARD_NUM+1)),	# // номер карты клиента
		("ClientExpiryDate", c_char * (MAX_DATE+1)), # // срок действия карты клиента
		("Hash", c_char * (MAX_HASH)),
		("NextRecId", c_int)
	]

class struct_out2(ctypes.Structure):
	_fields_ = [
		("Count", wintypes.DWORD)
	]

class struct_out3(ctypes.Structure):
	_fields_ = [
		("Buffer", POINTER(EnumStruct))
	]

class struct_out4(ctypes.Structure):
	_fields_ = [
		("Size", wintypes.DWORD)
	]

class struct_out5(ctypes.Structure):
	_fields_ = [
		("Buffer", c_void_p)
	]

class struct_out_cl4(ctypes.Structure):
	_fields_ = [
		("AmountClear", wintypes.DWORD),
		("Amount", wintypes.DWORD),
		("CardName", c_char * (MAX_NAME + 1) ),
		("CardType", wintypes.BYTE),
		("TrxDate", c_char * (MAX_DATE + 1)),
		("TrxTime", c_char * (MAX_TIME + 1)),		
		("TermNum", c_char * (MAX_TERM + 1)),
		("MerchNum", c_char * ( MAX_MERCHANT_LN + 1)),
		("AuthCode", c_char * ( MAX_AUTH_CODE + 1)),
		("RRN", c_char * ( MAX_RRN + 1 )),
		("MerchantTSN", wintypes.WORD),
		("MerchantBatchNum", wintypes.WORD),
		("ClientCard", c_char * (MAX_CARD_NUM )),
		("ClientExpiryDate", c_char * ( MAX_DATE + 1))
	]

class struct_out_cl5(ctypes.Structure):
	_fields_ = [
		("CardName", c_char * (MAX_NAME + 1) ),
		("CardType", wintypes.BYTE),
		("TrxDate", c_char * (MAX_DATE + 1)),
		("TrxTime", c_char * (MAX_TIME + 1)),		
		("TermNum", c_char * (MAX_TERM + 1)),
		("ClientCard", c_char * (MAX_CARD_NUM )),
		("ClientExpiryDate", c_char * ( MAX_DATE + 1))
	]

class TPassportData(ctypes.Structure):
	_fields_ = [
		("sFIO", c_char * ( MAX_FIO_N )), #  ///< ФИО
		("sAddr", c_char * 58), # ///< Адрес
		("sRes", c_short ), # ///< Резидент/нерезидент
		("sDocType", c_char * 21), # ///< Тип документа
		("sSer", c_char * 11),  # ///< Серия
		("sNum", c_char * 16),	#	 ///< Номер
		("sIssuer", c_char * 58), #  ///< Кем выдан
		("sWhen", c_char * 13), # ///< Когда выдан
		("sValid", c_char * 13), #  ///< Срок действия
		("sEmit", c_char * 42), # ///< Банк - эмитент карты
		("Agent", c_char * 42) # ///< Банк, выдавший карту
	]

class TGoodsData(ctypes.Structure):
	_fields_ = [
		("Price", wintypes.DWORD), #  ///< Цена за единицу, exp 2
		("Volume", wintypes.DWORD), # Количество exp 3
		("Name", c_char * (MAX_GOODS_NAME + 1) ), # ///<Наименование товара
		("Code", c_char * (MAX_GOODS_CODE + 1)) # Внутренний код учетной системы вызывающей программы
	]

class struct_in_reserved4(ctypes.Structure):
	_fields_ = [
		("size", wintypes.DWORD),
		("Reserved1", c_void_p),
		("RRN", c_char * ( MAX_RRN + 1 )),
		("RequestID", wintypes.DWORD),
		("Currency", wintypes.DWORD),
		("RecvCard", c_char * ( MAX_PAN_N + 1 )),		
		("BinHash", wintypes.BYTE * 20),
		("HashFlags", wintypes.BYTE* 5),
		("PassportData", TPassportData),
		("AuthCode", c_char * ( MAX_AUTH_CODE + 1)),
		("RecvValidDate", c_char* (MAX_CARD_DATE + 1)),
		("Department", wintypes.DWORD),
		("PaymentTag", c_char * (MAX_PAYMENT_TAG + 1)),
		("TagValue", c_char * (MAX_PAYMENT_VALUE + 1)),
		("CashierFIO", c_char * (MAX_FIO_N + 1)),
		("TextMessage", c_char * (MAX_TEXT_MESSAGE + 1)),
		("GoodsData",TGoodsData),
		("ExpectedCard", c_char * (MAX_CARD_NUM + 1)),
		("AmountOther", wintypes.DWORD)
	]

class struct_in_reserved5(ctypes.Structure):
	_fields_ = [
		("size", wintypes.DWORD),
		("bEditMode", wintypes.BYTE ),	
		("TextMessage", c_char * (MAX_TEXT_MESSAGE)),	
		("CashierFIO", c_char * (MAX_FIO_N + 1)),		
		("dwScreenFormFlags",wintypes.BYTE ),
		("ExpectedCard", c_char * (MAX_CARD_NUM + 1)),
		("CardType", wintypes.BYTE)
	]

class struct_out_reserved4(ctypes.Structure):
	_fields_ = [
		("size", wintypes.DWORD),
		("Reserved1", c_void_p),
		("Cert", wintypes.BYTE *128),
		("PassportData", TPassportData),
		("IsOwn", wintypes.BYTE),
		("Currency", wintypes.DWORD),		
		("TrxFlags", wintypes.DWORD),
		("RequestID", wintypes.DWORD),
		("CardEntryMode", c_char),
		("AID", c_char * 33),
		("LltID", wintypes.BYTE),
		("Flags", wintypes.BYTE),
		("RealPan", c_char * (MAX_PAN_N + 1))
	]

class struct_out_reserved5(ctypes.Structure):
	_pack_ = 1
	_fields_ = [
		("size", wintypes.DWORD),
		("Reserved1", c_void_p),
		("Hash", wintypes.BYTE * MAX_HASH),
		("CardData", wintypes.BYTE * (MAX_TRACK2)),
		("Balance", wintypes.DWORD),
		("Currency", wintypes.DWORD),
		("CardLCDataLen", wintypes.DWORD),
		("CardLCData", wintypes.BYTE * (MAX_CARD_LS_DATA)),
		("AuthCode", c_char * (6+1) ),
		("ClientName", c_char * MAX_CLIENT_NAME),
		("IsOwn", wintypes.BYTE),
		("LltID", wintypes.BYTE),
		("Flags", wintypes.BYTE),
		("RealPan", c_char * (MAX_PAN_N +1))
	]

class struct_out_reserved7(ctypes.Structure):
	_fields_ = [
		("size", wintypes.DWORD),					# ///< Размер структуры в байтах = sizeof(struct_out_reserved7)
		("TermNum", c_char * (MAX_TERM+1)),			#  ///< номер терминала
		("MerchNum", c_char * (MAX_MERCHANT_LN+1)),	# ///< номер мерчанта
		("Record", TBatchRecord)					# //< операция из журнала.
	]

class struct_out0(ctypes.Structure):
	_fields_ = [
		("LibVersion", wintypes.DWORD),		
		("Reserved", c_void_p)
	]

class struct_in14(ctypes.Structure):
	_fields_ = [ 
		("dwErrorCode", wintypes.DWORD)		# / ///< Код ошибки
	]

class struct_out14(ctypes.Structure):
	_fields_ = [ 
		("ErrorDescription", c_char * 256)		# ///< Текст ошибки, соответствующий коду в запросе
	]

class InArg(ctypes.Structure):
	_fields_ = [
		("Reserved", c_void_p),
		("in_struct", c_void_p)		
	]

class OutArg(ctypes.Structure):
	_fields_ = [
		("ErrorCode", wintypes.DWORD),
		("Flags", wintypes.DWORD),
		("Reserved", c_void_p),	
		("out_struct", c_void_p)
	]

class SberGate:
	def __init__(self):
		self.comport = self.get_sber_terminal_port_name() 
		self.Save()

		self.dll = ctypes.CDLL('gate.dll')
		self.call_sb_kernel = getattr(self.dll, '_call_sb_kernel', None)
		self.call_sb_kernel.argtypes = [wintypes.DWORD, c_void_p,  c_void_p ]
		
		self.cheque_text = ''		

		inArg = InArg()
		outArg = OutArg()
		in0 = struct_in0()
		out0 = struct_out0()

		in0.AppVersion=KERNEL_MINIMAL_VERSION
		inArg.in_struct= ctypes.cast(pointer(in0), ctypes.c_void_p)
		outArg.out_struct= ctypes.cast(pointer(out0), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_INITIALIZATION, ctypes.byref(inArg), ctypes.byref(outArg))
		if (error == 0):
			print('Библиотка успешно подгружена!')
		else:
			print('Ошибка ' + str(error) )
		#print(ErrorCode)

	def free_library(self, handle):
		kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
		kernel32.FreeLibrary.argtypes = [ctypes.wintypes.HMODULE]
		kernel32.FreeLibrary(handle)

	def __del__(self):
		error = self.call_sb_kernel(KO_FINALIZATION, ctypes.byref(c_void_p(0)), ctypes.byref(c_void_p(0)))
		if error == 0:
			print('Библиотка успешно выгружена!')
		self.free_library(self.dll._handle)
		del self.dll

	def print_attr(self, port, attr):
		print(str(attr) + ' = ' + str(getattr(port, attr)))

	def get_sber_terminal_port_name(self):
		for port in serial.tools.list_ports.comports():
			if 'PAX' in port.manufacturer:
				if 'COM' in port.name.upper():
					return port.name.upper().replace('COM', '')
				else:
					return port.name
		return -1

	def check_execute(f):
		@functools.wraps(f)
		def wrapper(self, *args, **kwargs):
			if self.Created():				
				ret = f(self, *args, **kwargs)				
				return ret
			else:
				print('Что-то не загрузилось!!!')
				return 0
		return wrapper

	def Save(self):
		ini_file = 'pinpad.ini'
		text = ''
		if os.path.exists(ini_file):
			with open(ini_file, 'r') as f:
				text = f.read().split('\n')
			for i, line in enumerate(text):
				if 'ComPort' in line:
					text[i] = 'ComPort='+ str(self.comport)
					with open(ini_file, 'w') as f:
						f.write('\n'.join(text))
					break
	@check_execute
	def TrnStart(self):
		in_arg = InArg()
		out_arg = OutArg()
		m_in = struct_in_cl4()
		m_out = struct_out_cl4()

		inExtra = struct_in_reserved4()

		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(m_in), 0, ctypes.sizeof(m_in))		
		ctypes.memset(ctypes.addressof(inExtra), 0, ctypes.sizeof(inExtra))
		
		in_arg.in_struct = ctypes.cast(pointer(m_in), ctypes.c_void_p)
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(m_out), 0, ctypes.sizeof(m_out))
		out_arg.out_struct = ctypes.cast(pointer(m_out), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_SUSPEND_TRANSACTION, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		return (error == 0 and out_arg.ErrorCode == 0)

	@check_execute
	def TrnCommit(self):
		in_arg = InArg()
		out_arg = OutArg()
		m_in = struct_in_cl4()
		m_out = struct_out_cl4()

		inExtra = struct_in_reserved4()

		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(m_in), 0, ctypes.sizeof(m_in))		
		ctypes.memset(ctypes.addressof(inExtra), 0, ctypes.sizeof(inExtra))
		
		in_arg.in_struct = ctypes.cast(pointer(m_in), ctypes.c_void_p)
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(m_out), 0, ctypes.sizeof(m_out))
		out_arg.out_struct = ctypes.cast(pointer(m_out), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_COMMIT_TRANSACTION, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		return (error == 0 and out_arg.ErrorCode == 0)

	@check_execute
	def TrnRollback(self):
		in_arg = InArg()
		out_arg = OutArg()
		m_in = struct_in_cl4()
		m_out = struct_out_cl4()

		inExtra = struct_in_reserved4()

		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(m_in), 0, ctypes.sizeof(m_in))		
		ctypes.memset(ctypes.addressof(inExtra), 0, ctypes.sizeof(inExtra))
		
		in_arg.in_struct = ctypes.cast(pointer(m_in), ctypes.c_void_p)
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(m_out), 0, ctypes.sizeof(m_out))
		out_arg.out_struct = ctypes.cast(pointer(m_out), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_ROLLBACK_TRANSACTION, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		return (error == 0 and out_arg.ErrorCode == 0)

	def Created(self):
		return self.dll and self.PinPadReady()

	@check_execute
	def Pay(self, PAmount, PPayInfo='', pHash=''):
		Result = False

		in_arg = InArg()
		out_arg = OutArg()
		m_in = struct_in_cl4()
		m_out = struct_out_cl4()
		inExtra = struct_in_reserved4()
		outExtra = struct_out_reserved4()

		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(m_in), 0, ctypes.sizeof(m_in))		
		ctypes.memset(ctypes.addressof(inExtra), 0, ctypes.sizeof(inExtra))
		
		in_arg.in_struct = ctypes.cast(pointer(m_in), ctypes.c_void_p)
		in_arg.Reserved  = ctypes.cast(pointer(inExtra), ctypes.c_void_p)
		inExtra.size = ctypes.sizeof(inExtra)
		
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(m_out), 0, ctypes.sizeof(m_out))
		ctypes.memset(ctypes.addressof(outExtra), 0, ctypes.sizeof(outExtra))
		
		out_arg.out_struct = ctypes.cast(pointer(m_out), ctypes.c_void_p) 
		out_arg.Reserved = ctypes.cast(pointer(outExtra), ctypes.c_void_p)
		outExtra.size = ctypes.sizeof(outExtra)

		inExtra.Department = DEPARTMENT_NOT_SPECIFIED
		m_in.Amount = PAmount

		print(ctypes.sizeof(in_arg))
		#print( )
		error = self.call_sb_kernel(KO_SALE, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p) )
		Result = error == 0
		if Result:
			print('err = ' + str(error))

			TrxInfo = TdisTCPTrxInfo()

			TrxInfo.Id = None
			TrxInfo.SignIsReq = False
			TrxInfo.RRN = m_out.RRN
			TrxInfo.IsSbrf = outExtra.IsOwn
			TrxInfo.CardName = m_out.CardName
			TrxInfo.CardType = m_out.CardType
			TrxInfo.TermNum  = m_out.TermNum
			TrxInfo.AuthCode = m_out.AuthCode
			TrxInfo.MerchTSN = m_out.MerchantTSN
			TrxInfo.MerchBatch = m_out.MerchantBatchNum
			TrxInfo.CardNum = m_out.ClientCard
			TrxInfo.ExpDate = m_out.ClientExpiryDate

			print(TrxInfo)

			print('CARD TYPE = ' + str(m_out.CardType))

			if (out_arg.Flags & F_HAVE_DOCUMENT):
				Result = self.Cheque()
			else:
				self.cheque_text = ''
				Result = False

		return Result

	@check_execute
	def Ret(self, PAmount):
		Result = False

		in_arg = InArg()
		out_arg = OutArg()
		m_in = struct_in_cl4()
		m_out = struct_out_cl4()
		inExtra = struct_in_reserved4()
		outExtra = struct_out_reserved4()

		TrxInfo = TdisTCPTrxInfo()

		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(m_in), 0, ctypes.sizeof(m_in))		
		ctypes.memset(ctypes.addressof(inExtra), 0, ctypes.sizeof(inExtra))
		
		in_arg.in_struct = ctypes.cast(pointer(m_in), ctypes.c_void_p)
		in_arg.Reserved  = ctypes.cast(pointer(inExtra), ctypes.c_void_p)
		inExtra.size = ctypes.sizeof(inExtra)
		
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(m_out), 0, ctypes.sizeof(m_out))
		ctypes.memset(ctypes.addressof(outExtra), 0, ctypes.sizeof(outExtra))
		
		out_arg.out_struct = ctypes.cast(pointer(m_out), ctypes.c_void_p) 
		out_arg.Reserved = ctypes.cast(pointer(outExtra), ctypes.c_void_p)
		outExtra.size = ctypes.sizeof(outExtra)

		inExtra.Department = DEPARTMENT_NOT_SPECIFIED
		m_in.Amount = PAmount
		inExtra.RRN = b'123456789111'
		error = self.call_sb_kernel(KO_REFUND, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		Result = error == 0
		if Result:
			TrxInfo.Id = None
			TrxInfo.SignIsReq = False
			TrxInfo.RRN = m_out.RRN
			TrxInfo.IsSbrf = outExtra.IsOwn
			TrxInfo.CardName = m_out.CardName
			TrxInfo.CardType = m_out.CardType
			TrxInfo.TermNum  = m_out.TermNum
			TrxInfo.AuthCode = m_out.AuthCode
			TrxInfo.MerchTSN = m_out.MerchantTSN
			TrxInfo.MerchBatch = m_out.MerchantBatchNum
			TrxInfo.CardNum = m_out.ClientCard
			TrxInfo.ExpDate = m_out.ClientExpiryDate

			print(TrxInfo)

			if (out_arg.Flags & F_HAVE_DOCUMENT):
				Result = self.Cheque()
			else:
				self.cheque_text = ''
				Result = False

		return Result
	
	def PinPadReady(self):
		in_arg = InArg()
		out_arg = OutArg()

		in13 = struct_in13()
		out13 = struct_out13()
		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(in13), 0, ctypes.sizeof(in_arg))		
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(out13), 0, ctypes.sizeof(in_arg))

		in_arg.in_struct = ctypes.cast(pointer(in13), ctypes.c_void_p) 
		out_arg.in_struct = ctypes.cast(pointer(out13), ctypes.c_void_p) 
		
		error = self.call_sb_kernel(KO_TEST_PINPAD, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		return (error == 0 and out_arg.ErrorCode == 0)

	@check_execute
	def ZReport(self):
		in_arg = InArg()
		out_arg = OutArg()
		
		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))	
		
		error = self.call_sb_kernel(KO_FULL_REPORT, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		return (error == 0 and out_arg.ErrorCode == 0 and (out_arg.Flags & F_HAVE_DOCUMENT) and self.Cheque()  )

	def Cheque(self):
		in_arg = InArg()
		out_arg = OutArg()
		out4 = struct_out4()
		# set input arguments
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		
		# set output arguments
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(out4), 0, ctypes.sizeof(out4))
		out_arg.out_struct = ctypes.cast(pointer(out4), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_SIZE_OF_CHEQUE, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

		#print(out4.Size)
		if (error == 0 and out_arg.ErrorCode == 0 ):
			in_arg = InArg()
			out_arg = OutArg()
			out5 = struct_out5()

			# set input arguments
			ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
			
			# set output arguments
			ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
			ctypes.memset(ctypes.addressof(out5), 0, ctypes.sizeof(out5))
			
			buf = ctypes.create_string_buffer( int(out4.Size) )
			out5.Buffer = ctypes.cast(pointer( buf ), ctypes.c_void_p)		
			
			out_arg.out_struct = ctypes.cast(pointer(out5), ctypes.c_void_p)

			error = self.call_sb_kernel(KO_GET_LAST_CHEQUE, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))

			if (error == 0 and out_arg.ErrorCode == 0 ):
				self.cheque_text = buf.value.decode('windows-1251')
				print(buf.value.decode('windows-1251'))
			else:
				self.cheque_text = ''
		return (error == 0 and out_arg.ErrorCode == 0 )

	@check_execute
	def GetCardHash(self):
		in_arg = InArg()
		out_arg = OutArg()
		m_in = struct_in_cl5()
		m_out = struct_out_cl5()
		m_res = struct_in_reserved5()		
		out_res = struct_out_reserved5()

		# in args
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(m_in), 0, ctypes.sizeof(m_in))		
		ctypes.memset(ctypes.addressof(m_res), 0, ctypes.sizeof(m_res))

		in_arg.in_struct = ctypes.cast(pointer(m_in), ctypes.c_void_p)
		in_arg.Reserved = ctypes.cast(pointer(m_res), ctypes.c_void_p)
		m_res.size = ctypes.sizeof(m_res)

		# out args
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(m_out), 0, ctypes.sizeof(m_out))
		ctypes.memset(ctypes.addressof(out_res), 0, ctypes.sizeof(out_res))
		out_arg.out_struct = ctypes.cast(pointer(m_out), ctypes.c_void_p)
		out_arg.Reserved = ctypes.cast(pointer(out_res), ctypes.c_void_p)
		out_res.size = ctypes.sizeof(out_res)

		error = self.call_sb_kernel(5002, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))
		#error = 1
		if (error == 0 and out_arg.ErrorCode == 0):
			
			#print( bytes(out_res.CardData).decode() )
			card_number = bytes(out_res.CardData).decode()
			if (len(card_number) > 16 ):
				card_number = card_number[:16]
			card_hash = hex_2_ascii(out_res.Hash, ctypes.sizeof(out_res.Hash))

			return 0, card_number, card_hash

		return (error == 0 and out_arg.ErrorCode == 0), '', ''

	@check_execute
	def GetTerminalNumber(self):
		in_arg = InArg()
		out_arg = OutArg()
		out7 = struct_out_reserved7()

		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(out7), 0, ctypes.sizeof(out7))

		out7.size = ctypes.sizeof(out7)
		out_arg.Reserved = ctypes.cast(pointer(out7), ctypes.c_void_p)
		error = self.call_sb_kernel(KO_GET_TERMINAL_AND_MERCHENT_ID, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))
		if (error == 0 and out_arg.ErrorCode == 0):
			print(out7.TermNum)
			print(out7.MerchNum)			
			return 0, out7.TermNum.decode(), out7.MerchNum.decode()
		return (error == 0 and out_arg.ErrorCode == 0), '', ''

	@check_execute
	def getOperations(self):
		in_arg = InArg()
		out_arg = OutArg()
		out2 = struct_out2()
		out3 = struct_out3()
		
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(out2), 0, ctypes.sizeof(out2))
		out_arg.out_struct = ctypes.cast(pointer(out2), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_FUNCTIONS_COUNT, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))
		if (error == 0 and out_arg.ErrorCode == 0):
			ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
			ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
			ctypes.memset(ctypes.addressof(out3), 0, ctypes.sizeof(out3))
			
			out_arg.out_struct = ctypes.cast(pointer(out3), ctypes.c_void_p)
			print('out2.Count = ' + str(out2.Count))
			#buf = EnumStruct()	

			buf = (EnumStruct * int(out2.Count) )()
			pbuf = ctypes.cast(buf, ctypes.POINTER(EnumStruct))
			
			out3.Buffer = pbuf	
			error = self.call_sb_kernel(3, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))
			if error == ERR_OK:  
				for n in range( int(out2.Count ) ):
					print('Function: ' + out3.Buffer[n].Name.decode('windows-1251') + ' Number = ' + str(out3.Buffer[n].FuncID)) 

	@check_execute
	def getErrorDesc(self, Code):
		in_arg = InArg()
		out_arg = OutArg()
		in14 = struct_in14()
		out14 = struct_out14()
		
		ctypes.memset(ctypes.addressof(in_arg), 0, ctypes.sizeof(in_arg))
		ctypes.memset(ctypes.addressof(in14), 0, ctypes.sizeof(in14))
		in_arg.in_struct = ctypes.cast(pointer(in14), ctypes.c_void_p)

		in14.dwErrorCode = wintypes.DWORD(Code)
		
		ctypes.memset(ctypes.addressof(out_arg), 0, ctypes.sizeof(out_arg))
		ctypes.memset(ctypes.addressof(out14), 0, ctypes.sizeof(out14))
		out_arg.out_struct = ctypes.cast(pointer(out14), ctypes.c_void_p)

		error = self.call_sb_kernel(KO_GET_ERROR_TEXT, ctypes.cast(pointer(in_arg), ctypes.c_void_p), ctypes.cast(pointer(out_arg), ctypes.c_void_p))
		if (error == 0 and out_arg.ErrorCode == 0):
			error_text = out14.ErrorDescription.decode('windows-1251')

			data = read_file()
			if str(Code) in data.keys():
				error_text = error_text + data[str(Code)]

			return 0, error_text		

		return (error == 0 and out_arg.ErrorCode == 0), ''


# def write_file(data):
# 	with open('errors.json', 'w', encoding='utf-8') as f:
# 		f.write(json.dumps(data))
# import re

if __name__ == '__main__':	
	# Создаём инстанс для работы с терминалом сбера
	sber = SberGate()
	# Уже можем оплатить что-то
	#print(sber.Pay(7000))
	# Но вначале надо проверить готовность пинпада
	#print(sber.PinPadReady())
	# Сделаем возврат
	#print(sber.Ret(1000))
	# Возникли проблемы смотрим описание ошибки
	#print(sber.getErrorDesc(4113))
	# Если нужно выяснить, что-то по карте
	#error, card_number, card_hash = sber.GetCardHash()
	# Или узнать информацию по терминалу
	#error, TermNum, MerchNum = sber.GetTerminalNumber()
	# Сверим итоги
	#sber.ZReport()
	# Если всё хорошо то вот он чек
	#cheque = sber.cheque_text
